from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.core.validators import MinLengthValidator



class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError('The Email must be set')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):

        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(
            email,
            password=password,
        )

        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.is_active = True

        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True, max_length=255)
    phone = models.CharField(null=True, blank=True, max_length=10, validators=[MinLengthValidator(10)])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = []

    objects = UserManager()
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True