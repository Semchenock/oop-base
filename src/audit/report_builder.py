from __future__ import annotations

from matplotlib.figure import Figure

from .enums import RiskLevel
from .transaction_log import TransactionLog
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

    def build_clients_report(self) -> pd.DataFrame:
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
                    table_key = f"risk_level_{r_key.value}"
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

    def build_transactions_report(self) -> pd.DataFrame:
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
                    "risk": getattr(log_data.risk, "value", None),
                    "reject_reason": log_data.reject_reason
                }
                for log_data in data
            ]
        )

    def build_accounts_report(self) -> pd.DataFrame:

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

    def _get_valid_client_transactions(self, client_id) -> list[TransactionLog]:
        client_transactions = self.bank.audit_log.get_client_transactions(client_id)
        valid_transactions = [t for t in client_transactions if t.status == TransactionStatus.EXECUTED and t.executed_at is not None]
        valid_transactions.sort(key=lambda x: x.executed_at)
        if len(valid_transactions) == 0:
            raise TransactionsNotFoundError

        return valid_transactions

    def plot_client_transactions_report(self, client_id) -> Figure:
        valid_transactions = self._get_valid_client_transactions(client_id)

        transactions_by_accounts = {}

        for t in valid_transactions:
            account_id = t.account_id
            transactions_by_accounts.setdefault(account_id, []).append(t)

        points_by_account = {}

        for account_id, transactions in transactions_by_accounts.items():
            account = self.bank.get_account(account_id)
            start_point_amount = account.balance - sum((t.get_signed_amount() for t in transactions))
            points_by_account[account_id] = [{
                "date": transactions[0].executed_at,
                "amount": start_point_amount,
            }]

            points = points_by_account[account_id]

            for t in transactions:
                prev_point = points[-1]
                prev_amount = prev_point["amount"]
                new_amount = prev_amount + (t.get_signed_amount())
                points.append({"date": t.executed_at, "amount": new_amount})

        fig, ax = plt.subplots()

        for account_id, points in points_by_account.items():
            df = pd.DataFrame(
                [
                    {
                        "date": point.get("date"),
                        "amount": point.get("amount"),
                    }
                    for point in points
                ]
            )

            ax.plot(df["date"], df["amount"], label=f"Account {account_id}")

        ax.legend()
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        ax.set_title("Client Balance Over Time")

        return fig

    def plot_client_income_expenses_report(self, client_id) -> Figure:
        valid_transactions = self._get_valid_client_transactions(client_id)
        signed_amount = [t.get_signed_amount() for t in valid_transactions]
        income = sum(amount for amount in signed_amount if amount > 0)
        expenses = -sum(amount for amount in signed_amount if amount < 0)

        fig, ax = plt.subplots()

        ax.bar(["Income", "Expenses"], [income, expenses])
        ax.set_title("Income vs Expenses")

        return fig

    def plot_client_accounts_balance_report(self, client_id) -> Figure:
        client_accounts = self.bank.search_accounts(client_id=client_id)

        data = list(map(lambda acc: {
            "account_id": acc.id,
            "balance": acc.balance
        }, client_accounts))

        df = pd.DataFrame(data)

        df = df[df["balance"] > 0]

        fig, ax = plt.subplots()
        ax.pie(
            df["balance"],
            labels=df["account_id"],
            autopct="%1.1f%%"
        )
        ax.set_title("Accounts Balance Distribution")

        return fig

    def save_charts(self, client_id, path: str) -> None:
        charts = {
            "balance": self.plot_client_transactions_report(client_id),
            "income_expenses": self.plot_client_income_expenses_report(client_id),
            "accounts_distribution": self.plot_client_accounts_balance_report(client_id),
        }

        self.plot_client_transactions_report(client_id).show()

        for name, fig in charts.items():
            fig.savefig(f"{path}_{name}.png")
            plt.close(fig)

    def export_to_json(self, df: pd.DataFrame, path: str):
        df.to_json(f"{path}.json", index=False)

    def export_to_csv(self, df: pd.DataFrame, path: str):
        df.to_csv(f"{path}.csv", index=False)

    def export_to_txt(self, df: pd.DataFrame, title:str, path: str):
        lines = [
            f"=== {title} ===",
            "",
            df.to_string(index=False)
        ]

        with open(f"{path}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


