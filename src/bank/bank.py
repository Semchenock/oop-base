import uuid

from account.enums import AccountStatus, AccountCurrency

from typing import Optional
from .client import Client, InvalidPassword, FraudType
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

class Session:
    def __init__(self, client_id: str):
        self.client_id:str = client_id
        self.created_at:datetime = datetime.now()
        self.session_id:str = str(uuid.uuid4())

MAX_SESSIONS_PER_ACCOUNT = 10

MAX_AMOUNT_PER_OPERATION = 10000

PROHIBITED_TIME_START_HOUR = 0
PROHIBITED_TIME_END_HOUR = 5

class Bank:
    def __init__(self):
        self.clients:list[Client] = []
        self.accounts:list[AccountType] = []
        self.clients_accounts_map: dict[str, list[str]] = {}
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
        self.transaction_queue = TransactionQueue()
        self.transaction_processor = TransactionProcessor(self, self.transaction_queue)

    def add_client(self,client:Client):
        self.clients.append(client)

    def open_account(self, client_id:str, account:AccountType):
        self.accounts.append(account)
        self.clients_accounts_map.setdefault(client_id, []).append(account.id)

    def get_account(self, account_id: str) -> AccountType | None:
        return next((a for a in self.accounts if a.id == account_id), None)

    def close_account(self, account_id:str):
        account = self.get_account(account_id=account_id)

        if account is None:
            raise AccountNotFound

        if account.balance != 0:
            raise AccountCantBeClosed

        account.close_account()

    def freeze_account(self, account_id:str):
        account = self.get_account(account_id=account_id)

        if account is None:
            raise AccountNotFound

        account.freeze_account()

    def unfreeze_account(self, account_id:str):
        account = self.get_account(account_id=account_id)

        if account is None:
            raise AccountNotFound

        account.unfreeze_account()

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

            # проверка лимита после добавления
            if len(session_list) > MAX_SESSIONS_PER_ACCOUNT:
                client.add_fraud(FraudType.TOO_MANY_SESSIONS)

            return session.session_id
        except InvalidPassword:
            client.add_fraud(FraudType.LOGIN_FAILED)
            raise



    def get_total_balance(self, client_id: str) -> int:
        accounts = self.search_accounts(client_id=client_id)
        not_closed_accounts = [acc for acc in accounts if acc.status != AccountStatus.CLOSED]
        return sum([acc.balance for acc in not_closed_accounts])

    def get_clients_ranking(self):
        sorted_clients = sorted(self.clients, key=lambda c: self.get_total_balance(c.client_id))
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
        client_account_ids = self.clients_accounts_map.get(client.client_id, [])

        if account_id not in client_account_ids:
            raise AccountNotFound

        return  next((acc for acc in self.accounts if acc.id == account_id), None)

    def withdraw(self, session_id: str, account_id: str, amount: int):
        client = self._get_client_from_session(session_id)
        self._check_fraud(client, amount)
        client_account = self._get_account_for_operation(client, account_id, amount)

        if client_account is None:
            raise AccountNotFound

        client_account.withdraw(amount)

    def deposit(self, session_id: str, account_id: str, amount: int):
        client = self._get_client_from_session(session_id)
        self._check_fraud(client, amount)
        client_account = self._get_account_for_operation(client, account_id, amount)

        if client_account is None:
            raise AccountNotFound

        client_account.deposit(amount)

    def convert_currency(self,amount: int, from_currency: AccountCurrency, to_currency: AccountCurrency) -> int:
        amount_in_main_currency = amount / self.main_currency_course[from_currency]
        amount_in_to_currency = amount_in_main_currency * self.main_currency_course[to_currency]
        return round(amount_in_to_currency)
