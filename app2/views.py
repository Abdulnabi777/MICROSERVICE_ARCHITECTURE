from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Expense
from .forms import ExpenseForm
from django.db.models import Sum,Avg
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def user_report(request):
    # Get the current time
    now = timezone.now()

    # Get the time range selected by the user (default is 'daily')
    time_range = request.GET.get('time_range', 'daily')  # Default is daily
    if time_range == 'daily':
        start_date = now - timedelta(days=1)
    elif time_range == 'weekly':
        start_date = now - timedelta(weeks=1)
    elif time_range == 'monthly':
        start_date = now - timedelta(days=30)  # Approx. 30 days for monthly
    elif time_range == 'yearly':
        start_date = now - timedelta(days=365)

    # Filter the user's expenses for the selected time range
    expenses = Expense.objects.filter(user=request.user, created_at__gte=start_date)

    # Aggregate the total expenses by expense type and date range
    expense_data = expenses.values('expense_type', 'date').annotate(total=Sum('amount')).order_by('date', 'expense_type')

    # Prepare data for Plotly
    expense_types = [entry['expense_type'] for entry in expense_data]
    expense_totals = [entry['total'] for entry in expense_data]

    # Creating the plot
    fig = make_subplots(rows=1, cols=1)

    # Create a bar chart with expense types on the X-axis and total amount on the Y-axis
    fig.add_trace(go.Bar(
        x=expense_types,  # Expense types as x-axis
        y=expense_totals,  # Total expenses as y-axis
        name="Total Expenses",
        marker=dict(color='blue'),
    ))

    # Customize the layout
    fig.update_layout(
        title=f"Total Expenses by Type ({time_range.capitalize()})",
        xaxis_title="Expense Type",
        yaxis_title="Total Amount",
        xaxis_tickangle=-45,
        template='plotly_dark',  # Choose a dark theme for the chart
        showlegend=False,
    )

    # Convert the plot to HTML for embedding in the template
    plot_div = fig.to_html(full_html=False)

    return render(request, 'user_report.html', {
        'plot_div': plot_div,  # Embed the interactive plot into the template
        'label': time_range.capitalize(),  # Display the label for the selected time range
    })

def Expenses(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Associate the logged-in user with the expense
            expense.save()  # Save the expense to the database
            messages.success(request, "Expense added successfully.")
            return redirect('home1')  # Redirect to the home page after successful submission
             
        else:
            messages.error(request, "There was an error with your form. Please try again.")
    else:
        form = ExpenseForm()  # Create an empty form for GET request

    return render(request, 'add_expense.html', {'form': form})

def View_Expenses(request):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Calculate the total expense for the current month for the logged-in user
    total_expenses_for_month = Expense.objects.filter(
        user=request.user,
        created_at__year=current_year,
        created_at__month=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Calculate the average expense for the current month for the logged-in user
    expenses_for_month = Expense.objects.filter(
        user=request.user,
        created_at__year=current_year,
        created_at__month=current_month
    )
    
    average_expense_for_month = expenses_for_month.aggregate(average=Avg('amount'))['average'] or 0

    # Round average expense to 2 decimal places
    average_expense_for_month = round(average_expense_for_month, 2)

    # Get the filter criteria from GET parameters
    expense_name_filter = request.GET.get('expense_name', '')
    amount_filter = request.GET.get('amount', '')
    location_filter = request.GET.get('location', '')
    from_date_filter = request.GET.get('from_date', '')
    to_date_filter = request.GET.get('to_date', '')

    # Build the base query for filtering expenses
    expenses_query = Expense.objects.filter(user=request.user)

    if from_date_filter:
        expenses_query = expenses_query.filter(created_at__gte=from_date_filter)

    if to_date_filter:
        expenses_query = expenses_query.filter(created_at__lte=to_date_filter)

    if expense_name_filter:
        expenses_query = expenses_query.filter(expense_type__icontains=expense_name_filter)

    if amount_filter:
        expenses_query = expenses_query.filter(amount__icontains=amount_filter)

    if location_filter:
        expenses_query = expenses_query.filter(location__icontains=location_filter)

    # Paginate results
    paginator = Paginator(expenses_query, 10)  # Show 10 expenses per page
    page_number = request.GET.get('page')
    expenses_for_current_page = paginator.get_page(page_number)

    return render(request, 'view_expense.html', {
        'total_expenses_for_month': total_expenses_for_month,
        'average_expense_for_month': average_expense_for_month,  # Pass the rounded value
        'expenses_for_current_page': expenses_for_current_page,
        'expense_name_filter': expense_name_filter,
        'amount_filter': amount_filter,
        'location_filter': location_filter,
        'from_date_filter': from_date_filter,
        'to_date_filter': to_date_filter,
    })

def EditExpense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully.")
            return redirect('view_expenses')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'edit_expense.html', {'form': form})

def DeleteExpense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully.")
        return redirect('view_expenses')
    
    return render(request, 'confirm_delete.html', {'expense': expense})

def View_Expenses_For_Month(request):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Fetch all expenses for the current month for the logged-in user
    expenses_for_month = Expense.objects.filter(
        user=request.user,
        created_at__year=current_year,
        created_at__month=current_month
    )

    return render(request, 'view_expenses_for_month.html', {
        'expenses_for_month': expenses_for_month,
    })

def expenses_for_month(request):
    # Get current month
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Filter expenses for the current month
    expenses = Expense.objects.filter(
        created_at__year=current_year, created_at__month=current_month
    )

    # Apply search if present
    search_query = request.GET.get('search', '')
    if search_query:
        expenses = expenses.filter(
            Q(user__username__icontains=search_query) |
            Q(expense_type__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Paginate results
    paginator = Paginator(expenses, 10)  # Show 10 expenses per page
    page_number = request.GET.get('page')
    expenses_for_month = paginator.get_page(page_number)

    return render(request, 'expenses_for_month.html', {
        'expenses_for_month': expenses_for_month,
    })

def reporting(request):
    # Get the current date and the first day of the current month
    now = timezone.now()
    start_of_month = timezone.datetime(now.year, now.month, 1)

    # Calculate the total number of users
    total_users = User.objects.count()

    # Calculate total expenses for the current month for all users
    total_expenses = Expense.objects.filter(created_at__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0

    # Calculate average expense per user for the current month
    users_with_expenses = Expense.objects.filter(created_at__gte=start_of_month).values('user').distinct()
    total_expense_per_user = total_expenses / len(users_with_expenses) if len(users_with_expenses) > 0 else 0

    # Filters
    user_filter = request.GET.get('user', '')
    expense_name_filter = request.GET.get('expense_name', '')
    amount_filter = request.GET.get('amount', '')
    location_filter = request.GET.get('location', '')
    from_date_filter = request.GET.get('from_date', '')
    to_date_filter = request.GET.get('to_date', '')

    # Build the base query for filtering expenses
    expenses_query = Expense.objects.filter(created_at__gte=start_of_month)

    if user_filter:
        expenses_query = expenses_query.filter(user__username__icontains=user_filter)

    if expense_name_filter:
        expenses_query = expenses_query.filter(expense_type__icontains=expense_name_filter)

    if amount_filter:
        expenses_query = expenses_query.filter(amount__icontains=amount_filter)

    if location_filter:
        expenses_query = expenses_query.filter(location__icontains=location_filter)

    if from_date_filter:
        expenses_query = expenses_query.filter(created_at__gte=from_date_filter)

    if to_date_filter:
        expenses_query = expenses_query.filter(created_at__lte=to_date_filter)

    # Get the filtered expenses
    filtered_expenses = expenses_query

    # When the user clicks the "View Graph" button
    if request.GET.get('view_graph') == 'true':
        # Aggregate expenses by type for the graph
        expense_data = Expense.objects.filter(created_at__gte=start_of_month).values('expense_type').annotate(
            total_amount=Sum('amount')
        ).order_by('expense_type')

        expense_types = [entry['expense_type'] for entry in expense_data]
        total_amounts = [entry['total_amount'] for entry in expense_data]

        # Create a Plotly graph
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Bar(
            x=expense_types,
            y=total_amounts,
            name="Total Expenses",
            marker=dict(color='blue'),
        ))

        fig.update_layout(
            title="Total Expenses by Type (Current Month)",
            xaxis_title="Expense Type",
            yaxis_title="Total Amount",
            template='plotly_dark',
            showlegend=False,
        )

        # Convert the plot to HTML
        plot_div = fig.to_html(full_html=False)

        # Return the graph to a new page
        return render(request, 'report_graph.html', {'plot_div': plot_div})

    return render(request, 'reporting.html', {
        'total_users': total_users,
        'total_expenses': total_expenses,
        'total_expense_per_user': total_expense_per_user,
        'filtered_expenses': filtered_expenses,
    })