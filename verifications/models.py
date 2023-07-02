from django.db import models
from datetime import datetime

from django.db.utils import IntegrityError
from rest_framework import serializers

# Create your models here.

class Customer(models.Model):
    PENDING = 'PENDING'
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'
    INVITED = 'INVITED'

    STATUS = [
        (PENDING, 'Pending'),
        (APPROVE, 'Approve'), 
        (REJECT, 'Reject'), 
        (INVITED, 'INVITED')
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
    photo_id = models.ImageField(max_length=500, null=True, blank=True)
    dob = models.CharField(max_length=15, null=True, blank=True)
    gender = models.CharField(choices=GENDER, max_length=20, default=MALE)
    verification_country = models.CharField(max_length=100, null=True, blank=True)

    # okra customer id field 
    customer_id = models.CharField(max_length=200, null=True, unique=True)

    # status field 
    status = models.CharField(max_length=20, choices=STATUS, default=INVITED)

    # invitation fields 
    is_invited = models.BooleanField(default=False, null=False)

    # time the user grant us access to their account and when last the account was updated 
    created_at = models.DateTimeField(null=True, default=datetime.utcnow)
    
    # bank name
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_id = models.CharField(max_length=100, null=True, blank=True)
    
    available_balance = models.CharField(max_length=100, null=True, blank=True)
    complete_onboarding = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"BVN number ---> {self.phone}"

    def update(self, params):
        for attr, value in params.items():
            setattr(self, attr, value)
            
        self.save()
        
    def fill_customer_detail(self, payload):
        data = {}
        identity = payload.get('identity')
        data['bank_name'] = payload.get('bankName')
        data['bank_id'] = payload.get('bankId')
        data['customer_id'] = payload.get('customerId')
        data['last_name'] = identity.get('lastname')
        data['first_name'] = identity.get('firstname')
        data['middle_name'] = identity.get('middlename', '')
        data['is_verify'] = True
        data['bvn'] = identity.get('bvn')
        
        
        if identity.get('phone'):
            data['phone'] = identity.get('phone')[0]
        if payload.get('customerEmail'):
            data['email'] = payload.get('customerEmail')[0]
            
        if identity.get('address'):
            data['address'] = identity.get('address')[0]
        if identity.get('photo_id'):
            data['photo_id'] = identity.get('photo_id')[0].get('url')
            
        data['dob'] = identity.get('dob')
        data['verification_country'] = identity.get('verification_country')
        data['created_at'] = datetime.utcnow()
        data['gender'] = identity.get('gender')
        data['status'] = self.PENDING
        data['marital_status'] = identity.get('marital_status')
        
            
        try:
            self.update(data)
        except IntegrityError:
            message = 'Customer id already exist'
            raise serializers.ValidationError(message)         
        
    def fill_account_balance(self, payload):
        self.available_balance = payload.get('balance').get('available_balance')
        self.save()
        
        

class CustomerIncomeData(models.Model):
    """Table showing the customer income data"""
    confidence = models.FloatField(max_length=10, null=True)
    source = models.CharField(max_length=100, null=False)
    monthly_amount = models.CharField(max_length=100, null=True)
    average_monthly_income = models.FloatField(null=True)
    account_age_months = models.IntegerField(null=True)
    last_two_years_income = models.FloatField(null=True)
    last_year_income = models.FloatField(null=True)
    
    customer = models.OneToOneField(Customer, on_delete=models.PROTECT, null=False)


    def __str__(self) -> str:
        return f"{self.customer.first_name} {self.customer.last_name} has {self.confidence} confidence level"
    
    @classmethod
    def fill_income_data(cls, payload, customer):
        income = payload.get('income')
        streams = income.get('streams')
        summary = income.get('summary')
        confidence = income.get('confidence')
        monthly_amount = streams[0].get('monthly_amount')
        source = streams[0].get('details').get('source').get('name')
        account_age_months = summary.get('account_age_months')
        average_monthly_income = summary.get('average_monthly_income')
        last_two_years_income = summary.get('last_two_years_income')
        last_year_income = summary.get('last_year_income')
                
        customer_income = CustomerIncomeData.objects.create(
                                        confidence=confidence, 
                                        monthly_amount=monthly_amount,
                                        source=source,
                                        average_monthly_income=average_monthly_income,
                                        account_age_months=account_age_months,
                                        last_two_years_income=last_two_years_income, 
                                        last_year_income=last_year_income,
                                        customer=customer
                                        )
        customer.complete_onboarding = True 
        customer.save()