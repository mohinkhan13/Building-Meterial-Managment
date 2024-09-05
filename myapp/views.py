from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import random
import requests


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
    if request.method == 'POST':
        email_or_mobile = request.POST.get('email_or_mobile').strip()  # Ensure no leading/trailing spaces    

        try:
            # Attempt to find user by email or mobile
            user_by_email = User.objects.filter(email=email_or_mobile).first()
            user_by_mobile = User.objects.filter(mobile=email_or_mobile).first()

            if user_by_email:
                user = user_by_email
            elif user_by_mobile:
                user = user_by_mobile
            else:
                # If neither email nor mobile found
                error = "Email or Mobile Number not found. Please enter valid details."
                return render(request, 'forgot-password.html', {'error': error})

            # Generate OTP
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['email_or_mobile'] = email_or_mobile

            if user.email == email_or_mobile:
                # Send OTP via email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}. It is valid for 2 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                msg = "OTP has been sent successfully to your email."                    

            elif user.mobile == email_or_mobile:
                # Send OTP via SMS
                mobile = str(email_or_mobile)
                otp = str(random.randint(100000, 999999))
                url = "https://www.fast2sms.com/dev/bulkV2"
                querystring = {
                    "authorization": "TIjv2PHxGFWfdeUqrO5VmSB6MY7Rcnh93ioDutwk0ZaspJAb8QXURP07NkDjvS6HEZVtBCF8MdbYs2n9",  # Replace with your actual API key
                    "variables_values": otp,
                    "route": "otp",
                    "numbers": mobile
                }
                headers = {'cache-control': "no-cache"}
                response = requests.request("GET", url, headers=headers, params=querystring)

                if response.status_code == 200:
                    msg = "OTP has been sent successfully to your Mobile."
                else:
                    msg = f"Failed to send OTP. API response: {response.text}"

            return render(request, 'otp.html', {'msg': msg})

        except Exception as e:
            error = f"An error occurred: {str(e)}"
            return render(request, 'forgot-password.html', {'error': error})

    else:
        return render(request, 'forgot-password.html')


def otp(request):
    otp1 = int(request.session.get('otp'))
    otp2 = int(request.POST.get('otp'))

    if otp1 is None:
        error = "OTP has expired or is invalid."
        return render(request, 'otp.html', {'error': error})

    if otp1 == otp2:
        del request.session['otp']
        return redirect('new-password')
    else:
        error = "OTP does not match."
        return render(request, 'otp.html', {'error': error})

def new_password(request):
    new_password = request.POST.get('new_password')
    cnew_password = request.POST.get('cnew_password')

    if new_password and cnew_password:
        if new_password == cnew_password:
            try:
                # Find the user by email or mobile, whichever was used
                user = User.objects.filter(email=request.session['email_or_mobile']).first()
                if not user:
                    user = User.objects.filter(mobile=request.session['email_or_mobile']).first()
                
                # Ensure the user exists
                if user:
                    # Hash the new password and save it
                    user.password = make_password(new_password)
                    user.save()

                    # Clear session
                    del request.session['email_or_mobile']
                    
                    msg = "Password Change Successfully"
                    return render(request,'login.html', {'msg':msg})
                else:
                    error = "User Not Found"
                    return render(request, 'new-password.html', {'error': error})
            
            except Exception as e:
                error = f"An error occurred: {str(e)}"
                return render(request, 'new-password.html', {'error': error})
        else:
            msg = 'Password And Confirm Password Do Not Match'
            return render(request, 'new-password.html', {'msg': msg})
    else:
        error = "Both password fields are required."
        return render(request, 'new-password.html', {'error': error})

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
