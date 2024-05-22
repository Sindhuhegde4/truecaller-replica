from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    name = models.CharField(max_length=50, null=False)
    phone_number = models.BigIntegerField(null=False)
    email = models.EmailField(max_length=50, null=True)
    spam = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class UserMapContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.user.username}, {self.contact.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    phone_number = models.BigIntegerField(null=False, unique=True)
    email = models.EmailField(max_length=50, null=True)
    spam = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class SpamPhoneNumber(models.Model):
    phone_number = models.BigIntegerField(null=False, unique=True)
    spam = models.BooleanField(default=True)

    def __str__(self):
        return str(self.phone_number)
