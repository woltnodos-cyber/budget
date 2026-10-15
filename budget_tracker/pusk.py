import base64
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from algorithm import BudgetTracker, JsonReportExporter
from model import Transaction, BudgetExceededError, InvalidTransactionDataError

IMAGE_DATA = b"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"

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

        try:
            self.img_data = base64.b64decode(IMAGE_DATA)
            self.photo_img = tk.PhotoImage(data=self.img_data)
            self.img_label = tk.Label(root, image=self.photo_img)
            self.img_label.pack(pady=5)
        except Exception as e:
            print(e)

        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_widgets()

    def create_widgets(self):
        top_frame = ttk.Frame(self.scrollable_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        btn_convert = ttk.Button(top_frame, text="Конвертир", command=self.change_currency)
        btn_convert.pack(side=tk.LEFT, padx=5)

        budget_frame = ttk.LabelFrame(self.scrollable_frame, text="Общий бюджет")
        budget_frame.pack(fill=tk.X, padx=10, pady=10)

        self.lbl_total = ttk.Label(budget_frame, text=f"Лимит: {self.total_budget_limit} {self.current_currency}", font=("Arial", 12, "bold"))
        self.lbl_total.pack(padx=10, pady=10, anchor="w")

        categories_frame = ttk.LabelFrame(self.scrollable_frame, text="Категории и расходы")
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.cat_tree = ttk.Treeview(categories_frame, columns=("name", "limit", "spent"), show="headings", height=6)
        self.cat_tree.heading("name", text="Категория")
        self.cat_tree.heading("limit", text="Лимит")
        self.cat_tree.heading("spent", text="Потрачено")
        self.cat_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_categories()

        trans_frame = ttk.LabelFrame(self.scrollable_frame, text="Добавить операцию")
        trans_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(trans_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_amount = ttk.Entry(trans_frame)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(trans_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_category = ttk.Combobox(trans_frame, values=list(self.tracker.categories.keys()))
        self.combo_category.grid(row=1, column=1, padx=5, pady=5)

        btn_add = ttk.Button(trans_frame, text="Добавить расход", command=self.add_transaction)
        btn_add.grid(row=2, column=0, columnspan=2, pady=10)

        chart_frame = ttk.LabelFrame(self.scrollable_frame, text="Аналитика")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_chart(chart_frame)

    def refresh_categories(self):
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        for cat_name, cat_obj in self.tracker.categories.items():
            converted_limit = cat_obj.budget_limit / self.current_rate
            converted_spent = cat_obj.spent / self.current_rate
            self.cat_tree.insert("", tk.END, values=(cat_name, f"{converted_limit:.2f} {self.current_currency}", f"{converted_spent:.2f} {self.current_currency}"))

    def add_transaction(self):
        try:
            amount = float(self.entry_amount.get()) * self.current_rate
            category = self.combo_category.get()
            if not category:
                messagebox.showerror("Ошибка", "Выберите категорию!")
                return
            
            tx = Transaction(amount=amount, category=category, date=datetime.date.today())
            self.tracker.add_transaction(tx)
            self.refresh_categories()
            self.lbl_total.config(text=f"Лимит: {self.total_budget_limit / self.current_rate:.2f} {self.current_currency}")
            messagebox.showinfo("Успех", "Транзакция успешно добавлена!")
            self.entry_amount.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для суммы!")
        except BudgetExceededError as e:
            messagebox.showwarning("Внимание", f"Лимит бюджета превышен: {e}")
        except InvalidTransactionDataError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")

    def show_chart(self, parent):
        fig, ax = plt.subplots(figsize=(5, 3))
        categories = list(self.tracker.categories.keys())
        spents = [cat.spent / self.current_rate for cat in self.tracker.categories.values()]
        
        ax.bar(categories, spents, color='skyblue')
        ax.set_title("Расходы по категориям")
        ax.set_ylabel(f"Сумма ({self.current_currency})")
        plt.xticks(rotation=45, ha='right')
        fig.tight_layout()

        canvas_chart = FigureCanvasTkAgg(fig, master=parent)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def change_currency(self):
        currency_window = tk.Toplevel(self.root)
        currency_window.title("Выбор валюты")
        currency_window.geometry("250x200")
        
        ttk.Label(currency_window, text="Выберите валюту:", font=("Arial", 11)).pack(pady=10)
        
        def set_curr(curr, rate):
            self.current_currency = curr
            self.current_rate = rate
            self.refresh_categories()
            self.lbl_total.config(text=f"Лимит: {self.total_budget_limit / self.current_rate:.2f} {self.current_currency}")
            messagebox.showinfo("Валюта", f"Валюта изменена на {curr}")
            currency_window.destroy()

        ttk.Button(currency_window, text="Тенге (₸)", command=lambda: set_curr("₸", 1.0)).pack(pady=5)
        ttk.Button(currency_window, text="Доллар ($)", command=lambda: set_curr("$", 480.0)).pack(pady=5)
        ttk.Button(currency_window, text="Евро (€)", command=lambda: set_curr("€", 520.0)).pack(pady=5)
        ttk.Button(currency_window, text="Рубль (₽)", command=lambda: set_curr("₽", 5.2)).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()
