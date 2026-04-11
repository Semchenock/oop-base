import uuid

from account.enums import AccountStatus, AccountCurrency

from typing import Optional

from audit.audit_log import AuditLog
from audit.enums import TransactionEntity, TransactionDirection, AccountActionsEnum, LoginStatus
from audit.report_builder import ReportBuilder
from audit.risk_analyzer import RiskAnalyzer
from audit.transaction_log import TransactionLog
from audit.account_log import AccountLog
from audit.login_log import LoginLog
from transaction.enums import TransactionStatus
from .client import Client, InvalidPassword
from .constants import MAX_SESSIONS_PER_ACCOUNT, PROHIBITED_TIME_START_HOUR, PROHIBITED_TIME_END_HOUR, MAX_AMOUNT_PER_OPERATION
from account.types import AccountType
from datetime import datetime, time

from .enums import FraudType

from transaction.transaction_queue import TransactionQueue
from transaction.transaction_processor import TransactionProcessor

class AccountNotFound(Exception):
    pass

class ClientNotFound(Exception):
    pass

class AccountCantBeClosed(Exception):
    pass

class ProhibitedOperationTime(Exception):
    pass

class ClientIsNotAdult(Exception):
    pass

class DuplicateAccount(Exception):
    pass

class Session:
    def __init__(self, client_id: str):
        self.client_id:str = client_id
        self.created_at:datetime = datetime.now()
        self.session_id:str = str(uuid.uuid4())



class Bank:
    def __init__(self):
        self.clients:list[Client] = []
        self.accounts:list[AccountType] = []
        self.clients_accounts_map: dict[str, list[str]] = {}
        self.accounts_clients_map: dict[str, str] = {}
        self.sessions:list[Session] = []
        self.clients_sessions_map: dict[str, list[str]] = {}
        self.sessions_clients_map: dict[str, str] = {}
        self.main_currency:AccountCurrency = AccountCurrency.USD
        self.main_currency_course: dict[AccountCurrency, float] = {
            AccountCurrency.RUB: 79.91,
            AccountCurrency.USD: 1,
            AccountCurrency.EUR: 0.87,
            AccountCurrency.KZT: 0.0020,
            AccountCurrency.CNY: 0.14,
        }
        self.transaction_queue = TransactionQueue(self)
        self.transaction_processor = TransactionProcessor(self, self.transaction_queue)
        self.audit_log = AuditLog()
        self.risk_analyzer = RiskAnalyzer(self.audit_log)
        self.report_builder = ReportBuilder(self)

    def add_client(self,client:Client):
        if not client.is_adult():
            raise ClientIsNotAdult

        self.clients.append(client)

    def open_account(self, client_id:str, account:AccountType):
        client = self.search_client_by_id(client_id)

        if client is None:
            raise ClientNotFound

        if any(acc.id == account.id for acc in self.accounts):
            raise DuplicateAccount

        account.add_client_id(client_id)
        self.accounts.append(account)
        self.clients_accounts_map.setdefault(client_id, []).append(account.id)
        self.accounts_clients_map[account.id] = client_id
        self.audit_log.add_log(AccountLog(account_id=account.id, action=AccountActionsEnum.CREATE))
        client.add_account_id(account.id)

    def get_account(self, account_id: str) -> AccountType | None:
        return next((a for a in self.accounts if a.id == account_id), None)

    def close_account(self, account_id:str):
        account = self.get_account(account_id=account_id)

        if account is None:
            raise AccountNotFound

        if account.balance != 0:
            raise AccountCantBeClosed

        account.close_account()
        self.audit_log.add_log(AccountLog(account_id=account.id, action=AccountActionsEnum.CLOSE))

    def freeze_account(self, account_id:str):
        account = self.get_account(account_id=account_id)

        if account is None:
            raise AccountNotFound

        account.freeze_account()
        self.audit_log.add_log(AccountLog(account_id=account.id, action=AccountActionsEnum.FREEZE))

    def unfreeze_account(self, account_id:str):
        account = self.get_account(account_id=account_id)

        if account is None:
            raise AccountNotFound

        account.unfreeze_account()
        self.audit_log.add_log(AccountLog(account_id=account.id, action=AccountActionsEnum.UNFREEZE))

    def search_accounts(self, account_id: Optional[str] = None, client_id: Optional[str] = None) -> list[AccountType]:
        """
        Возвращает список аккаунтов по account_id или client_id.
        Если ничего не передано, возвращает [].
        """
        if account_id is None and client_id is None:
            return []

        results = self.accounts

        if account_id is not None:
            # ищем конкретный аккаунт по ID
            results = [acc for acc in results if acc.id == account_id]

        if client_id is not None:
            # фильтруем аккаунты, принадлежащие клиенту
            account_ids = self.clients_accounts_map.get(client_id, [])
            results = [acc for acc in results if acc.id in account_ids]

        return results

    def search_client_by_login(self, client_login: str)-> Client | None:
        return next((c for c in self.clients if c.login == client_login), None)

    def search_client_by_id(self, client_id: str)-> Client | None:
        return next((c for c in self.clients if c.client_id == client_id), None)

    def search_client_by_session_id(self, session_id: str) -> Client | None:
        client_id = self.sessions_clients_map.get(session_id, None)
        if client_id is None:
            return None

        return self.search_client_by_id(client_id)

    def search_client_by_account_id(self, account_id:str) -> Client | None:
        client_id = self.accounts_clients_map.get(account_id, None)
        if client_id is None:
            return None

        return self.search_client_by_id(client_id)

    def authenticate_client(self, client_login: str, client_password: str) -> str:
        client = self.search_client_by_login(client_login)

        if client is None:
            raise ClientNotFound

        try:
            client.validate_password(client_password)
            session_list = self.clients_sessions_map.setdefault(client.client_id, [])

            session = Session(client_id=client.client_id)
            session_list.append(session.session_id)
            self.sessions.append(session)
            self.sessions_clients_map[session.session_id] = session.client_id

            sessions_count = len(session_list)

            self.audit_log.add_log(
                LoginLog(status=LoginStatus.SUCCESS, client_id=client.client_id, session_id=session.session_id, sessions_count=sessions_count))

            if sessions_count > MAX_SESSIONS_PER_ACCOUNT:
                client.add_fraud(FraudType.TOO_MANY_SESSIONS)

            return session.session_id
        except InvalidPassword:
            client.add_fraud(FraudType.LOGIN_FAILED)
            self.audit_log.add_log(LoginLog(status=LoginStatus.FAILED, client_id=client.client_id, try_count=client.try_count))
            raise

    def logout_client(self, client_id: str):
        session_list = self.clients_sessions_map.get(client_id, None)
        if session_list is None:
            return

        ids_set = set(session_list)

        self.sessions[:] = [s for s in self.sessions if s.session_id not in ids_set]
        del self.clients_sessions_map[client_id]

        for session_id in session_list:
            del self.sessions_clients_map[session_id]


    def get_total_balance(self, client_id: str) -> int:
        accounts = self.search_accounts(client_id=client_id)
        not_closed_accounts = [acc for acc in accounts if acc.status != AccountStatus.CLOSED]
        return sum([self.convert_currency(acc.balance, acc.currency, self.main_currency) for acc in not_closed_accounts])

    def get_clients_ranking(self):
        sorted_clients = sorted(self.clients, key=lambda c: self.get_total_balance(c.client_id), reverse=True)
        return sorted_clients

    def _is_operations_allowed(self):
        now = datetime.now().time()

        if time(PROHIBITED_TIME_START_HOUR, 0) < now < time(PROHIBITED_TIME_END_HOUR, 0):
            raise ProhibitedOperationTime

    def _get_client_from_session(self, session_id: str) -> Client:
        client = self.search_client_by_session_id(session_id)

        if client is None:
            raise ClientNotFound

        return client

    def _check_fraud(self, client: Client, amount: int):
        try:
            self._is_operations_allowed()
        except ProhibitedOperationTime:
            client.add_fraud(FraudType.NIGHT_OPERATION)
            raise

        if amount > MAX_AMOUNT_PER_OPERATION:
            client.add_fraud(FraudType.BIG_TRANSACTION)

    def _get_account_for_operation(self, client: Client, account_id: str, amount) -> AccountType | None:
        print(self.clients_accounts_map, client.client_id)
        client_account_ids = self.clients_accounts_map.get(client.client_id, [])

        print(account_id, client_account_ids)
        if account_id not in client_account_ids:
            raise AccountNotFound

        return  next((acc for acc in self.accounts if acc.id == account_id), None)

    def _create_transaction_log(self, is_withdraw: bool, account: AccountType, status: TransactionStatus, amount: int, reject_reason: Optional[str] = None):
        transaction_id=str(uuid.uuid4())

        common_args={
            'transaction_id' : transaction_id,
            'executed_at': datetime.now(),
            'created_at': datetime.now(),
            'amount': amount,
            'currency': account.currency,
            'status': status,
            'reject_reason': reject_reason,
        }

        self.audit_log.add_log(TransactionLog(
                entity = TransactionEntity.CLIENT if is_withdraw else TransactionEntity.EXTERNAL,
                direction=TransactionDirection.DEBIT,
                account_id=account.id if is_withdraw else None,
                client_id=account.client_id if is_withdraw else None,
                **common_args
            ))
        self.audit_log.add_log(TransactionLog(
                entity=TransactionEntity.EXTERNAL if is_withdraw else TransactionEntity.CLIENT,
                direction=TransactionDirection.CREDIT,
                account_id=None if is_withdraw else account.id,
                client_id=None if is_withdraw else account.client_id,
                **common_args
            ))


    def withdraw(self, session_id: str, account_id: str, amount: int):
        client = self._get_client_from_session(session_id)
        self._check_fraud(client, amount)
        client_account = self._get_account_for_operation(client, account_id, amount)

        if client_account is None:
            raise AccountNotFound

        log_args = {
            'is_withdraw': True,
            'account': client_account,
            'amount': amount
        }

        try:
            client_account.withdraw(amount)
            self._create_transaction_log(status = TransactionStatus.EXECUTED, **log_args)
        except Exception as e:
            self._create_transaction_log(status=TransactionStatus.REJECTED, reject_reason=self.audit_log.get_exception_message(e), **log_args)
            raise e

    def deposit(self, session_id: str, account_id: str, amount: int):
        client = self._get_client_from_session(session_id)
        self._check_fraud(client, amount)
        print(client, account_id, amount)
        client_account = self._get_account_for_operation(client, account_id, amount)

        if client_account is None:
            raise AccountNotFound

        log_args = {
            'is_withdraw': False,
            'account': client_account,
            'amount': amount
        }

        try:
            client_account.deposit(amount)
            self._create_transaction_log(status = TransactionStatus.EXECUTED, **log_args)
        except Exception as e:
            self._create_transaction_log(status=TransactionStatus.REJECTED, reject_reason=self.audit_log.get_exception_message(e), **log_args)
            raise e

    def convert_currency(self, amount: int, from_currency: AccountCurrency, to_currency: AccountCurrency) -> int:
        amount_in_to_currency = amount * self.main_currency_course[from_currency] / self.main_currency_course[to_currency]
        return round(amount_in_to_currency)
