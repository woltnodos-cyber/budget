import tkinter as tk
from tkinter import messagebox, ttk
from algorithm import BudgetTracker, JsonReportExporter
from model import Transaction, BudgetExceededError, InvalidTransactionDataError

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта расходов")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        self.tracker = BudgetTracker()
        
        # Автоматически загружаем категории из CSV при старте
        try:
            self.tracker.load_categories_from_csv("categories.csv")
        except Exception as e:
            # Если файл не найден локально в корне, пробуем путь внутри пакета
            try:
                self.tracker.load_categories_from_csv("budget_tracker/categories.csv")
            except Exception:
                pass

        # Заголовок
        title_label = tk.Label(root, text="Управление личным бюджетом", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Фрейм для добавления расхода
        frame_add = tk.LabelFrame(root, text=" Добавить расход ", font=("Arial", 10))
        frame_add.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_add, text="ID транзакции:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_id = tk.Entry(frame_add, width=20)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5)
        self.entry_id.insert(0, "1")

        tk.Label(frame_add, text="Сумма:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_amount = tk.Entry(frame_add, width=20)
        self.entry_amount.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Категория:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        # Получаем список названий категорий для выпадающего списка
        category_names = [cat.name for cat in self.tracker.categories.values()]
        if not category_names:
            category_names = ["Еда", "Транспорт", "Развлечения"] # запасной вариант
            
        self.combo_category = ttk.Combobox(frame_add, values=category_names, width=18, state="readonly")
        self.combo_category.grid(row=2, column=1, padx=5, pady=5)
        if category_names:
            self.combo_category.current(0)

        tk.Label(frame_add, text="Описание (#теги):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_desc = tk.Entry(frame_add, width=20)
        self.entry_desc.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Дата (ГГГГ-ММ-ДД):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entry_date = tk.Entry(frame_add, width=20)
        self.entry_date.grid(row=4, column=1, padx=5, pady=5)
        import datetime
        self.entry_date.insert(0, datetime.date.today().isoformat())

        btn_add = tk.Button(frame_add, text="Добавить расход", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=self.add_expense)
        btn_add.grid(row=5, column=0, columnspan=2, pady=10)

        # Фрейм для отчетов и действий
        frame_actions = tk.LabelFrame(root, text=" Действия и отчёты ", font=("Arial", 10))
        frame_actions.pack(fill="x", padx=15, pady=10)

        btn_report = tk.Button(frame_actions, text="Показать сводный отчёт", width=25, command=self.show_report)
        btn_report.pack(pady=5)

        btn_save = tk.Button(frame_actions, text="Сохранить отчёт в JSON", width=25, command=self.save_json)
        btn_save.pack(pady=5)

    def add_expense(self):
        try:
            trans_id = int(self.entry_id.get().strip())
            amount = float(self.entry_amount.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "ID и сумма должны быть числами!")
            return

        category_name = self.combo_category.get()
        description = self.entry_desc.get().strip()
        date_str = self.entry_date.get().strip()

        transaction = Transaction(
            trans_id=trans_id,
            category_name=category_name,
            amount=amount,
            description=description,
            date_str=date_str
        )

        try:
            self.tracker.add_transaction(transaction)
            messagebox.showinfo("Успех", f"Расход на сумму {amount} успешно добавлен!")
            # Увеличиваем ID для удобства следующего ввода
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(trans_id + 1))
            self.entry_amount.delete(0, tk.END)
            self.entry_desc.delete(0, tk.END)
        except (InvalidTransactionDataError, BudgetExceededError) as e:
            messagebox.showerror("Ошибка ограничения бюджета", str(e))

    def show_report(self):
        report = self.tracker.get_report()
        if report.transaction_count == 0:
            messagebox.showinfo("Отчёт", "Расходов пока нет.")
            return

        report_text = f"Всего потрачено: {report.total_spent:.2f}\n" \
                      f"Количество транзакций: {report.transaction_count}\n\n" \
                      f"Последние операции:\n"
        
        for op in list(self.tracker.last_operations):
            report_text += f"- {op}\n"

        messagebox.showinfo("Сводный отчёт", report_text)

    def save_json(self):
        exporter = JsonReportExporter()
        json_data = self.tracker.export_report(exporter)
        
        with open("budget_report.json", "w", encoding="utf-8") as f:
            f.write(json_data)
            
        messagebox.showinfo("Успех", "Отчёт успешно сохранён в файл budget_report.json!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()
