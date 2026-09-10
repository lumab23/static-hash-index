from collections.abc import Callable
from time import perf_counter

from app.core.bucket import Bucket, IndexEntry, Overflow
from app.core.pages import Page


def calculate_bucket_count(total_records: int, bucket_capacity: int) -> int:
    """Calcula NB como o menor inteiro estritamente maior que NR / FR."""
    if isinstance(total_records, bool) or not isinstance(total_records, int):
        raise TypeError("O total de registros deve ser um inteiro.")
    if isinstance(bucket_capacity, bool) or not isinstance(bucket_capacity, int):
        raise TypeError("A capacidade do bucket deve ser um inteiro.")

    if total_records < 0:
        raise ValueError("O total de registros deve ser maior ou igual a zero.")
    if bucket_capacity <= 0:
        raise ValueError("A capacidade do bucket deve ser maior que zero.")

    return (total_records // bucket_capacity) + 1


class HashIndex:
    def __init__(
        self,
        bucket_capacity: int,
        hash_function: Callable[[str, int], int],
        overflow_factory: Callable[[int], Overflow],
    ) -> None:
        calculate_bucket_count(0, bucket_capacity)
        if not callable(hash_function):
            raise TypeError("A função hash deve ser chamável.")
        if not callable(overflow_factory):
            raise TypeError("A fábrica de overflow deve ser chamável.")

        self.bucket_capacity = bucket_capacity
        self.nb = 0
        self.buckets: list[Bucket] = []
        self.total_indexed = 0
        self.collision_count = 0
        self.overflow_bucket_count = 0
        self.build_time = 0.0
        self._hash_function = hash_function
        self._overflow_factory = overflow_factory

    def build(self, pages: list[Page]) -> None:
        started_at = perf_counter()
        total_records = sum(len(page.records) for page in pages)
        nb = calculate_bucket_count(total_records, self.bucket_capacity)
        buckets = [
            Bucket(bucket_id, self.bucket_capacity, self._overflow_factory)
            for bucket_id in range(nb)
        ]
        total_indexed = 0
        collision_count = 0
        overflow_bucket_count = 0

        for page in pages:
            for key in page.records:
                entry = IndexEntry(key=key, page_id=page.id)
                bucket_id = self._bucket_id_for(key, nb)
                bucket = buckets[bucket_id]
                if bucket.is_full():
                    collision_count += 1
                    if bucket.overflow is None:
                        overflow_bucket_count += 1
                bucket.add(entry)
                total_indexed += 1

        build_time = perf_counter() - started_at
        self.nb = nb
        self.buckets = buckets
        self.total_indexed = total_indexed
        self.collision_count = collision_count
        self.overflow_bucket_count = overflow_bucket_count
        self.build_time = build_time

    def hash_overflow_details(self, key: str) -> dict[str, object]:
        """Consulta o bucket da chave e as taxas globais em porcentagem."""
        bucket = self.get_bucket(self.bucket_id_for(key))
        overflow_entries = []
        block = bucket.overflow
        while block is not None:
            overflow_entries.extend(entry.key for entry in block.entries)
            block = block.next
        return {
            "key": key,
            "bucket_id": bucket.id,
            "bucket_capacity": bucket.capacity,
            "bucket_occupancy": len(bucket.entries),
            "collision_count": self.collision_count,
            "collision_rate": (
                self.collision_count / self.total_indexed * 100
                if self.total_indexed else 0.0
            ),
            "overflow_bucket_count": self.overflow_bucket_count,
            "overflow_rate": self.overflow_bucket_count / self.nb * 100,
            "overflow_entries": overflow_entries,
        }

    def bucket_id_for(self, key: str) -> int:
        self._require_built()
        return self._bucket_id_for(key, self.nb)

    def get_bucket(self, bucket_id: int) -> Bucket:
        self._require_built()
        self._validate_bucket_id(bucket_id, self.nb)
        return self.buckets[bucket_id]

    def _require_built(self) -> None:
        if self.nb == 0:
            raise RuntimeError("O índice ainda não foi construído.")

    def _bucket_id_for(self, key: str, nb: int) -> int:
        if not isinstance(key, str):
            raise TypeError("A chave deve ser uma string.")
        if not key.strip():
            raise ValueError("A chave não pode estar vazia ou conter apenas espaços.")
        bucket_id = self._hash_function(key, nb)
        self._validate_bucket_id(bucket_id, nb)
        return bucket_id

    @staticmethod
    def _validate_bucket_id(bucket_id: int, nb: int) -> None:
        if isinstance(bucket_id, bool) or not isinstance(bucket_id, int):
            raise TypeError("O identificador do bucket deve ser um inteiro.")
        if bucket_id < 0 or bucket_id >= nb:
            raise ValueError("O identificador do bucket deve estar entre zero e NB - 1.")
