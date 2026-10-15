import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
import calendar
from algorithm import BudgetTracker, JsonReportExporter
from model import Transaction, BudgetExceededError, InvalidTransactionDataError

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта расходов — Астана Edition")
        self.root.geometry("800x680")
        self.root.resizable(False, False)
        
        self.tracker = BudgetTracker()
        
        try:
            self.tracker.load_categories_from_csv("categories.csv")
        except Exception:
            try:
                self.tracker.load_categories_from_csv("budget_tracker/categories.csv")
            except Exception:
                pass

        self.total_budget_limit = sum(cat.budget_limit for cat in self.tracker.categories.values())
        if self.total_budget_limit == 0:
            self.total_budget_limit = 300000.0

        title_label = tk.Label(root, text="Управление личным бюджетом", font=("Arial", 12, "bold"), fg="#2c3e50")
        title_label.pack(pady=4)

        budget_frame = tk.Frame(root, bg="#e8f8f5", bd=2, relief="groove")
        budget_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(budget_frame, text="Остаток бюджета на месяц:", font=("Arial", 10), bg="#e8f8f5", fg="#7f8c8d").pack(pady=2)
        
        budget_display_frame = tk.Frame(budget_frame, bg="#e8f8f5")
        budget_display_frame.pack(pady=2)

        self.lbl_remaining = tk.Label(budget_display_frame, text=f"{self.total_budget_limit:,.2f} ₸", font=("Arial", 22, "bold"), bg="#e8f8f5", fg="#27ae60")
        self.lbl_remaining.pack(side="left", padx=5)

        btn_edit_budget = tk.Button(budget_display_frame, text="✏️", font=("Arial", 12), command=self.edit_budget, bg="#ffffff", relief="raised")
        btn_edit_budget.pack(side="left", padx=5)

        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_column = tk.Frame(main_frame)
        left_column.pack(side="left", fill="y", padx=5)

        frame_add = tk.LabelFrame(left_column, text=" Добавить расход ", font=("Arial", 10, "bold"))
        frame_add.pack(fill="x", padx=5, pady=5)

        tk.Label(frame_add, text="ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.entry_id = tk.Entry(frame_add, width=18)
        self.entry_id.grid(row=0, column=1, padx=5, pady=4)
        self.entry_id.insert(0, "1")

        tk.Label(frame_add, text="Сумма (₸):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.entry_amount = tk.Entry(frame_add, width=18)
        self.entry_amount.grid(row=1, column=1, padx=5, pady=4)

        tk.Label(frame_add, text="Категория:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        category_names = [cat.name for cat in self.tracker.categories.values()]
        if not category_names:
            category_names = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Коммунальные услуги"]
            
        self.combo_category = ttk.Combobox(frame_add, values=category_names, width=16, state="readonly")
        self.combo_category.grid(row=2, column=1, padx=5, pady=4)
        if category_names:
            self.combo_category.current(0)

        tk.Label(frame_add, text="Описание:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.entry_desc = tk.Entry(frame_add, width=18)
        self.entry_desc.grid(row=3, column=1, padx=5, pady=4)

        tk.Label(frame_add, text="Дата:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        date_frame = tk.Frame(frame_add)
        date_frame.grid(row=4, column=1, sticky="w", padx=2, pady=4)

        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day

        years = [str(y) for y in range(2020, self.current_year + 1)]
        self.combo_year = ttk.Combobox(date_frame, values=years, width=5, state="readonly")
        self.combo_year.pack(side="left", padx=1)
        self.combo_year.set(str(self.current_year))
        self.combo_year.bind("<<ComboboxSelected>>", self.update_date_ranges)

        months = [f"{m:02d}" for m in range(1, 13)]
        self.combo_month = ttk.Combobox(date_frame, values=months, width=3, state="readonly")
        self.combo_month.pack(side="left", padx=1)
        self.combo_month.set(f"{self.current_month:02d}")
        self.combo_month.bind("<<ComboboxSelected>>", self.update_date_ranges)

        self.combo_day = ttk.Combobox(date_frame, width=3, state="readonly")
        self.combo_day.pack(side="left", padx=1)
        self.update_date_ranges()

        btn_add = tk.Button(frame_add, text="Добавить расход", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), command=self.add_expense)
        btn_add.grid(row=5, column=0, columnspan=2, pady=8)

        frame_templates = tk.LabelFrame(left_column, text=" Шаблоны и Пополнение ", font=("Arial", 10, "bold"))
        frame_templates.pack(fill="x", padx=5, pady=5)

        tk.Button(frame_templates, text="🚌 Автобус (110 ₸)", width=21, command=lambda: self.apply_template("Транспорт", 110, "Проезд на автобусе")).pack(pady=1)
        tk.Button(frame_templates, text="🚀 Экспресс (250 ₸)", width=21, command=lambda: self.apply_template("Транспорт", 250, "Проезд экспресс")).pack(pady=1)
        tk.Button(frame_templates, text="☕ Кофе (800 ₸)", width=21, command=lambda: self.apply_template("Еда", 800, "Кофе с собой")).pack(pady=1)
        tk.Button(frame_templates, text="🍽 Обед (2000 ₸)", width=21, command=lambda: self.apply_template("Еда", 2000, "Бизнес-ланч")).pack(pady=1)
        
        tk.Button(frame_templates, text="➕ Бюджет +10 000 ₸", width=21, bg="#d4efdf", command=lambda: self.add_to_budget(10000)).pack(pady=1)
        tk.Button(frame_templates, text="➕ Бюджет +15 000 ₸", width=21, bg="#d4efdf", command=lambda: self.add_to_budget(15000)).pack(pady=1)
        tk.Button(frame_templates, text="➕ Бюджет +20 000 ₸", width=21, bg="#d4efdf", command=lambda: self.add_to_budget(20000)).pack(pady=1)

        right_column = tk.Frame(main_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=5)

        frame_history = tk.LabelFrame(right_column, text=" История транзакций ", font=("Arial", 10, "bold"))
        frame_history.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("date", "category", "amount", "desc")
        self.tree = ttk.Treeview(frame_history, columns=columns, show="headings", height=14)
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("desc", text="Описание")
        
        self.tree.column("date", width=80, anchor="center")
        self.tree.column("category", width=100, anchor="w")
        self.tree.column("amount", width=70, anchor="e")
        self.tree.column("desc", width=110, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        frame_actions = tk.Frame(right_column)
        frame_actions.pack(fill="x", padx=5, pady=5)

        btn_report = tk.Button(frame_actions, text="Сводный отчёт", bg="#2980b9", fg="white", font=("Arial", 9, "bold"), command=self.show_report)
        btn_report.pack(side="left", padx=2, expand=True, fill="x")

        btn_save = tk.Button(frame_actions, text="Экспорт в JSON", bg="#8e44ad", fg="white", font=("Arial", 9, "bold"), command=self.save_json)
        btn_save.pack(side="right", padx=2, expand=True, fill="x")

    def edit_budget(self):
        new_val = simpledialog.askfloat("Изменение бюджета", "Введите общий лимит бюджета на месяц (₸):", initialvalue=self.total_budget_limit)
        if new_val is not None:
            self.total_budget_limit = new_val
            self.update_budget_display()

    def add_to_budget(self, amount):
        self.total_budget_limit += amount
        self.update_budget_display()
        messagebox.showinfo("Успех", f"К общему бюджету добавлено {amount:,.2f} ₸!")

    def update_budget_display(self):
        report = self.tracker.get_report()
        remaining = self.total_budget_limit - report.total_spent
        self.lbl_remaining.config(text=f"{remaining:,.2f} ₸")
        if remaining < 0:
            self.lbl_remaining.config(fg="#c0392b")
        else:
            self.lbl_remaining.config(fg="#27ae60")

    def apply_template(self, category, amount, description):
        self.combo_category.set(category)
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, str(amount))
        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, description)

    def update_date_ranges(self, event=None):
        selected_year = int(self.combo_year.get())
        selected_month = int(self.combo_month.get())
        today = datetime.date.today()

        if selected_year == today.year:
            max_month = today.month
            months = [f"{m:02d}" for m in range(1, max_month + 1)]
            self.combo_month['values'] = months
            if selected_month > max_month:
                self.combo_month.set(f"{max_month:02d}")
                selected_month = max_month
        else:
            self.combo_month['values'] = [f"{m:02d}" for m in range(1, 13)]

        _, max_days = calendar.monthrange(selected_year, selected_month)
        if selected_year == today.year and selected_month == today.month:
            max_day = today.day
        else:
            max_day = max_days

        days = [f"{d:02d}" for d in range(1, max_day + 1)]
        self.combo_day['values'] = days
        
        current_day_val = self.combo_day.get()
        if not current_day_val or int(current_day_val) > max_day:
            self.combo_day.set(f"{max_day:02d}")

    def add_expense(self):
        try:
            trans_id = int(self.entry_id.get().strip())
            amount = float(self.entry_amount.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "ID и сумма должны быть числами!")
            return

        category_name = self.combo_category.get()
        description = self.entry_desc.get().strip()
        
        y = self.combo_year.get()
        m = self.combo_month.get()
        d = self.combo_day.get()
        date_str = f"{y}-{m}-{d}"

        transaction = Transaction(
            trans_id=trans_id,
            category_name=category_name,
            amount=amount,
            description=description,
            date_str=date_str
        )

        try:
            self.tracker.add_transaction(transaction)
            self.tree.insert("", "end", values=(date_str, category_name, f"{amount:.2f} ₸", description))
            self.update_budget_display()
            
            messagebox.showinfo("Успех", f"Расход на сумму {amount} ₸ успешно добавлен!")
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

        report_text = f"Всего потрачено: {report.total_spent:.2f} ₸\n" \
                      f"Остаток бюджета: {self.total_budget_limit - report.total_spent:.2f} ₸\n" \
                      f"Количество транзакций: {report.transaction_count}\n\n" \
                      f"Последние операции:\n"
        
        for op in list(self.tracker.last_operations):
            report_text += f"- {op} ₸\n"

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
