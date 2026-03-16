from __future__ import annotations

from .transaction_queue import TransactionQueue, QueueIsEmpty
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bank.bank import Bank

DEFAULT_RETRY_COUNT = 0

class TransactionProcessor:
    def __init__(self, bank: Bank, queue: TransactionQueue, retry_count: int = DEFAULT_RETRY_COUNT):
        self.bank = bank
        self.queue = queue
        self.retry_count = retry_count

    def process(self):
        transaction=None
        for i in range(self.retry_count + 1):
            try:
                transaction = self.queue.dequeue()
                break
            except QueueIsEmpty:
                continue

        if transaction is None:
            raise QueueIsEmpty

        transaction.execute(self.bank)
