# Generated by Django 5.1.3 on 2024-11-18 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0006_expense_created_at_alter_expense_date_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Expense',
        ),
    ]
