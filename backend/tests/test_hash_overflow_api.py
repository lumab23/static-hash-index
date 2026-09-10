from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.api.routes import data
from app.core.hash_function import hash_key
from app.core.hash_index import HashIndex
from app.core.index_state import get_current_index, set_current_index
from app.core.overflow import OverflowBlock
from app.core.pages import Page
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_state():
    previous_index = get_current_index()
    previous_pages = data._page_manager
    set_current_index(None)
    yield
    set_current_index(previous_index)
    data._page_manager = previous_pages


def build(words, capacity=1):
    index = HashIndex(capacity, hash_key, OverflowBlock)
    index.build([Page(0, words)])
    set_current_index(index)
    return index


def query(key):
    return client.get('/api/index/hash-overflow', params={'key': key})


def test_requires_built_index():
    assert query('a').status_code == 409
    set_current_index(HashIndex(1, hash_key, OverflowBlock))
    assert query('a').status_code == 409


@pytest.mark.parametrize('key', ['', ' ', '\t\n'])
def test_rejects_blank_key(key):
    build([])
    assert query(key).status_code == 422


def test_requires_key():
    assert client.get('/api/index/hash-overflow').status_code == 422


def test_real_upload_build_and_overflow_query():
    assert client.post('/api/data/load',
                       files={'file': ('words.txt', b'a\ne\ni\n', 'text/plain')},
                       data={'page_size': '1'}).status_code == 200
    assert client.post('/api/index/build', json={'fr': 1}).status_code == 200
    response = query('i')
    assert response.status_code == 200
    assert response.json() == {
        'key': 'i', 'bucket_id': 1, 'bucket_capacity': 1, 'bucket_occupancy': 1,
        'collision_count': 2, 'collision_rate': pytest.approx(200 / 3),
        'overflow_bucket_count': 1, 'overflow_rate': 25.0,
        'overflow_entries': ['e', 'i'],
    }
    assert client.post('/api/search/index', json={'key': 'i'}).json()['found']
    assert client.get('/api/index/buckets/1').json()['total_entries'] == 3
    assert client.get('/api/index/summary').json()['total_indexed'] == 3
    client.post('/api/data/load', files={'file': ('new.txt', b'new', 'text/plain')},
                data={'page_size': '1'})
    assert query('i').status_code == 409


def test_empty_index_and_empty_bucket():
    build([])
    body = query('missing').json()
    assert body['bucket_occupancy'] == 0
    assert body['collision_count'] == body['overflow_bucket_count'] == 0
    assert body['collision_rate'] == body['overflow_rate'] == 0
    assert body['overflow_entries'] == []
    build(['a', 'e', 'i'])
    body = query('b').json()
    assert body['bucket_occupancy'] == 0
    assert body['overflow_entries'] == []
    assert body['collision_count'] == 2  # Métrica global, não do bucket consultado.


def test_filling_primary_area_is_not_a_collision():
    index = build(['a', 'c'], capacity=2)
    body = query('a').json()
    assert body['bucket_occupancy'] == 2
    assert body['collision_count'] == body['overflow_bucket_count'] == 0
    assert index.collision_count == 0


def test_counts_buckets_not_blocks_and_resets_on_rebuild():
    # NR=6, FR=1, NB=7: três entradas em cada um de dois buckets.
    index = build(['a', 'h', 'o', 'b', 'i', 'p'])
    assert index.collision_count == 4
    assert index.overflow_bucket_count == 2
    body = query('a').json()
    assert body['overflow_entries'] == ['h', 'o']
    assert body['collision_rate'] == pytest.approx(400 / 6)
    assert body['overflow_rate'] == pytest.approx(200 / 7)
    index.build([Page(0, ['a'])])
    assert index.collision_count == index.overflow_bucket_count == 0
    assert query('a').json()['overflow_entries'] == []


def test_query_preserves_exact_key_and_does_not_mutate_index():
    index = build([' Á &+? ', ' Á &+? ', ' Á &+? '])
    before = deepcopy(index.hash_overflow_details(' Á &+? '))
    for _ in range(2):
        response = query(' Á &+? ')
        assert response.status_code == 200
        assert response.json() == before
    assert query('missing').status_code == 200
    assert index.hash_overflow_details(' Á &+? ') == before
    assert index.total_indexed == 3


def test_core_requires_built_index_and_valid_key():
    index = HashIndex(1, hash_key, OverflowBlock)
    with pytest.raises(RuntimeError):
        index.hash_overflow_details('a')
    index.build([])
    with pytest.raises(ValueError):
        index.hash_overflow_details(' ')
    with pytest.raises(TypeError):
        index.hash_overflow_details(None)
