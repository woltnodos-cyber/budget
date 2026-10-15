from __future__ import annotations

import json
from collections import deque
from typing import Deque, Iterable, Set

from generator import DataGeneratorStorage
from model import (
    BudgetExceededError,
    Category,
    ExpenseReport,
    InvalidTransactionDataError,
    Transaction,
)


class BaseReportExporter:

    def export(self, report: ExpenseReport) -> str:
        raise NotImplementedError()


class ConsoleReportExporter(BaseReportExporter):

    def export(self, report: ExpenseReport) -> str:
        lines = [
            "===== Отчёт по расходам =====",
            f"Всего потрачено: {report.total_spent:.2f}",
            f"Количество транзакций: {report.transaction_count}",
            "-----------------------------",
        ]
        return "\n".join(lines)


class JsonReportExporter(BaseReportExporter):

    def export(self, report: ExpenseReport) -> str:
        payload = {
            "total_spent": report.total_spent,
            "transaction_count": report.transaction_count,
            "transactions": [
                {
                    "trans_id": item.trans_id,
                    "category_name": item.category_name,
                    "amount": item.amount,
                    "description": item.description,
                    "date_str": item.date_str,
                }
                for item in report._transactions
            ],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)


class BudgetTracker:

    def __init__(self) -> None:
        self.categories: dict[str, Category] = {}
        self.transactions: list[Transaction] = []
        self.tags: Set[str] = set()
        self.last_operations: Deque[str] = deque(maxlen=5)

    def add_category(self, category: Category) -> None:
        self.categories[category.name.strip().lower()] = category

    def load_categories_from_csv(self, file_path: str) -> None:
        for row in DataGeneratorStorage.read_csv_generator(file_path):
            category = Category(
                id=int(row["id"]),
                name=row["name"].strip(),
                budget_limit=float(row["budget_limit"]),
            )
            self.add_category(category)

    def add_transaction(self, transaction: Transaction) -> None:
        if not transaction.description.strip() or transaction.amount <= 0:
            raise InvalidTransactionDataError("Описание и сумма транзакции указаны неверно.")

        key = transaction.category_name.strip().lower()
        if key not in self.categories:
            raise InvalidTransactionDataError(f"Категория '{transaction.category_name}' не найдена.")

        category = self.categories[key]
        spent_in_category = sum(
            item.amount for item in self.transactions if item.category_name.lower() == key
        )

        if spent_in_category + transaction.amount > category.budget_limit:
            raise BudgetExceededError(
                f"Бюджет категории '{category.name}' превышен: "
                f"{spent_in_category + transaction.amount:.2f} > {category.budget_limit:.2f}"
            )

        self.transactions.append(transaction)
        self.tags.update(self.extract_tags(transaction.description))
        self.last_operations.append(
            f"{transaction.date_str} | {transaction.category_name} | {transaction.amount:.2f}"
        )

    @staticmethod
    def extract_tags(description: str) -> set[str]:
        words = description.split()
        tags = {word.lower() for word in words if word.startswith("#")}
        return tags

    def get_report(self) -> ExpenseReport:
        return ExpenseReport(self.transactions)

    def custom_search_by_description(self, keyword: str) -> list[Transaction]:
        target = keyword.strip().lower()
        if not target:
            return []

        matches: list[Transaction] = []
        for transaction in self.transactions:
            if target in transaction.description.lower():
                matches.append(transaction)
        return matches

    def custom_sort_by_amount(self, transactions: Iterable[Transaction] | None = None) -> list[Transaction]:
        items = list(transactions) if transactions is not None else list(self.transactions)
        if len(items) <= 1:
            return items

        pivot = items[len(items) // 2].amount
        left = [item for item in items if item.amount < pivot]
        middle = [item for item in items if item.amount == pivot]
        right = [item for item in items if item.amount > pivot]

        return self.custom_sort_by_amount(left) + middle + self.custom_sort_by_amount(right)

    def export_report(self, exporter: BaseReportExporter) -> str:
        return exporter.export(self.get_report())