from django.contrib import admin

# Register your models here.

class ShopAdmin(admin.AdminSite):
    site_header = 'Shop Admin'
    login_template = 'shop/admin/login.html'

shop_admin = ShopAdmin(name='shop admin',)