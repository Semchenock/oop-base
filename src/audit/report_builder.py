from __future__ import annotations

from .enums import RiskLevel, TransactionDirection
from transaction.enums import TransactionStatus
import pandas as pd
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from bank.bank import Bank

class TransactionsNotFoundError(Exception):
    pass

class ReportBuilder:
    def __init__(self, bank: Bank):
        self.bank = bank

    def build_clients_report(self):
        data = [
                {
                    "client_id": c.client_id,
                    "name": c.name,
                    "status": c.status.value,
                    "date_of_birth": c.date_of_birth.strftime("%Y-%m-%d"),
                    "login": c.login,
                    "try_count": c.try_count,
                }
                for c in self.bank.clients
            ]

        for c_data in data:
            client_id = c_data.get("client_id", None)
            if client_id is not None:
                risk = self.bank.audit_log.get_client_risk_profile(client_id)
                for r_key in risk.keys():
                    table_key = f"risk_level_{r_key}"
                    c_data[table_key] = risk[r_key]

        return pd.DataFrame(
            [
                {
                    "client_id": c_data.get("client_id", None),
                    "name": c_data.get("name", None),
                    "status": c_data.get("status", None),
                    "date_of_birth": c_data.get("date_of_birth", None),
                    "login": c_data.get("login", None),
                    "try_count": c_data.get("try_count", None),
                    f"risk_level_{RiskLevel.LOW.value}": c_data.get(f"risk_level_{RiskLevel.LOW.value}", 0),
                    f"risk_level_{RiskLevel.MEDIUM.value}": c_data.get(f"risk_level_{RiskLevel.MEDIUM.value}", 0),
                    f"risk_level_{RiskLevel.HIGH.value}": c_data.get(f"risk_level_{RiskLevel.HIGH.value}", 0),
                }
                for c_data in data
            ]
        )

    def build_transactions_report(self):
        data = self.bank.audit_log.get_all_transaction_logs()

        return pd.DataFrame(
            [
                {
                    "entity": log_data.entity.value,
                    "account_id": log_data.account_id,
                    "client_id": log_data.client_id,
                    "transaction_id": log_data.transaction_id,
                    "created_at": log_data.created_at,
                    "executed_at": log_data.executed_at,
                    "amount": log_data.amount,
                    "currency": log_data.currency.value,
                    "direction": log_data.direction.value,
                    "status": log_data.status.value,
                }
                for log_data in data
            ]
        )

    def build_accounts_report(self):

        return pd.DataFrame(
            [
                {
                    "account_id": acc.id,
                    "type": acc.__class__.__name__,
                    "client_id": acc.client_id,
                    "owner_name": acc.owner_name,
                    "created_at": acc.created_at,
                    "balance": acc.balance,
                    "currency": acc.currency.value,
                    "status": acc.status.value,
                    "fee": getattr(acc, "fee", None),
                    "overdraft_limit": getattr(acc, "overdraft_limit", None),
                    "min_balance": getattr(acc, "min_balance", None),
                    "monthly_interest": getattr(acc, "monthly_interest", None),
                }
                for acc in self.bank.accounts
            ]
        )

    def _get_valid_client_transactions(self, client_id):
        client_transactions = self.bank.audit_log.get_client_transactions(client_id)
        valid_transactions = [t for t in client_transactions if t.status == TransactionStatus.EXECUTED and t.executed_at is not None]
        valid_transactions.sort(key=lambda x: x.executed_at)
        if len(valid_transactions) == 0:
            raise TransactionsNotFoundError

        return valid_transactions

    def build_client_transactions_report(self, client_id, export_path=None):
        valid_transactions = self._get_valid_client_transactions(client_id)

        points: list[dict] = [{
            "date": valid_transactions[0].executed_at,
            "amount": 0,
        }]

        for t in valid_transactions:
            prev_point = points[-1]
            prev_amount = 0 if prev_point is None else prev_point.get("amount", 0)
            new_amount = prev_amount + (t.get_signed_amount())
            points.append({"date": t.executed_at, "amount": new_amount})

        df = pd.DataFrame(
            [
                {
                    "date": point.get("date"),
                    "amount": point.get("amount"),
                }
                for point in points
            ]
        )

        plt.figure()
        plt.plot(df["date"], df["amount"])

        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Client Balance Over Time")

        plt.xticks(rotation=45)
        plt.tight_layout()

        if export_path is not None:
            plt.savefig(export_path)

        plt.show()

    def build_client_income_expenses_report(self, client_id, export_path=None):
        valid_transactions = self._get_valid_client_transactions(client_id)
        signed_amount = [t.get_signed_amount() for t in valid_transactions]
        income = sum(amount for amount in signed_amount if amount > 0)
        expenses = -sum(amount for amount in signed_amount if amount < 0)

        plt.figure()
        plt.bar(["Income", "Expenses"], [income, expenses])
        plt.title("Income vs Expenses")

        if export_path is not None:
            plt.savefig(export_path)

        plt.show()

    def build_client_accounts_balance_report(self, client_id, export_path=None):
        client_accounts = self.bank.search_accounts(client_id=client_id)

        data = list(map(lambda acc: {
            "account_id": acc.id,
            "balance": acc.balance
        }, client_accounts))

        df = pd.DataFrame(data)

        df = df[df["balance"] > 0]

        plt.figure()
        plt.pie(
            df["balance"],
            labels=df["account_id"],
            autopct="%1.1f%%"
        )
        plt.title("Accounts Balance Distribution")

        if export_path is not None:
            plt.savefig(export_path)

        plt.show()

    def export_to_json(self, df: pd.DataFrame, path: str):
        df.to_json(path, index=False)

    def export_to_csv(self, df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)

