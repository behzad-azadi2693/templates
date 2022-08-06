from django.contrib import admin

import django.apps
models = django.apps.apps.get_models()
for model in models:
    try:
        admin.site.register(model)
    except:
        admin.site.unregister(model)

admin.site.index_title = 'Shoes Shop'
admin.site.site_header = 'The Shoes Admin'
admin.site.site_title = 'Title Shoes Shop'




# Register your models here.
from django.contrib.auth import get_user_model
from .forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

class UserControlling(admin.AdminSite):
    site_header = 'User Controlling'
    login_template = 'accounts/admin/login.html'

user_control = UserControlling(name='user admin controling')

user_control.index_title = 'Shoes Shop User'
user_control.site_header = 'The Shoes User'
user_control.site_title = 'Title Shoes Shop User'

class AdminUser(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('phone', 'is_admin', 'is_active')
    list_filter = ('is_admin','phone')

    readonly_fields = ['is_admin','phone', 'is_superuser', 'user_permissions', 'groups']    
    fieldsets = ( #this is for form
            ('اطلاعات شخصی',{'fields':('phone','password')}),
            ('دسترسی',{'fields':('is_active','is_admin','is_superuser')}),
            ('محدودیت  ها',{'fields':('groups', 'user_permissions')}),
        )
    add_fieldsets = (#this is for add_form 
        (' اطلاعات شخصی',{'fields':('phone','password', 'password_confierm')}),
    )


    def can_edit_password(self, logged_user, chosen_user=None):
        if logged_user and logged_user.is_superuser:
            return True
        

    search_field = ('phone',)
    ordering = ('phone',)

user_control.register(Group)
user_control.register(get_user_model(),AdminUser)

