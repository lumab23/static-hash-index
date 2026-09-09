from app.core.bucket import Bucket, IndexEntry
from app.core.hash_function import hash_key
from app.core.hash_index import HashIndex
from app.core.overflow import OverflowBlock
from app.core.pages import PageManager
from app.core.search import search_by_index


def test_real_hash_distribution_and_page_references() -> None:
    pages = PageManager(["apple", "house", "water", "river", "Água"], 2)
    index = HashIndex(2, hash_key, OverflowBlock)
    index.build(pages.pages)

    assert index.nb == 3
    assert index.total_indexed == 5
    for page in pages.pages:
        for key in page.records:
            bucket_id = hash_key(key, index.nb)
            assert type(bucket_id) is int
            assert 0 <= bucket_id < index.nb
            assert hash_key(key, index.nb) == bucket_id
            assert index.bucket_id_for(key) == bucket_id
            assert index.get_bucket(bucket_id).find(key) == IndexEntry(key, page.id)


def test_real_overflow_search_and_rebuild() -> None:
    # NR = 3 e FR = 1 produzem NB = 4; as três chaves reais vão ao bucket 1.
    pages = PageManager(["a", "e", "i"], 1)
    index = HashIndex(1, hash_key, OverflowBlock)
    index.build(pages.pages)
    assert index.nb == 4
    assert [hash_key(key, index.nb) for key in ["a", "e", "i"]] == [1, 1, 1]

    previous_bucket = None
    for rebuild in range(2):
        if rebuild:
            index.build(pages.pages)
        bucket = index.get_bucket(1)
        assert isinstance(bucket, Bucket)
        assert bucket is not previous_bucket
        assert bucket.entries == [IndexEntry("a", 0)]
        assert bucket.is_full() is True
        first = bucket.overflow
        assert isinstance(first, OverflowBlock)
        assert first.capacity == 1
        assert first.entries == [IndexEntry("e", 1)]
        second = first.next
        assert isinstance(second, OverflowBlock)
        assert second.capacity == 1
        assert second.entries == [IndexEntry("i", 2)]
        assert second.next is None
        assert first.get_all_entries() == [IndexEntry("e", 1), IndexEntry("i", 2)]

        total_stored = 0
        for stored_bucket in index.buckets:
            total_stored += len(stored_bucket.entries)
            block = stored_bucket.overflow
            while block is not None:
                total_stored += len(block.entries)
                block = block.next
        assert total_stored == index.total_indexed == 3

        for key, page_id in [("a", 0), ("e", 1), ("i", 2)]:
            assert bucket.find(key) == IndexEntry(key, page_id)
            result = search_by_index(key, index, pages)
            assert result.found is True
            assert result.bucket_id == 1
            assert result.page_id == page_id
            assert result.pages_read == 1
            assert result.trace[-1] == "Chave confirmada"

        # "m" também chega ao bucket 1, obrigando a busca a percorrer o overflow.
        assert hash_key("m", index.nb) == 1
        missing = search_by_index("m", index, pages)
        assert missing.found is False
        assert missing.page_id is None
        assert missing.pages_read == 0
        previous_bucket = bucket


def test_real_overflow_starts_only_when_primary_bucket_is_full() -> None:
    bucket = Bucket(1, 2, OverflowBlock)
    # Com NB = 4, estas entradas compartilham o destino mesmo antes de lotar.
    assert [hash_key(key, 4) for key in ["a", "e", "i"]] == [1, 1, 1]
    bucket.add(IndexEntry("a", 0))
    assert bucket.is_full() is False
    assert bucket.overflow is None

    bucket.add(IndexEntry("e", 1))
    assert bucket.is_full() is True
    assert bucket.overflow is None

    # Pela regra acadêmica, esta é a primeira inserção em bucket já cheio.
    bucket.add(IndexEntry("i", 2))
    assert bucket.entries == [IndexEntry("a", 0), IndexEntry("e", 1)]
    assert isinstance(bucket.overflow, OverflowBlock)
    assert bucket.overflow.capacity == 2
    assert bucket.overflow.entries == [IndexEntry("i", 2)]
