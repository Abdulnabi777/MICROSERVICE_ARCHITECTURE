from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserLoginHistory

# Home Page (Displays the list of users and provides an edit and delete option)
@login_required(login_url='login')
def HomePage(request):
    search_query = request.GET.get('q', '')  # Get the search query from the GET request
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all()

    # Pass the user's role (whether they are admin or not) to the template
    is_admin = request.user.is_superuser

    return render(request, 'home.html', {'users': users, 'is_admin': is_admin})
 

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('add_user')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('add_user')

        user = User.objects.create_user(username=username, email=email, password=password)
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        user.save()

        messages.success(request, "User added successfully.")
        return redirect('user_list')
    
    return render(request, 'home.html')

def user_list(request):
    search_query = request.GET.get('q', '')
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all()
    return render(request, 'home.html', {'users': users})

@login_required(login_url='login')
def EditUser(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit this user's profile.")
        return redirect('home')

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        new_password = request.POST.get('password')

        # Validate the new values
        if new_username != user.username and User.objects.filter(username=new_username).exists():
            messages.error(request, "Username already taken!")
            return redirect('edit_user', user_id=user.id)

        if new_email != user.email and User.objects.filter(email=new_email).exists():
            messages.error(request, "Email already taken!")
            return redirect('edit_user', user_id=user.id)

        # Update the user's details
        user.username = new_username
        user.email = new_email
        if new_password:
            user.set_password(new_password)  # Ensure the password is hashed properly

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('home')
    
    return render(request, 'edit_user.html', {'user': user})

# Delete User
@login_required(login_url='login')
def DeleteUser(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Only allow admins to delete users
    if request.user.is_superuser:
        user.delete()
        messages.success(request, "User deleted successfully!")
    else:
        messages.error(request, "You do not have permission to delete users.")

    return redirect('home')

def AddUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Check for username and email uniqueness
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('add_user')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('add_user')

        # Create the user
        user = User.objects.create_user(username, email, password)
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        user.save()

        messages.success(request, "User added successfully!")
        return redirect('home')

    return render(request, 'add_user.html')

# Signup Page
def SigupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        role = request.POST.get('role')  # Get the selected role from the dropdown

        # Check for username and email uniqueness
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # Create the user
        my_user = User.objects.create_user(uname, email, pass1)

        # Assign the role to the user
        if role == 'admin':
            my_user.is_superuser = True
            my_user.is_staff = True
        my_user.save()

        # Automatically log in the user after signup
        user = authenticate(username=uname, password=pass1)
        if user is not None:
            login(request, user)

        return redirect('login')  # Redirect to the home page after successful signup

    return render(request, 'signup.html')

def HomePage1(request):
    # You can implement similar functionality as HomePage for regular users, 
    # or make it simpler depending on your needs.
    search_query = request.GET.get('q', '')  # Get the search query from the GET request
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all()

    return render(request, 'home1.html', {'users': users})

# Login Page
def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)

            # Record the login event in the UserLoginHistory table
            UserLoginHistory.objects.create(user=user)  # This should be fine if user is valid

            # Redirect to the appropriate page based on user role
            if user.is_superuser:
                return redirect('home')  # Admin goes to home page (home.html)
            else:
                return redirect('home1')  # Regular user goes to home1 page (home1.html)
        else:
            messages.error(request, "Username or password is incorrect!!!")
            return redirect('login')

    return render(request, 'login.html')

# Logout Page
def LogoutPage(request):
    logout(request)
    return redirect('login')
