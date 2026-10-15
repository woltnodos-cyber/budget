from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class BudgetExceededError(Exception):
    pass


class InvalidTransactionDataError(Exception):
    pass


@dataclass(frozen=True)
class Category:
    id: int
    name: str
    budget_limit: float


@dataclass(frozen=True)
class Transaction:
    trans_id: int
    category_name: str
    amount: float
    description: str
    date_str: str


class ExpenseReport:
    def __init__(self, transactions: Iterable[Transaction]) -> None:
        self._transactions = list(transactions)

    @property
    def total_spent(self) -> float:
        return round(sum(item.amount for item in self._transactions), 2)

    @property
    def transaction_count(self) -> int:
        return len(self._transactions)