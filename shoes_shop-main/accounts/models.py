from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class  MyUserManager(BaseUserManager):
    def create_user(self, phone, password):
        if not phone:
            raise ValueError("لطفا شماره تلفن خود را وارد کنید")
        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, phone, password):
        user = self.create_user(phone=phone, password=password)
        user.is_admin=True
        user.save(using=self._db)
        return user
 
class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True, verbose_name="شماره تماس شما") # validators should be a list
    

    is_active = models.BooleanField(default=True, verbose_name="user is active")
    is_admin = models.BooleanField(default=False, verbose_name="user is admin")
    
    objects=MyUserManager()
    USERNAME_FIELD = 'phone'
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self) -> str:
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
        
    @property
    def is_staff(self):
        return self.is_admin
