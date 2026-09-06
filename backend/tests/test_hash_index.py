import pytest

from app.core.hash_index import calculate_bucket_count


@pytest.mark.parametrize(
    "total_records, bucket_capacity, expected",
    [(10, 2, 6), (10, 3, 4), (0, 2, 1), (2, 10, 1)],
)
def test_calculates_bucket_count(
    total_records: int, bucket_capacity: int, expected: int
) -> None:
    assert calculate_bucket_count(total_records, bucket_capacity) == expected


@pytest.mark.parametrize("bucket_capacity", [0, -1])
def test_rejects_non_positive_capacity(bucket_capacity: int) -> None:
    with pytest.raises(ValueError):
        calculate_bucket_count(10, bucket_capacity)


def test_rejects_negative_record_count() -> None:
    with pytest.raises(ValueError):
        calculate_bucket_count(-1, 2)


@pytest.mark.parametrize("total_records", [None, "10", 10.0, True, False])
def test_rejects_invalid_record_count_type(total_records: object) -> None:
    with pytest.raises(TypeError):
        calculate_bucket_count(total_records, 2)


@pytest.mark.parametrize("bucket_capacity", [None, "2", 2.0, True, False])
def test_rejects_invalid_capacity_type(bucket_capacity: object) -> None:
    with pytest.raises(TypeError):
        calculate_bucket_count(10, bucket_capacity)


@pytest.mark.parametrize("total_records", [0, 1, 10, 11, 100])
@pytest.mark.parametrize("bucket_capacity", [1, 2, 3, 10])
def test_bucket_count_is_strictly_greater_than_ratio(
    total_records: int, bucket_capacity: int
) -> None:
    nb = calculate_bucket_count(total_records, bucket_capacity)

    assert nb > total_records / bucket_capacity


def test_handles_large_integers_without_rounding() -> None:
    total_records = 10**30
    bucket_capacity = 3

    nb = calculate_bucket_count(total_records, bucket_capacity)

    assert nb * bucket_capacity > total_records
    assert (nb - 1) * bucket_capacity <= total_records
