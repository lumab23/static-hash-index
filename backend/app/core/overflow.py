class OverflowBlock:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")

        self.capacity = capacity
        self.entries = []
        self.next = None

    def is_full(self) -> bool:
        return len(self.entries) >= self.capacity

    def add(self, entry):
        if not self.is_full():
            self.entries.append(entry)
            return

        if self.next is None:
            self.next = OverflowBlock(self.capacity)

        self.next.add(entry)

    def get_all_entries(self):
        entries = list(self.entries)

        if self.next is not None:
            entries.extend(self.next.get_all_entries())

        return entries