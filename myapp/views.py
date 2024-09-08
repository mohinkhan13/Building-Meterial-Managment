from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from .models import *
import random
import requests
import json
import stripe

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

def index(request):
    try:
        user = User.objects.get(email=request.session['email'])

        if 'buyer' in user.usertype:
            products = Product.objects.filter(status='published')[:8]            
            return render(request, 'index.html',{'user':user,'products':products})
        else:
            return render(request, 'seller-index.html',{'user':user})
    except:
        products = Product.objects.filter(status='published')[:8]
        return render(request, 'index.html',{'products':products})


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
                usertype=request.POST['usertype'],
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
                wishlist = Wishlist.objects.filter(user=user)
                request.session['wishlist_count']=len(wishlist)

                if 'buyer' in user.usertype:
                    products = Product.objects.filter(status='published')[:4]
                    return render(request, 'index.html',{'user':user,'products':products})
                else:
                    return render(request,'seller-index.html',{'user':user})

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
    user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        try:            

            # Check if old password matches
            if check_password(request.POST['old_password'], user.password):
                if request.POST['new_password'] == request.POST['cnew_password']:
                    if check_password(request.POST['new_password'], user.password):
                        error = "Old Password And New Password Must Not Be The Same"
                        if user.usertype == "buyer":
                            return render(request, 'change-password.html', {'error': error})
                        else:
                            return render(request, 'seller-change-password.html', {'error': error})                        
                    else:
                        # Update password with hashing
                        user.password = make_password(request.POST['new_password'])
                        user.save()

                        # Clear session and logout
                        logout(request)
                        return redirect('login')
                else:
                    error = "New Password And Confirm New Password Must Be The Same"
                    if user.usertype == "buyer":
                            return render(request, 'change-password.html', {'error': error})
                    else:
                        return render(request, 'seller-change-password.html', {'error': error})                    
            else:
                error = "Incorrect Old Password"
                if user.usertype == "buyer":
                    return render(request, 'change-password.html', {'error': error})
                else:
                    return render(request, 'seller-change-password.html', {'error': error})
                
        except User.DoesNotExist:
            return redirect('login')
    else:
        if user.usertype == "buyer":
            return render(request, 'change-password.html')
        else:
            return render(request, 'seller-change-password.html')


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
        if user.usertype == "buyer":
            return render(request, 'user-profile.html', {'user': user})
        else:
            return render(request, 'seller-user-profile.html', {'user': user})
    else:
        if user.usertype == "buyer":
            return render(request, 'user-profile.html', {'user': user})
        else:
            return render(request, 'seller-user-profile.html', {'user': user})


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
    try:
        user = User.objects.get(email=request.session['email'])
        if user.usertype == 'buyer':
            products_list = Product.objects.filter(status='published')

            # Apply pagination with 20 products per page
            paginator = Paginator(products_list, 20)  # Show 20 products per page
            page_number = request.GET.get('page')  # Get the page number from the request
            products = paginator.get_page(page_number)  # Get the products for the current page

            return render(request, 'products.html', {'products': products})
        else:
            status_filter = request.GET.get('status')
            if status_filter in ['published', 'draft']:
                products = Product.objects.filter(status=status_filter)
            else:
                products = Product.objects.all() 

            total_count = Product.objects.count()
            published_count = Product.objects.filter(status='published').count()
            draft_count = Product.objects.filter(status='draft').count()
            return render(request, 'seller-products.html', {
            'products': products,
            'total_count': total_count,
            'published_count': published_count,
            'draft_count': draft_count,
            'current_status': status_filter
        })
    except:
        products_list = Product.objects.filter(status='published')

        # Apply pagination with 20 products per page
        paginator = Paginator(products_list, 20)  # Show 20 products per page
        page_number = request.GET.get('page')  # Get the page number from the request
        products = paginator.get_page(page_number)  # Get the products for the current page

        return render(request, 'products.html', {'products': products})        



def seller_add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        highlighted_price = request.POST.get('highlighted_price')
        category = request.POST.get('category')
        description = request.POST.get('description')
        status = request.POST.get('status')

        seller = User.objects.get(email=request.session['email'])
        category = Category.objects.get(name=category) if category else None
        product = Product(
            seller=seller,
            product_name=product_name,
            product_price=product_price,
            highlighted_price=highlighted_price,
            category=category,
            description=description,
            status=status
        )
        product.save()

        # Handle multiple image uploads
        images = request.FILES.getlist('product_image')
        first_image = None
        for i, image in enumerate(images):
            product_image = ProductImage.objects.create(product=product, image=image)
            if i == 0:
                first_image = product_image  # Set the first image as featured

        if first_image:
            product.featured_image = first_image
            product.save()

        return redirect('products')  # Redirect to a success page or list view

    categories = Category.objects.all()
    return render(request, 'seller-add-product.html', {'categories': categories})


def category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category', '').strip().lower()

        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                message = "Category already exists."
            except Category.DoesNotExist:
                Category.objects.create(name=category_name)
                message = "Category created successfully."
        else:
            message = "Please enter a valid category."

        categories = Category.objects.all()  # Fetch all categories for display
        return render(request, 'seller-category.html', {'message': message, 'categories': categories})

    categories = Category.objects.all()  # Fetch all categories when page loads
    return render(request, 'seller-category.html', {'categories': categories})

def seller_product_publish(request,id):
    product=Product.objects.get(id=id)
    product.status = 'published'
    product.save()

    return redirect('products')

def product_view(request, id):
    product = Product.objects.get(id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4]
    reviews = product.reviews.all()
    error_message = None
    
    if request.method == 'POST':
        content = request.POST.get('content')
        rating = request.POST.get('rating')

        try:
            user = User.objects.get(email=request.session.get('email'))
            
            # Validate the data
            if content and rating:
                rating = int(rating)
                if 1 <= rating <= 5:
                    # Create and save the review
                    Review.objects.create(
                        user=user,
                        product=product,
                        content=content,
                        rating=rating
                    )
                    return redirect('product-view', id=product.id)
                else:
                    error_message = "Rating must be between 1 and 5."
            else:
                error_message = "Please provide both review content and a rating."
        except User.DoesNotExist:
            error_message = "Please log in to submit a review."
            return redirect('login')
    
    return render(request, 'product-view.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'error_message': error_message,
    })

def wishlist(request):
    if 'email' not in request.session:
        return redirect('login')
    try:
        user = User.objects.get(email=request.session['email'])
    except User.DoesNotExist:
        return redirect('login')

    wishlist = Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlist)
    return render(request,'wishlist.html',{'wishlist_items':wishlist_items})

def add_to_wishlist(request,id):
    try:
        item = Product.objects.get(id=id)    
        user = User.objects.get(email=request.session['email'])
        if user:
            Wishlist.objects.create(user=user,product=item)
            return redirect('wishlist')
        else:
            message = 'Please Login First'
            return redirect('login')
    except:
        msg = "Please Login For Add Itme in Wishlist"
        return render(request,'login.html', {'msg':msg})

def remove_wishlist(request,id):
    wishlist = Wishlist.objects.get(id=id)
    wishlist.delete()
    return redirect('wishlist')

def cart(request):
    if 'email' not in request.session:
        return redirect('login')  # Redirect to login page if the user is not logged in
    try:
        user = User.objects.get(email=request.session['email'])
    except User.DoesNotExist:
        return redirect('login')  # Redirect to login page if the user is not found

    # Fetch the wishlist items for the user
    net_price=0
    carts = Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        net_price += i.total_price
    request.session['cart_counts']=len(carts)
    
    return render(request, 'cart.html', {'carts': carts, 'net_price':net_price, 'user':user})

def add_to_cart(request, id):
    try:
        product = Product.objects.get(id=id)
        user = User.objects.get(email=request.session['email'])
        if not Cart.objects.filter(user=user, product=product).exists():
            # Add the product to the wishlist if it's not already there
            Cart.objects.create(
                user=user,
                product=product,
                product_price=product.product_price,
                product_qty=1,
                total_price=product.product_price,
                payment_status=False
            )

        return redirect('cart')

    except:
        msg = "Please Login For Add Itme in Wishlist"
        return render(request,'login.html', {'msg':msg})

def remove_cart(request,id):
    product = Product.objects.get(id=id)
    user = User.objects.get(email=request.session['email'])
    cart = Cart.objects.get(user=user,product=product)
    cart.delete()
    return redirect('cart')

def change_qty(request):
    product_qty = int(request.POST.get('product_qty'))
    cid = int(request.POST.get('cid'))

    try:
        cart = Cart.objects.get(pk=cid)
        cart.product_qty = product_qty
        cart.total_price = cart.product_price * product_qty
        cart.save()
    except Cart.DoesNotExist:
        # Handle the case where the cart item does not exist
        pass

    return redirect('cart')

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = request.session.get('email', 'guest@example.com')  # Fallback if email is not in session
        amount = int(data['post_data'])        
        final_amount = amount * 100

        user = User.objects.get(email=request.session['email'])
        
        user_name = f"{user.fname} {user.lname}"
        user_address = f"{user.address}"
        user_mobile = f"{user.mobile}"
        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': final_amount,
                    'product_data': {
                        'name': 'Checkout Session Data',
                        'description': f'''Customer: {user_name},\n\n 
                        Address: {user_address}, \n 
                        Mobile: {user_mobile}''',
                    },
                    
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + f'/payment-success/{{CHECKOUT_SESSION_ID}}/',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
            customer_email=email,
            shipping_address_collection={
                'allowed_countries': ['IN'],
            },
        )

        return JsonResponse({'id': session.id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def payment_success(request, session_id):
    try:
        # Stripe se payment session ki details fetch karein
        session = stripe.checkout.Session.retrieve(session_id)
        customer_email = session.get('customer_email')
        payment_status = session.get('payment_status')
        
        # User ko retrieve karein email se
        user = get_object_or_404(User, email=customer_email)

        if payment_status == 'paid':
            # Agar payment successful ho, to Order entry create karein
            order = Order.objects.create(
                user=user,
                full_name=f"{user.fname} {user.lname}",
                address=user.address,
                mobile=user.mobile,
                total_amount=session['amount_total'] / 100,  # paisa ko INR me convert karen
                status='paid'
            )
            
            # User ke cart items ko fetch karein jo abhi tak paid nahi hain
            user_cart_items = Cart.objects.filter(user=user, payment_status=False)
           
            # Order items ko create karein aur Cart items ko delete karein
            for item in user_cart_items:
                OrderItem.objects.create(
                    seller=item.product.seller,
                    order=order,
                    product=item.product,
                    product_qty=item.product_qty,
                    product_price=item.product_price,
                    total_price=item.total_price
                )
            
            # Cart items ko delete karein
            user_cart_items.delete()

            # Cart count ko session mein update karein
            request.session['cart_counts'] = 0

            # Order success page render karein
            return render(request, 'order_success.html', {'order': order})
        else:
            return HttpResponse("Payment not successful")
    
    except stripe.error.StripeError as e:
        # Stripe se related error ko handle karein
        return HttpResponse(f"Stripe Error: {str(e)}", status=400)
    
    except Exception as e:
        # Any other error ko handle karein
        return HttpResponse(f"Error occurred: {str(e)}", status=500)



def success(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        i.payment_status=True
        i.save()
    carts=Cart.objects.filter(user=user,payment_status=False)
    request.session['cart_counts']=len(carts)
    return render(request,'success.html')

def cancel(request):
    return render(request,'cancel.html')

def order_list(request):
    try:
        user = User.objects.get(email=request.session['email'])
        orders = Order.objects.filter(user=user).order_by('-created_at')
        return render(request,'order-list.html', {'orders':orders})
    except:
        return render(request,'order-list.html')

def order_detail(request,order_id):
    user = User.objects.get(email=request.session['email'])
    order = Order.objects.get(id=order_id)
    return render(request,'order-detail.html', {'order':order})