from djongo import models
from django.db.models.signals import post_save
from django.utils.timezone import datetime
# Create your models here.

class Account(models.Model):
    First_name=models.CharField(max_length=50)
    Last_name=models.CharField(max_length=50)
    Username=models.CharField(max_length=50,unique=True)
    Emailaddress=models.EmailField(max_length=50,unique=True)
    Password=models.CharField(max_length=50)
    created_on=models.DateTimeField(auto_now_add=True,editable=False)

class AccountDetail(models.Model):
    account=models.OneToOneField(Account,on_delete=models.CASCADE)
    reset=models.CharField(max_length=200)
    verify=models.CharField(max_length=200)
    reset_time=models.DateTimeField(default=datetime.now())
    verify_time=models.DateTimeField(default=datetime.now())
    verify_account=models.BooleanField(default=False)
    def update_account(sender,**kwargs):
        AccountDetail.objects.create(account=kwargs['instance'])
    post_save.connect(update_account,sender=Account)

class Session(models.Model):
    user_id=models.PositiveIntegerField(default=0)
    session_key=models.CharField(max_length=50)
    session_id=models.CharField(max_length=100)