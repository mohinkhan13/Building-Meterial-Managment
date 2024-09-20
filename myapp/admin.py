from django.contrib import admin
from .models import *
# Register your models here.
class UserAdmin(admin.ModelAdmin):
	list_display = ('fname', 'email', 'mobile', 'usertype')
	search_fields = ('fname', 'email', 'mobile')
	list_filter = ('usertype',)

admin.site.register(User,UserAdmin)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Cart)
# admin.site.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')  # Columns to display in the list view
    search_fields = ('name', 'email', 'subject')  # Fields to enable search functionality
    list_filter = ('created_at',)  # Filter by created date

admin.site.register(ContactMessage, ContactMessageAdmin)
