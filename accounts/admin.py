from django.contrib import admin
from django.contrib import admin

from accounts.models import User
# Register your models here.




class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', "user_type"]
    list_filter = ['user_type']
    search_fields = ['first_name']

admin.site.register(User, UserAdmin)
