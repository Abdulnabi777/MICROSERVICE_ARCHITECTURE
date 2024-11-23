"""
URL configuration for registration project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views as v1
from app2 import views as v2
urlpatterns = [

    path('admin/', admin.site.urls),
    path('', v1.SigupPage, name='signup'),
    path('home/', v1.HomePage, name='home'),
    path('login/', v1.LoginPage, name='login'),
    path('logout/', v1.LogoutPage, name='logout'),
    # Edit and Delete User URLs
    path('edit_user/<int:user_id>/', v1.EditUser, name='edit_user'),
    path('delete_user/<int:user_id>/', v1.DeleteUser, name='delete_user'),

    path('home1/', v1.HomePage1, name='home1'),
    path('user_list/', v1.HomePage, name='user_list'),  # User List
    path('add_user/', v1.AddUser, name='add_user'),    # Add User
    path('add-expense/', v2.Expenses, name='add_expense'),
    path('view_expenses/', v2.View_Expenses, name='view_expenses'),
    path('user/report/', v2.user_report, name='user_report'),
    path('edit_expense/<int:expense_id>/', v2.EditExpense, name='edit_expense'),
    path('delete_expense/<int:expense_id>/', v2.DeleteExpense, name='delete_expense'),
    path('reporting/', v2.reporting, name='reporting'),
    path('expenses-for-month/', v2.expenses_for_month, name='expenses_for_month'),
    path('view_expenses_for_month/', v2.View_Expenses_For_Month, name='view_expenses_for_month'),
]

