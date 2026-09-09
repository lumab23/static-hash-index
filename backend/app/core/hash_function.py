def hash_key(key: str, nb: int) -> int:
    
    if nb <= 0:
        raise ValueError("NB deve ser maior que zero.")

    hash_value = 0

    for char in key:
        hash_value = (hash_value * 31 + ord(char)) % nb

    return hash_value