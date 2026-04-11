from datetime import datetime, timedelta, time

from audit.audit_log import AuditLog
from bank.constants import MAX_AMOUNT_PER_OPERATION, PROHIBITED_TIME_START_HOUR, PROHIBITED_TIME_END_HOUR
from bank.client import Client
from transaction.transaction import Transaction
from .constants import LARGE_AMOUNT_COEFFICIENT, FREQUENT_OPERATIONS_COEFFICIENT, NEW_ACCOUNT_COEFFICIENT, NIGHT_OPERATIONS_COEFFICIENT

from .enums import RiskLevel

class RiskAnalyzer:
    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log

    def analyze_transaction(self, transaction: Transaction, client: Client) -> RiskLevel:
        large_amount = round((transaction.amount / MAX_AMOUNT_PER_OPERATION) * LARGE_AMOUNT_COEFFICIENT)

        operations_per_hour_count = self.audit_log.get_operations_per_hour_count(client.client_id)
        frequent_operations = operations_per_hour_count * FREQUENT_OPERATIONS_COEFFICIENT

        new_account = NEW_ACCOUNT_COEFFICIENT if (datetime.now() - transaction.to_account.created_at) < timedelta(hours=24) else 0

        night_operation = NIGHT_OPERATIONS_COEFFICIENT if time(PROHIBITED_TIME_START_HOUR, 0) < datetime.now().time() < time(PROHIBITED_TIME_END_HOUR, 0) else 0

        total = large_amount + frequent_operations + new_account + night_operation

        if total < 20:
            return RiskLevel.LOW
        elif total < 160:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

