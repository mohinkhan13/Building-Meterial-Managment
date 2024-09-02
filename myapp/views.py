from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import User
# Create your views here.


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        try:
            # Check if the email is already registered
            if User.objects.filter(email=request.POST['email']).exists():
                error = "Email Already Registered"
                return render(request, 'register.html', {'error': error})

            # Check if passwords match
            if request.POST['password'] != request.POST['cpassword']:
                error = "Passwords and confirm Password not matched"
                return render(request, 'register.html', {'error': error})

            # Check for valid mobile number length
            if len(request.POST['mobile']) != 10:
                error = "Please Enter a Valid Mobile Number"
                return render(request, 'register.html', {'error': error})

            # Create the user
            User.objects.create(
                fname=request.POST['fname'],
                lname=request.POST['lname'],
                address=request.POST['address'],
                email=request.POST['email'],
                mobile=request.POST['mobile'],
                password=make_password(request.POST['password']),
                profile_picture=request.FILES.get('profile_picture')
            )
            return redirect('login')  # Redirect to login page instead of rendering

        except User.DoesNotExist:
            error = "An error occurred. Please try again."
            return render(request, 'register.html', {'error': error})

    else:
        return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])

            # Check if the password is correct
            if not check_password(request.POST['password'], user.password):
                error = "Password is Incorrect"
                return render(request, 'login.html', {'error': error})

            # Set session variables

            else:
                request.session['email'] = user.email
                request.session['fname'] = user.fname
                request.session['profile_picture'] = user.profile_picture.url

                return redirect('index')

        except User.DoesNotExist:
            error = "Email Not Registered"
            return render(request, 'register.html', {'error': error})

    else:
        return render(request, 'login.html')


def forgot_password(request):
    return render(request, 'forgot-password.html')


def change_password(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.session['email'])

            # Check if old password matches
            if check_password(request.POST['old_password'], user.password):
                if request.POST['new_password'] == request.POST['cnew_password']:
                    if check_password(request.POST['new_password'], user.password):
                        error = "Old Password And New Password Must Not Be The Same"
                        return render(request, 'change-password.html', {'error': error})
                    else:
                        # Update password with hashing
                        user.password = make_password(request.POST['new_password'])
                        user.save()

                        # Clear session and logout
                        logout(request)
                        return redirect('login')
                else:
                    error = "New Password And Confirm New Password Must Be The Same"
                    return render(request, 'change-password.html', {'error': error})
            else:
                error = "Incorrect Old Password"
                return render(request, 'change-password.html', {'error': error})
        except User.DoesNotExist:
            return redirect('login')
    else:
        return render(request, 'change-password.html')


def user_profile(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        user.fname = request.POST['fname']
        user.lname = request.POST['lname']
        user.mobile = request.POST['mobile']
        user.address = request.POST['address']
        try:
            user.profile_picture = request.FILES['profile_picture']
        except:
            pass
        user.save()
        request.session['profile_picture'] = user.profile_picture.url
        return render(request, 'user-profile.html', {'user': user})
    else:
        return render(request, 'user-profile.html', {'user': user})


def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_picture']
        return render(request, 'login.html')
    except:
        msg = "User Logged Out Successfully"
        return render(request, 'login.html', {'msg': msg})


def contact(request):
    return render(request, 'contact.html')


def products(request):
    return render(request, 'products.html')
