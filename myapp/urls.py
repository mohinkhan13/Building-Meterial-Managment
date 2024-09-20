from django.urls import path
from .views import *
urlpatterns = [
    path('', index , name='index'),
    path('register/', register , name='register'),
    path('login/', login , name='login'),
    path('logout/', logout , name='logout'),
    path('contact/', contact , name='contact'),
    path('forgot-password/', forgot_password , name='forgot-password'),
    path('change-password', change_password , name='change-password'),
    path('user-profile', user_profile , name='user-profile'),
    path('products/', products , name='products'),
    path('otp/', otp , name='otp'),
    path('new-password', new_password, name="new-password"),
    path('product-view/<int:id>', product_view, name='product-view'),
    path('wishlist/', wishlist, name='wishlist'),
    path('add-to-wishlist/<int:id>', add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/<int:id>', remove_wishlist, name='remove-from-wishlist'),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<int:id>', add_to_cart, name='add-to-cart'),
    path('remove-cart/<int:id>', remove_cart, name='remove-cart'),
    path('change-qty/', change_qty,name='change-qty'),
    path('create-checkout-session/', create_checkout_session, name='payment'),
    path('payment-success/<str:session_id>/', payment_success, name='payment-success'),
    path('success.html/', success,name='success'),
    path('cancel.html/', cancel,name='cancel'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order-list/', order_list,name='order-list'),
    path('contact/', contact_us, name='contact'),  # Add this line


    # Seller URLS

    path('seller-add-product/', seller_add_product, name='seller-add-product'),
    path('seller-edit-product/<int:id>/', seller_edit_product, name='seller-edit-product'),
    path('category/', category, name='category'),
    path('seller-product-publish/<int:id>', seller_product_publish, name='seller-product-publish'),

]