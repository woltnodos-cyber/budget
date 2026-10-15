import tkinter as tk
from tkinter import messagebox, ttk
from model import BudgetTracker

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта расходов")
        self.root.geometry("450x450")
        self.root.resizable(False, False)
        
        self.tracker = BudgetTracker()

        # Заголовок
        title_label = tk.Label(root, text="Управление личным бюджетом", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Фрейм для добавления расхода
        frame_add = tk.LabelFrame(root, text=" Добавить расход ", font=("Arial", 10))
        frame_add.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_add, text="Сумма (тенге/руб):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_amount = tk.Entry(frame_add, width=20)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Категория:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.combo_category = ttk.Combobox(frame_add, values=self.tracker.categories, width=18, state="readonly")
        self.combo_category.grid(row=1, column=1, padx=5, pady=5)
        if self.tracker.categories:
            self.combo_category.current(0)

        tk.Label(frame_add, text="Описание:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_desc = tk.Entry(frame_add, width=20)
        self.entry_desc.grid(row=2, column=1, padx=5, pady=5)

        btn_add = tk.Button(frame_add, text="Добавить расход", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=self.add_expense)
        btn_add.grid(row=3, column=0, columnspan=2, pady=10)

        # Фрейм для отчетов и действий
        frame_actions = tk.LabelFrame(root, text=" Действия и отчёты ", font=("Arial", 10))
        frame_actions.pack(fill="x", padx=15, pady=10)

        btn_report = tk.Button(frame_actions, text="Показать сводный отчёт", width=25, command=self.show_report)
        btn_report.pack(pady=5)

        btn_save = tk.Button(frame_actions, text="Сохранить отчёт в JSON", width=25, command=self.save_json)
        btn_save.pack(pady=5)

    def add_expense(self):
        amount_str = self.entry_amount.get().strip()
        category = self.combo_category.get()
        desc = self.entry_desc.get().strip()

        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму!")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return

        self.tracker.add_expense(amount, category, desc)
        messagebox.setItem = messagebox.showinfo("Успех", f"Расход на сумму {amount} добавлен!")
        
        # Очистка полей
        self.entry_amount.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)

    def show_report(self):
        report = self.tracker.get_summary()
        if not report:
            messagebox.showinfo("Отчёт", "Расходов пока нет.")
            return

        report_text = f"Всего расходов: {report['total_expenses']} руб/тенге\n\nПо категориям:\n"
        for cat, amt in report['by_category'].items():
            report_text += f"- {cat}: {amt}\n"

        messagebox.showinfo("Сводный отчёт", report_text)

    def save_json(self):
        self.tracker.save_to_json("budget_report.json")
        messagebox.showinfo("Успех", "Отчёт успешно сохранён в файл budget_report.json!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()
