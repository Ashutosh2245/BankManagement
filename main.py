##>>>>>>>>>>>>>>> BANK MANAGEMENT PROJECT <<<<<<<<<<<<<<<<<##

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import json
import random
import string
from pathlib import Path

class Bank:
    database = 'data.json'
    data = []

    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            data = []
    except Exception as err:
        print(f"Exception loading data: {err}")

    @classmethod
    def __update(cls):
        with open(cls.database, 'w') as fs:
            fs.write(json.dumps(Bank.data, indent=4))

    @classmethod
    def __accountgenerate(cls):
        # Generate 10 digit numeric account number
        return ''.join(random.choices(string.digits, k=10))

    def create_account(self, name, age, email, pin, account_type):
        if age < 18 or len(str(pin)) != 4:
            return False, "Age must be >= 18 and PIN must be 4 digits."

        account_no = Bank.__accountgenerate()
        info = {
            "name": name,
            "age": age,
            "email": email,
            "pin": pin,
            "accountNo.": account_no,
            "balance": 0,
            "transactions": [],
            "account_type": account_type,
            "loan": 0,
        }
        Bank.data.append(info)
        Bank.__update()
        return True, f"Account created! Your account number is: {account_no}"

    def validate_user(self, accnumber, pin):
        user = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]
        if not user:
            return None
        return user[0]

    def deposit_money(self, accnumber, pin, amount):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        if amount <= 0 or amount > 100000:
            return False, "Deposit amount must be between 1 and 100000."
        user['balance'] += amount
        user['transactions'].append({
            "type": "deposit",
            "amount": amount,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        Bank.__update()
        return True, f"₹{amount} deposited successfully."

    def withdraw_money(self, accnumber, pin, amount):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        if amount <= 0:
            return False, "Withdrawal amount must be positive."
        if user['balance'] < amount:
            return False, "Insufficient balance."
        user['balance'] -= amount
        user['transactions'].append({
            "type": "withdraw",
            "amount": amount,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        Bank.__update()
        return True, f"₹{amount} withdrawn successfully."

    def apply_loan(self, accnumber, pin, amount):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        if amount <= 0:
            return False, "Loan amount must be positive."
        if user['loan'] > 0:
            return False, "You already have an outstanding loan."
        user['loan'] = amount
        Bank.__update()
        return True, f"Loan of ₹{amount} granted."

    def repay_loan(self, accnumber, pin, amount):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        if amount <= 0:
            return False, "Repayment amount must be positive."
        if user['loan'] == 0:
            return False, "No outstanding loan to repay."
        if amount > user['loan']:
            amount = user['loan']  # repay only outstanding loan
        if user['balance'] < amount:
            return False, "Insufficient balance to repay loan."
        user['balance'] -= amount
        user['loan'] -= amount
        Bank.__update()
        return True, f"₹{amount} loan repaid. Remaining loan: ₹{user['loan']}"

    def get_details(self, accnumber, pin):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        return True, user

    def add_interest(self, accnumber, pin, rate, time_years):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        interest = (user['balance'] * rate * time_years) / 100
        user['balance'] += interest
        user['transactions'].append({
            "type": "interest",
            "amount": interest,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        Bank.__update()
        return True, f"₹{interest:.2f} interest added."

    def get_transactions(self, accnumber, pin):
        user = self.validate_user(accnumber, pin)
        if not user:
            return False, "Invalid account or PIN."
        return True, user.get("transactions", [])

# --- GUI part ---

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BankApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bank = Bank()
        self.title("Royal Bank of India")
        self.geometry("500x500")

        self.current_user = None

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Royal Bank of India", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        ctk.CTkLabel(self, text="Account Number:").pack(pady=5)
        self.acc_entry = ctk.CTkEntry(self)
        self.acc_entry.pack()

        ctk.CTkLabel(self, text="PIN:").pack(pady=5)
        self.pin_entry = ctk.CTkEntry(self, show="*")
        self.pin_entry.pack()

        ctk.CTkButton(self, text="Login", command=self.login).pack(pady=20)
        ctk.CTkButton(self, text="Create New Account", command=self.create_account_screen).pack()

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

    def login(self):
        acc = self.acc_entry.get()
        try:
            pin = int(self.pin_entry.get())
        except:
            messagebox.showerror("Error", "PIN must be 4 digit number")
            return

        user = self.bank.validate_user(acc, pin)
        if user:
            self.current_user = user
            self.create_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Account Number or PIN")

    def create_account_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Create Account", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(self, text="Name:").pack()
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack()

        ctk.CTkLabel(self, text="Age:").pack()
        self.age_entry = ctk.CTkEntry(self)
        self.age_entry.pack()

        ctk.CTkLabel(self, text="Email:").pack()
        self.email_entry = ctk.CTkEntry(self)
        self.email_entry.pack()

        ctk.CTkLabel(self, text="PIN (4 digits):").pack()
        self.new_pin_entry = ctk.CTkEntry(self, show="*")
        self.new_pin_entry.pack()

        ctk.CTkLabel(self, text="Account Type:").pack()
        self.account_type_var = ctk.StringVar(value="Savings")
        ctk.CTkRadioButton(self, text="Savings", variable=self.account_type_var, value="Savings").pack()
        ctk.CTkRadioButton(self, text="Current", variable=self.account_type_var, value="Current").pack()

        ctk.CTkButton(self, text="Create", command=self.create_account).pack(pady=20)
        ctk.CTkButton(self, text="Back to Login", command=self.create_login_screen).pack()

    def create_account(self):
        name = self.name_entry.get()
        age_str = self.age_entry.get()
        email = self.email_entry.get()
        pin_str = self.new_pin_entry.get()
        acc_type = self.account_type_var.get()

        if not name or not age_str or not email or not pin_str:
            messagebox.showerror("Error", "All fields are required.")
            return
        try:
            age = int(age_str)
            pin = int(pin_str)
        except:
            messagebox.showerror("Error", "Age and PIN must be numbers.")
            return
        success, msg = self.bank.create_account(name, age, email, pin, acc_type)
        if success:
            messagebox.showinfo("Success", msg)
            self.create_login_screen()
        else:
            messagebox.showerror("Error", msg)

    def create_dashboard(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text=f"Welcome, {self.current_user['name']}!", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self, text=f"Balance: ₹{self.current_user['balance']:.2f}").pack()
        ctk.CTkLabel(self, text=f"Loan Outstanding: ₹{self.current_user.get('loan', 0):.2f}").pack(pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10, fill="x", padx=20)

        buttons = [
            ("Deposit", self.deposit_screen),
            ("Withdraw", self.withdraw_screen),
            ("Apply Loan", self.apply_loan_screen),
            ("Repay Loan", self.repay_loan_screen),
            ("Show Details", self.show_details_screen),
            ("Show Transactions", self.show_transactions_screen),
            ("Add Interest", self.add_interest_screen),
            ("Update Details", self.update_details_screen),
            ("Delete Account", self.delete_account_screen),
            ("Logout", self.logout),
        ]

        for (text, cmd) in buttons:
            btn = ctk.CTkButton(btn_frame, text=text, command=cmd)
            btn.pack(pady=5, fill="x")

    def logout(self):
        self.current_user = None
        self.create_login_screen()

    def deposit_screen(self):
        self.popup_amount("Deposit Money", self.deposit_action)

    def withdraw_screen(self):
        self.popup_amount("Withdraw Money", self.withdraw_action)

    def apply_loan_screen(self):
        self.popup_amount("Apply for Loan", self.apply_loan_action)

    def repay_loan_screen(self):
        self.popup_amount("Repay Loan", self.repay_loan_action)

    def add_interest_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Add Interest", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(self, text="Annual Interest Rate (%)").pack()
        self.interest_rate_entry = ctk.CTkEntry(self)
        self.interest_rate_entry.pack()

        ctk.CTkLabel(self, text="Time (Years)").pack()
        self.interest_time_entry = ctk.CTkEntry(self)
        self.interest_time_entry.pack()

        ctk.CTkButton(self, text="Add Interest", command=self.add_interest_action).pack(pady=20)
        ctk.CTkButton(self, text="Back", command=self.create_dashboard).pack()

    def update_details_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Update Details", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(self, text=f"Current Name: {self.current_user['name']}").pack()
        ctk.CTkLabel(self, text=f"Current Email: {self.current_user['email']}").pack()

        ctk.CTkLabel(self, text="New Name").pack()
        self.update_name_entry = ctk.CTkEntry(self)
        self.update_name_entry.pack()

        ctk.CTkLabel(self, text="New Email").pack()
        self.update_email_entry = ctk.CTkEntry(self)
        self.update_email_entry.pack()

        ctk.CTkLabel(self, text="New PIN (4 digits)").pack()
        self.update_pin_entry = ctk.CTkEntry(self, show="*")
        self.update_pin_entry.pack()

        ctk.CTkButton(self, text="Update", command=self.update_details_action).pack(pady=20)
        ctk.CTkButton(self, text="Back", command=self.create_dashboard).pack()

    def delete_account_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Delete Account", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self, text="Are you sure you want to delete your account?").pack(pady=10)

        ctk.CTkButton(self, text="Delete", fg_color="red", command=self.delete_account_action).pack(pady=10)
        ctk.CTkButton(self, text="Cancel", command=self.create_dashboard).pack()

    def show_details_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Account Details", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        details = "\n".join([f"{k}: {v}" for k, v in self.current_user.items() if k != 'transactions'])
        ctk.CTkLabel(self, text=details).pack(pady=10)

        ctk.CTkButton(self, text="Back", command=self.create_dashboard).pack(pady=20)

    def show_transactions_screen(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Transaction History", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        txns = self.current_user.get("transactions", [])
        if not txns:
            ctk.CTkLabel(self, text="No transactions yet.").pack(pady=10)
        else:
            for txn in txns[-10:][::-1]:  # show last 10 txns
                ctk.CTkLabel(self, text=f"{txn['time']} | {txn['type'].capitalize()} | ₹{txn['amount']}").pack()

        ctk.CTkButton(self, text="Back", command=self.create_dashboard).pack(pady=20)

    # Actions for buttons
    def popup_amount(self, title, callback):
        popup = ctk.CTkToplevel(self)
        popup.geometry("300x200")
        popup.title(title)

        ctk.CTkLabel(popup, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(popup, text="Amount:").pack()
        amount_entry = ctk.CTkEntry(popup)
        amount_entry.pack(pady=10)

        def submit():
            try:
                amt = float(amount_entry.get())
            except:
                messagebox.showerror("Error", "Enter a valid amount.")
                return
            callback(amt)
            popup.destroy()

        ctk.CTkButton(popup, text="Submit", command=submit).pack(pady=10)

    def deposit_action(self, amount):
        success, msg = self.bank.deposit_money(self.current_user['accountNo.'], self.current_user['pin'], amount)
        if success:
            self.current_user['balance'] += amount
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.create_dashboard()

    def withdraw_action(self, amount):
        success, msg = self.bank.withdraw_money(self.current_user['accountNo.'], self.current_user['pin'], amount)
        if success:
            self.current_user['balance'] -= amount
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.create_dashboard()

    def apply_loan_action(self, amount):
        success, msg = self.bank.apply_loan(self.current_user['accountNo.'], self.current_user['pin'], amount)
        if success:
            self.current_user['loan'] = amount
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.create_dashboard()

    def repay_loan_action(self, amount):
        success, msg = self.bank.repay_loan(self.current_user['accountNo.'], self.current_user['pin'], amount)
        if success:
            self.current_user['loan'] -= amount
            self.current_user['balance'] -= amount
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.create_dashboard()

    def add_interest_action(self):
        try:
            rate = float(self.interest_rate_entry.get())
            time = float(self.interest_time_entry.get())
        except:
            messagebox.showerror("Error", "Enter valid numbers for rate and time.")
            return
        success, msg = self.bank.add_interest(self.current_user['accountNo.'], self.current_user['pin'], rate, time)
        if success:
            self.current_user['balance'] += (self.current_user['balance'] * rate * time) / 100
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.create_dashboard()

    def update_details_action(self):
        new_name = self.update_name_entry.get()
        new_email = self.update_email_entry.get()
        new_pin = self.update_pin_entry.get()

        if new_name:
            self.current_user['name'] = new_name
        if new_email:
            self.current_user['email'] = new_email
        if new_pin:
            if len(new_pin) != 4 or not new_pin.isdigit():
                messagebox.showerror("Error", "PIN must be 4 digits.")
                return
            self.current_user['pin'] = int(new_pin)

        Bank.__update()
        messagebox.showinfo("Success", "Details updated.")
        self.create_dashboard()

    def delete_account_action(self):
        Bank.data = [acc for acc in Bank.data if acc['accountNo.'] != self.current_user['accountNo.']]
        Bank.__update()
        messagebox.showinfo("Deleted", "Your account has been deleted.")
        self.current_user = None
        self.create_login_screen()

if __name__ == "__main__":
    app = BankApp()
    app.mainloop()

##PROJECT COMPLETED.