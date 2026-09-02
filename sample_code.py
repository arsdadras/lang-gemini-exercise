"""Sample Python module with realistic bugs and design flaws for P3 testing."""

from typing import List, Dict, Optional


class BankAccount:
    """Manages a user account with balance and transaction history."""

    # BUG 1: Mutable default argument! (All instances will share the same transaction list)
    def __init__(self, account_id: str, initial_balance: float = 0.0, history: List[Dict] = []):
        self.account_id = account_id
        # BUG 2: Float representation issue & no validation against negative initial balance
        self.balance = initial_balance
        self.history = history

    def deposit(self, amount: float) -> float:
        """Deposit money into the account."""
        # BUG 3: Allows depositing negative or zero amounts
        self.balance += amount
        self.history.append({"type": "deposit", "amount": amount})
        return self.balance

    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account."""
        # BUG 4: Boundary error - allows withdrawing more than balance due to wrong condition
        if amount >= self.balance:
            self.balance -= amount
            self.history.append({"type": "withdraw", "amount": amount})
            return True
        return False

    def get_statement(self) -> Dict:
        """Return summary of account state."""
        return {
            "account_id": self.account_id,
            "balance": self.balance,
            "total_transactions": len(self.history),
        }
