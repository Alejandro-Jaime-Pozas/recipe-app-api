"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# this to manage how the User model will work
class UserManager(BaseUserManager):
    """Manager for users."""

    # this is a custom method not built in to create a new user
    def create_user(self, email, password=None, **extra_fields):  # pwd set to None if there's need to create an unusable user; extra_fields is for any kwargs we need to pass in
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')  # do not allow empty email field
        user = self.model(email=self.normalize_email(email), **extra_fields)  # this to access the model that is associated with this manager; requires that the email is normalized
        user.set_password(password)  # set_password is django built-in method to encrypt the user's input password
        user.save(using=self._db)  # to save to the db session; 'using' used to specify which db, can input multiple dbs; self._db referring to this UserManager's db

        return user

    def create_superuser(self, email, password):
        """Create, save and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True  # python built-in
        user.is_superuser = True  # python built-in
        user.save(using=self._db)

        return user


# User is based from abstractbaseuser parent class which contains the functionality for the auth system (but not any fields) and permissionsmixin which contains functionality for permissions and fields req in those permissions
class User(AbstractBaseUser, PermissionsMixin):  # don't forget to add this model to admin.py
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # is_active is django field
    is_staff = models.BooleanField(default=False)  # is_staff is django field to allow django admin access; default it's best to give the least permissions

    objects = UserManager()  # this to assign the UserManager manager to this User model..when querying the db, this is what the command for >>> User.objects.all() is referring to

    USERNAME_FIELD = 'email'  # this to switch default user authentication field from username to email


class Recipe(models.Model):  # don't forget to add this model to admin.py
    """Recipe object."""
    # set relationship to the user model
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # use default user model (we've modified)
        on_delete=models.CASCADE,  # if the related object is deleted (user) also delete all recipes..
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # text fields hold more content and multiple lines vs CharField
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title