from .transaction import Transaction

class TransactionAlreadyInQueue(Exception):
    pass

class TransactionNotFound(Exception):
    pass

class QueueIsEmpty(Exception):
    pass

class TransactionQueue:
    def __init__(self):
        self.transactions: list[Transaction] = []

    def _check_duplicate_id(self, new_transaction: Transaction):
        transaction_with_id = next((t for t in self.transactions if t.transaction_id == new_transaction.transaction_id), None)
        if transaction_with_id:
            raise TransactionAlreadyInQueue


    def enqueue(self, transaction: Transaction):
        self._check_duplicate_id(transaction)
        self.transactions.append(transaction)

    def dequeue(self) -> Transaction:

        self.transactions.sort(key=lambda t: (-t.priority, t.timestamp))

        for i, transaction in enumerate(self.transactions):
            if transaction.can_execute():
                return self.transactions.pop(i)

        raise QueueIsEmpty

    def cancel(self, transaction_id: str):
        for i, transaction in enumerate(self.transactions):
            if transaction.transaction_id == transaction_id:
                transaction.cancel()
                self.transactions.pop(i)
                return

        raise TransactionNotFound


