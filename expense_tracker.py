import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# File to store expenses
CSV_FILE = "expenses.csv"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")
        
        # Initialize DataFrame
        if os.path.exists(CSV_FILE):
            self.df = pd.read_csv(CSV_FILE)
        else:
            self.df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
        
        # GUI Components
        self.create_widgets()
        self.update_expense_list()
    
    def create_widgets(self):
        # Frame for input
        input_frame = ttk.LabelFrame(self.root, text="Add New Expense", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Date
        ttk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, pady=5)
        
        # Category
        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky="w")
        self.category_var = tk.StringVar()
        categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        self.category_dropdown = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories)
        self.category_dropdown.grid(row=1, column=1, pady=5)
        
        # Amount
        ttk.Label(input_frame, text="Amount ($):").grid(row=2, column=0, sticky="w")
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=2, column=1, pady=5)
        
        # Description
        ttk.Label(input_frame, text="Description:").grid(row=3, column=0, sticky="w")
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=3, column=1, pady=5)
        
        # Add Button
        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Expense List
        list_frame = ttk.LabelFrame(self.root, text="Expense List", padding=10)
        list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tree = ttk.Treeview(list_frame, columns=("Date", "Category", "Amount", "Description"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount ($)")
        self.tree.heading("Description", text="Description")
        self.tree.pack(fill="both", expand=True)
        
        # Delete Button
        ttk.Button(list_frame, text="Delete Selected", command=self.delete_expense).pack(pady=5)
        
        # Visualization Frame
        viz_frame = ttk.LabelFrame(self.root, text="Spending Analysis", padding=10)
        viz_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # Plot Buttons
        ttk.Button(viz_frame, text="Show Pie Chart", command=self.plot_pie_chart).pack(pady=5)
        ttk.Button(viz_frame, text="Show Bar Chart", command=self.plot_bar_chart).pack(pady=5)
        
        # Matplotlib Figure
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
    
    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()
        desc = self.desc_entry.get()
        
        if not (date and category and amount):
            messagebox.showerror("Error", "Date, Category, and Amount are required!")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return
        
        new_expense = {"Date": date, "Category": category, "Amount": amount, "Description": desc}
        self.df = pd.concat([self.df, pd.DataFrame([new_expense])], ignore_index=True)
        self.df.to_csv(CSV_FILE, index=False)
        
        self.update_expense_list()
        self.clear_entries()
        messagebox.showinfo("Success", "Expense added successfully!")
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No expense selected!")
            return
        
        index = int(self.tree.index(selected[0]))
        self.df = self.df.drop(index).reset_index(drop=True)
        self.df.to_csv(CSV_FILE, index=False)
        self.update_expense_list()
        messagebox.showinfo("Success", "Expense deleted!")
    
    def update_expense_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for _, row in self.df.iterrows():
            self.tree.insert("", "end", values=(row["Date"], row["Category"], row["Amount"], row["Description"]))
    
    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.category_var.set("")
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
    
    def plot_pie_chart(self):
        if self.df.empty:
            messagebox.showerror("Error", "No expenses to display!")
            return
        
        self.ax.clear()
        category_totals = self.df.groupby("Category")["Amount"].sum()
        category_totals.plot(kind="pie", autopct="%1.1f%%", ax=self.ax)
        self.ax.set_title("Expenses by Category")
        self.canvas.draw()
    
    def plot_bar_chart(self):
        if self.df.empty:
            messagebox.showerror("Error", "No expenses to display!")
            return
        
        self.ax.clear()
        category_totals = self.df.groupby("Category")["Amount"].sum()
        category_totals.plot(kind="bar", ax=self.ax)
        self.ax.set_title("Expenses by Category")
        self.ax.set_ylabel("Amount ($)")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()