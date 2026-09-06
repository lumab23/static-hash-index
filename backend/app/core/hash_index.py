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
