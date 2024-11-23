from django.db import models as m2
from django.contrib.auth.models import User
from django.utils import timezone

class Expense(m2.Model):
    EXPENSE_TYPE_CHOICES = [
        ('Food', 'Food'),
        ('Transportation', 'Transportation'),
        ('Utility', 'Utility'),
        ('Entertainment', 'Entertainment'),
        ('Other', 'Other'),
    ]

    user = m2.ForeignKey(User, on_delete=m2.CASCADE, related_name='expenses')  # Links the expense to the user
    expense_type = m2.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES)  # Type of the expense
    amount = m2.DecimalField(max_digits=10, decimal_places=2)  # Amount spent
    location = m2.CharField(max_length=255)  # Where the expense was incurred (e.g., restaurant, store, etc.)
    date = m2.DateField(default=timezone.now)  # Date the expense occurred
    description = m2.TextField()  # A description of the expense
    created_at = m2.DateTimeField(auto_now_add=True)  # Timestamp when the expense was created

    def __str__(self):
        return f"{self.expense_type} - {self.amount} - {self.date} - {self.created_at}"