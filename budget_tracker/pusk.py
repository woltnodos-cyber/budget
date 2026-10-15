from __future__ import annotations

import logging
import os
import sys
from datetime import datetime

from algorithm import BudgetTracker, ConsoleReportExporter
from generator import DataGeneratorStorage
from model import BudgetExceededError, InvalidTransactionDataError, Transaction


logging.basicConfig(
    filename="budget_tracker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def print_menu() -> None:
    print("\n=== Система учёта расходов ===")
    print("1. Добавить расход")
    print("2. Показать сводный отчёт")
    print("3. Поиск по описанию")
    print("4. Сортировка расходов по сумме")
    print("5. Сохранить отчёт в JSON")
    print("0. Выход")


def input_transaction_data() -> Transaction:
    category_name = input("Введите категорию (например, Food): ").strip()
    amount = float(input("Введите сумму расхода: ").strip())
    description = input("Введите описание: ").strip()
    date_value = input("Введите дату (YYYY-MM-DD, пусто = сегодня): ").strip()

    if not date_value:
        date_value = datetime.now().strftime("%Y-%m-%d")

    return Transaction(
        trans_id=int(datetime.now().timestamp() * 1000),
        category_name=category_name,
        amount=amount,
        description=description,
        date_str=date_value,
    )


def main() -> None:
    tracker = BudgetTracker()
    csv_path = resource_path("categories.csv")

    try:
        tracker.load_categories_from_csv(csv_path)
        logging.info("Категории успешно загружены из %s", csv_path)
        print("Категории загружены.")
    except FileNotFoundError:
        logging.error("Файл categories.csv не найден по пути: %s", csv_path)
        print(f"Ошибка: файл categories.csv не найден по пути: {csv_path}")
        return
    except Exception as exc:
        logging.exception("Ошибка загрузки категорий: %s", exc)
        print(f"Ошибка при загрузке категорий: {exc}")
        return

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                transaction = input_transaction_data()
                tracker.add_transaction(transaction)
                logging.info("Добавлена транзакция: %s", transaction)
                print("Транзакция добавлена успешно.")

            elif choice == "2":
                report_text = tracker.export_report(ConsoleReportExporter())
                print(report_text)
                logging.info("Сформирован отчёт в консоль.")

            elif choice == "3":
                keyword = input("Введите текст для поиска: ").strip()
                matches = tracker.custom_search_by_description(keyword)
                if not matches:
                    print("Совпадений не найдено.")
                else:
                    print("Найденные транзакции:")
                    for item in matches:
                        print(f"- {item.date_str} | {item.category_name} | {item.amount:.2f} | {item.description}")
                logging.info("Поиск по описанию выполнен для запроса '%s'", keyword)

            elif choice == "4":
                sorted_transactions = tracker.custom_sort_by_amount()
                print("Транзакции отсортированы по сумме:")
                for item in sorted_transactions:
                    print(f"- {item.category_name}: {item.amount:.2f} ({item.description})")
                logging.info("Сортировка по сумме завершена.")

            elif choice == "5":
                report_data = {
                    "total_spent": tracker.get_report().total_spent,
                    "transaction_count": tracker.get_report().transaction_count,
                    "transactions": [
                        {
                            "trans_id": item.trans_id,
                            "category_name": item.category_name,
                            "amount": item.amount,
                            "description": item.description,
                            "date_str": item.date_str,
                        }
                        for item in tracker.transactions
                    ],
                }
                DataGeneratorStorage.save_report("report.json", report_data)
                print("Отчёт сохранён в файл report.json")
                logging.info("Отчёт сохранён в report.json")

            elif choice == "0":
                print("До свидания!")
                logging.info("Пользователь завершил работу с приложением.")
                break

            else:
                print("Некорректный вариант. Попробуйте ещё раз.")

        except (ValueError, InvalidTransactionDataError, BudgetExceededError) as exc:
            logging.error("Бизнес-ошибка: %s", exc)
            print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()