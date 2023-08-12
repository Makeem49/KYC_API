from django.db import models
from datetime import datetime

from django.db.utils import IntegrityError
from rest_framework import serializers
from django.

# Create your models here.

class RiskThreshold(models.Model):
    
    # countries options 
    NIGERIA = 'NIGERIA'
    INDIA = 'INDIA'
    INDONESIA = 'INDONESIA'
    
    
    COUNTRIES = [
        (NIGERIA, 'Pending'),
        (INDIA, 'Approve'), 
        (INDONESIA, 'Reject'), 
    ]
    
    account_balance = models.DecimalField(max_digits=16, decimal_places=2)
    employed = models.BooleanField(null=False)
    minimum_monthly_salary = models.DecimalField(max_digits=16, decimal_places=2)
    country = models.CharField(max_length=10, choices=COUNTRIES, null=False, unique=True)
    
    
    def __str__(self) -> str:
        return f"threshold id {self.id}"
    
    def update(self, params):
        for attr, value in params.items():
            setattr(self, attr, value)   
        self.save()
    
    
class AppID(models.Model):
    app_id = models.CharField(max_length=200, null=False)
    
    def __str__(self) -> str:
        return self.app_id


class Customer(models.Model):
    # status options
    PENDING = 'PENDING'
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'
    INVITED = 'INVITED'
    
    # residential options 
    OWNED = 'OWNED'
    RENT = 'RENT'
    INHERITED = 'INHERITED'
    
    #choices
    STATUS = [
        (PENDING, 'Pending'),
        (APPROVE, 'Approve'), 
        (REJECT, 'Reject'), 
        (INVITED, 'INVITED')
    ]
    
    #choices
    RESIDENTIAL_TYPE = [
        (OWNED , 'OWNED'),
        (RENT , 'RENT'),
        (INHERITED , 'INHERITED')
    ]
    
    MALE = "M"
    FEMALE = "F"
    GENDER = [(MALE, "Male"), (FEMALE, "Female")]


    # bvn fields 
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    is_verify = models.BooleanField(default=False, null=False, blank=False)
    bvn = models.CharField(null=True, blank=True, max_length=11, unique=True)
    phone = models.CharField(max_length=26, blank=False, null=False, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    photo_id = models.CharField(max_length=500, null=True, blank=True)
    dob = models.CharField(max_length=15, null=True, blank=True)
    gender = models.CharField(choices=GENDER, max_length=20, default=MALE)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    # okra customer id field 
    borrower_id = models.CharField(max_length=200, null=True)

    # status field 
    status = models.CharField(max_length=20, choices=STATUS, default=INVITED)

    # invitation fields 
    is_invited = models.BooleanField(default=False, null=False)

    # time the user grant us access to their account and when last the account was updated 
    created_at = models.DateTimeField(null=True, default=datetime.utcnow)
    updated_at = models.DateTimeField(null=True, default=datetime.utcnow)
    
    residential_address = models.CharField(max_length=200, null=False)
    residential_type = models.CharField(max_length=20, choices=RESIDENTIAL_TYPE, null=False)
    
    
    # credit check 
    lga_origin = models.CharField(max_length=100, null=True)
    lga_residence = models.CharField(max_length=100, null=True)
    nin = models.CharField(max_length=15, null=True)
    watchlist = models.CharField(max_length=20, null=False, default='No')
    
    # RELATIONSHIP
    risk_country_threshold = models.ForeignKey(RiskThreshold, on_delete=models.PROTECT, null=False)
    app_id = models.ForeignKey(AppID, on_delete=models.PROTECT, null=True)
    
    
    def __str__(self):
        return f"BVN number ---> {self.bvn}"

    def update(self, params):
        for attr, value in params.items():
            setattr(self, attr, value)   
        self.save()
            
            
class CustomerIncomeData(models.Model):
    """Table showing the customer income data"""
    average_monthly_income = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    total_money_received = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    total_money_spent = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    eligibility_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    debt_to_income = models.CharField(max_length=20, null=True)
    debt_to_income_reason = models.CharField(max_length=200, null=True)
    institution_name = models.CharField(max_length=30, null=False)
    bank_code = models.IntegerField(null=True)
    type = models.CharField(max_length=100, null=True)
    balance = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    account_number = models.CharField(max_length=14, null=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)

    def __str__(self) -> str:
        return f"{self.customer.first_name} {self.customer.last_name} has {self.balance} confidence level"
   