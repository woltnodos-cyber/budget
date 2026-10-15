import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from algorithm import BudgetTracker, JsonReportExporter
from model import Transaction, BudgetExceededError, InvalidTransactionDataError


class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта расходов — Астана Edition")
        self.root.geometry("800x850")
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

        self.last_stipend_month = None
        self.current_currency = "₸"
        self.current_rate = 1.0

        header_label = tk.Label(root, text=" Astana Edition 🏙️ ", font=("Arial", 16, "bold"), fg="#2980b9")
        header_label.pack(pady=5, fill="x")

        title_label = tk.Label(root, text="Управление личным бюджетом", font=("Arial", 12, "bold"), fg="#2c3e50")
        title_label.pack(pady=2)

        budget_frame = tk.Frame(root, bg="#e8f8f5", bd=2, relief="groove")
        budget_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(budget_frame, text="Остаток бюджета на месяц:", font=("Arial", 10), bg="#e8f8f5", fg="#7f8c8d").pack(pady=2)
        
        budget_display_frame = tk.Frame(budget_frame, bg="#e8f8f5")
        budget_display_frame.pack(pady=2)

        self.lbl_remaining = tk.Label(budget_display_frame, text=f"{self.total_budget_limit:,.2f} {self.current_currency}", font=("Arial", 22, "bold"), bg="#e8f8f5", fg="#27ae60")
        self.lbl_remaining.pack(side="left", padx=5)

        btn_edit_budget = tk.Button(budget_display_frame, text="✏️", font=("Arial", 12), command=self.edit_budget, bg="#ffffff", relief="raised")
        btn_edit_budget.pack(side="left", padx=5)

        btn_currency = tk.Button(budget_display_frame, text="💱 Конвертир", font=("Arial", 10), command=self.show_currency_converter, bg="#d1f2eb", relief="raised")
        btn_currency.pack(side="left", padx=5)

        btn_credit = tk.Button(budget_display_frame, text="💳 Кредит", font=("Arial", 10), command=self.ask_for_credit, bg="#fadbd8", relief="raised")
        btn_credit.pack(side="left", padx=5)

        main_container = tk.Frame(root)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(main_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_left = tk.Frame(self.canvas)
        self.scrollable_left.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_left, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        left_column = self.scrollable_left
        left_column.config(width=340)

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
            category_names = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Коммунальные услуги", "Другие расходы"]
            
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

        months = [str(m) for m in range(1, 13)]
        self.combo_month = ttk.Combobox(date_frame, values=months, width=3, state="readonly")
        self.combo_month.pack(side="left", padx=1)
        self.combo_month.set(str(self.current_month))

        days = [str(d) for d in range(1, 32)]
        self.combo_day = ttk.Combobox(date_frame, values=days, width=3, state="readonly")
        self.combo_day.pack(side="left", padx=1)
        self.combo_day.set(str(self.current_day))

        btn_add = tk.Button(frame_add, text="Добавить расход", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.add_transaction)
        btn_add.grid(row=5, column=0, columnspan=2, pady=8, sticky="ew", padx=5)

        frame_categories = tk.LabelFrame(left_column, text=" Категории и лимиты ", font=("Arial", 10, "bold"))
        frame_categories.pack(fill="x", padx=5, pady=5)

        self.tree_categories = ttk.Treeview(frame_categories, columns=("Category", "Limit", "Spent"), show="headings", height=5)
        self.tree_categories.heading("Category", text="Категория")
        self.tree_categories.heading("Limit", text="Лимит")
        self.tree_categories.heading("Spent", text="Потрачено")
        self.tree_categories.column("Category", width=110)
        self.tree_categories.column("Limit", width=85)
        self.tree_categories.column("Spent", width=85)
        self.tree_categories.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        cat_scroll = ttk.Scrollbar(frame_categories, orient="vertical", command=self.tree_categories.yview)
        cat_scroll.pack(side="right", fill="y")
        self.tree_categories.configure(yscrollcommand=cat_scroll.set)

        btn_edit_cat = tk.Button(left_column, text="Изменить лимит категории", bg="#3498db", fg="white", font=("Arial", 9), command=self.edit_category_limit)
        btn_edit_cat.pack(fill="x", padx=5, pady=2)

        frame_history = tk.LabelFrame(left_column, text=" История транзакций ", font=("Arial", 10, "bold"))
        frame_history.pack(fill="x", padx=5, pady=5)

        self.tree_history = ttk.Treeview(frame_history, columns=("ID", "Date", "Cat", "Sum", "Desc"), show="headings", height=6)
        self.tree_history.heading("ID", text="ID")
        self.tree_history.heading("Date", text="Дата")
        self.tree_history.heading("Cat", text="Категория")
        self.tree_history.heading("Sum", text="Сумма")
        self.tree_history.heading("Desc", text="Описание")
        self.tree_history.column("ID", width=30)
        self.tree_history.column("Date", width=70)
        self.tree_history.column("Cat", width=85)
        self.tree_history.column("Sum", width=65)
        self.tree_history.column("Desc", width=90)
        self.tree_history.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        hist_scroll = ttk.Scrollbar(frame_history, orient="vertical", command=self.tree_history.yview)
        hist_scroll.pack(side="right", fill="y")
        self.tree_history.configure(yscrollcommand=hist_scroll.set)

        btn_delete_tx = tk.Button(left_column, text="Удалить выбранную транзакцию", bg="#e74c3c", fg="white", font=("Arial", 9), command=self.delete_transaction)
        btn_delete_tx.pack(fill="x", padx=5, pady=2)

        frame_chart = tk.LabelFrame(left_column, text=" Аналитика расходов ", font=("Arial", 10, "bold"))
        frame_chart.pack(fill="x", padx=5, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(4, 2.5))
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=frame_chart)
        self.canvas_chart.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        self.update_ui()

    def update_ui(self):
        self.update_categories_display()
        self.update_history_display()
        self.update_chart()
        self.update_remaining_budget()

    def update_remaining_budget(self):
        total_spent = sum(tx.amount for tx in self.tracker.transactions) if hasattr(self.tracker, 'transactions') else 0.0
        remaining = self.total_budget_limit - total_spent
        converted_remaining = remaining / self.current_rate
        
        if remaining < 0:
            self.lbl_remaining.config(text=f"{converted_remaining:,.2f} {self.current_currency}", fg="#c0392b")
        else:
            self.lbl_remaining.config(text=f"{converted_remaining:,.2f} {self.current_currency}", fg="#27ae60")

    def update_categories_display(self):
        for row in self.tree_categories.get_children():
            self.tree_categories.delete(row)
            
        spent_per_cat = {}
        if hasattr(self.tracker, 'transactions'):
            for tx in self.tracker.transactions:
                spent_per_cat[tx.category_name] = spent_per_cat.get(tx.category_name, 0.0) + tx.amount

        for cat in self.tracker.categories.values():
            spent = spent_per_cat.get(cat.name, 0.0)
            limit_conv = cat.budget_limit / self.current_rate
            spent_conv = spent / self.current_rate
            self.tree_categories.insert("", "end", values=(cat.name, f"{limit_conv:,.2f}", f"{spent_conv:,.2f}"))

    def update_history_display(self):
        for row in self.tree_history.get_children():
            self.tree_history.delete(row)
        for tx in self.tracker.transactions:
            sum_conv = tx.amount / self.current_rate
            self.tree_history.insert("", "end", values=(tx.trans_id, tx.date_str, tx.category_name, f"{sum_conv:,.2f}", tx.description))

    def update_chart(self):
        self.ax.clear()
        
        spent_per_cat = {}
        if hasattr(self.tracker, 'transactions'):
            for tx in self.tracker.transactions:
                spent_per_cat[tx.category_name] = spent_per_cat.get(tx.category_name, 0.0) + tx.amount

        categories = [cat.name for cat in self.tracker.categories.values() if spent_per_cat.get(cat.name, 0.0) > 0]
        spents = [spent_per_cat[cat] / self.current_rate for cat in categories]
        
        if categories:
            self.ax.bar(categories, spents, color="#3498db")
            self.ax.set_title("Расходы по категориям", fontsize=9)
            self.ax.tick_params(axis='x', rotation=30, labelsize=8)
            self.ax.tick_params(axis='y', labelsize=8)
        else:
            self.ax.text(0.5, 0.5, "Нет данных о расходах", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
        
        self.fig.tight_layout()
        self.canvas_chart.draw()

    def add_transaction(self):
        try:
            tx_id = int(self.entry_id.get())
            amount = float(self.entry_amount.get()) * self.current_rate
            category = self.combo_category.get()
            desc = self.entry_desc.get()
            year = int(self.combo_year.get())
            month = int(self.combo_month.get())
            day = int(self.combo_day.get())
            tx_date_str = f"{year}-{month:02d}-{day:02d}"

            total_spent = sum(tx.amount for tx in self.tracker.transactions)
            remaining = self.total_budget_limit - total_spent

            if remaining - amount < 0:
                if messagebox.askyesno("Кредит", "У вас недостаточно средств, хотите взять кредит?"):
                    if messagebox.askyesno("Подтверждение кредита", "Вы точно уверены? Условия кредита: 50% каждый месяц"):
                        credit_amount = simpledialog.askfloat("Сумма кредита", "Введите сумму кредита (₸):", initialvalue=abs(remaining - amount) + 50000)
                        if credit_amount:
                            self.total_budget_limit += credit_amount
                    else:
                        return
                else:
                    return

            tx = Transaction(trans_id=tx_id, amount=amount, category_name=category, date_str=tx_date_str, description=desc)
            self.tracker.add_transaction(tx)
            
            self.entry_amount.delete(0, tk.END)
            self.entry_desc.delete(0, tk.END)
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(tx_id + 1))
            
            self.update_ui()
            messagebox.showinfo("Успех", "Транзакция успешно добавлена!")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных: {e}")
        except BudgetExceededError as e:
            messagebox.showwarning("Предупреждение", f"Лимит бюджета превышен!\n{e}")
        except InvalidTransactionDataError as e:
            messagebox.showerror("Ошибка", f"Ошибка транзакции: {e}")

    def delete_transaction(self):
        selected_item = self.tree_history.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите транзакцию для удаления!")
            return
        
        item_values = self.tree_history.item(selected_item, "values")
        tx_id = int(item_values[0])
        
        deleted = False
        for tx in list(self.tracker.transactions):
            if tx.trans_id == tx_id:
                self.tracker.transactions.remove(tx)
                deleted = True
                break
        
        if deleted:
            self.update_ui()
            messagebox.showinfo("Успех", "Транзакция удалена.")
        else:
            messagebox.showerror("Ошибка", "Не удалось найти транзакцию для удаления.")

    def edit_budget(self):
        new_limit = simpledialog.askfloat("Изменить бюджет", "Введите новый общий лимит бюджета (в тенге):", initialvalue=self.total_budget_limit)
        if new_limit is not None:
            self.total_budget_limit = new_limit
            self.update_remaining_budget()

    def edit_category_limit(self):
        selected_item = self.tree_categories.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите категорию для изменения лимита!")
            return
        
        item_values = self.tree_categories.item(selected_item, "values")
        cat_name = item_values[0]
        
        current_limit_conv = float(item_values[1].replace(",", ""))
        new_limit = simpledialog.askfloat("Лимит категории", f"Введите новый лимит для категории '{cat_name}':", initialvalue=current_limit_conv)
        
        if new_limit is not None:
            new_limit_base = new_limit * self.current_rate
            if cat_name in self.tracker.categories:
                self.tracker.categories[cat_name].budget_limit = new_limit_base
                self.update_ui()

    def ask_for_credit(self):
        if messagebox.askyesno("Кредит", "Хотите оформить кредит?"):
            if messagebox.askyesno("Подтверждение кредита", "Вы точно уверены? Условия кредита: 50% каждый месяц"):
                credit_amount = simpledialog.askfloat("Сумма кредита", "Введите сумму кредита (₸):")
                if credit_amount and credit_amount > 0:
                    self.total_budget_limit += credit_amount
                    self.update_remaining_budget()
                    messagebox.showinfo("Успех", f"Кредит на сумму {credit_amount:,.2f} ₸ успешно добавлен к бюджету!")

    def show_currency_converter(self):
        conv_window = tk.Toplevel(self.root)
        conv_window.title("Конвертер валют")
        conv_window.geometry("300x220")
        conv_window.resizable(False, False)

        tk.Label(conv_window, text="Выберите валюту отображения:", font=("Arial", 11, "bold")).pack(pady=10)

        def set_currency(curr, rate):
            self.current_currency = curr
            self.current_rate = rate
            self.update_ui()
            conv_window.destroy()

        tk.Button(conv_window, text="Тенге (₸)", width=20, command=lambda: set_currency("₸", 1.0)).pack(pady=3)
        tk.Button(conv_window, text="Доллар ($)", width=20, command=lambda: set_currency("$", 480.0)).pack(pady=3)
        tk.Button(conv_window, text="Евро (€)", width=20, command=lambda: set_currency("€", 520.0)).pack(pady=3)
        tk.Button(conv_window, text="Рубль (₽)", width=20, command=lambda: set_currency("₽", 5.2)).pack(pady=3)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()
