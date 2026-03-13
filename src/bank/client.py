from .enums import ClientAccountStatus, FraudType

from datetime import date, datetime

class InvalidPassword(Exception):
    pass

class ClientAccountFrozen(Exception):
    pass

class ClientAccountClosed(Exception):
    pass

MAX_TRY_COUNT = 3

class Contact:
    def __init__(self, contact_type: str, value: str):
        self.contact_type = contact_type
        self.value = value

class Fraud:
    def __init__(self, fraud_type: FraudType):
        self.fraud_type = fraud_type
        self.created_at = datetime.now()

    def __repr__(self):
        return f"Fraud(type={self.fraud_type.value}, time={self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"

class Client:
    def __init__(self, name:str, client_id:str, date_of_birth: date, login:str, password:str, contacts:list[Contact]):
        self.client_id = client_id
        self.name = name
        self.status = ClientAccountStatus.ACTIVE
        self.contacts:list[Contact] = contacts
        self.date_of_birth:date = date_of_birth
        self.login=login
        self.password=password
        self.try_count:int = 0
        self.frauds:list[Fraud] = []

    def close_account(self):
        self.status = ClientAccountStatus.CLOSED

    def freeze_account(self):
        self.status = ClientAccountStatus.FROZEN

    def unfreeze_account(self):
        self.status = ClientAccountStatus.ACTIVE
        self.try_count = 0

    def is_adult(self) -> bool:
        today = date.today()
        age = today.year - self.date_of_birth.year
        # если день рождения ещё не был в этом году, уменьшаем на 1
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age >= 18

    def _check_account_status(self):
        if self.status == ClientAccountStatus.FROZEN:
            raise ClientAccountFrozen
        elif self.status == ClientAccountStatus.CLOSED:
            raise ClientAccountClosed

    def validate_password(self, password:str):
        self._check_account_status()

        if self.password == password:
            self.try_count = 0
            return

        self.try_count += 1

        if self.try_count >= MAX_TRY_COUNT:
            self.freeze_account()

        raise InvalidPassword

    def add_fraud(self, fraud_type: FraudType):
        self.frauds.append(Fraud(fraud_type))
