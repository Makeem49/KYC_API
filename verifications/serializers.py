from rest_framework import serializers, status
from rest_framework.response import Response
from django.conf import settings

from .models import Customer, AppID, RiskThreshold

class WaitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'phone', 'status', 'created_at', 'nationality']


    
class SendCustomerInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone', 'nationality', 'bvn']
        
    def to_internal_value(self, data):
        # Convert the 'country' field to uppercase if it exists in the data
        if 'nationality' in data:
            data['nationality'] = data['nationality'].upper()
        return super().to_internal_value(data)
        
    # def create(self, validated_data):
    #     number = self.validated_data.get('phone')
    #     bvn = self.validated_data.get('bvn')
    #     customer = Customer.objects.filter(phone=number, bvn=bvn).first()
    #     if customer:
    #         if customer.complete_onboarding:
    #             return Response(data=f'Invite link send to {number}', status=status.HTTP_201_CREATED)
    #     return super().create(validated_data)
    


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields  = ['first_name', 'last_name', 'middle_name', 'is_verify', 'bvn', 
                   'phone', 'email', 'address', 'marital_status', 'photo_id', 
                   'dob', 'gender', 'nationality', 'borrower_id', 'status', 
                   'created_at', 'lga_origin', 'lga_residence', 'nin', 'watchlist',
                   ]
        
        
class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields  = ['status']
        

class CustomerListSerializer(serializers.ModelSerializer):  
    risk_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id','name', 'phone', 'verification_country', 'status', 'risk_level']
        
        
    def get_risk_level(self, obj):
        """Get all the account associated with the user, and add everything together and divide by 
        the number of user account to get a true average for teh user."""
        
        customer_income = obj.customerincomedata_set.all()
        country_risk_balance = obj.risk_country_threshold.account_balance
        
        total_income = 0
        for income in customer_income:
            total_income += income.average_monthly_income
            
        total_income = total_income/len(customer_income)
            
        risk_level = 'pass'
        if total_income < country_risk_balance:
            risk_level = 'high'
        return risk_level


class OnBoardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name','middle_name', 'bvn', 'app_id', 'country', 'residential_type', 
                  'residential_address', 'email', 'phone']
        
        
    def create(self, validated_data):
        bvn = self.validated_data.get('bvn')
        customer = Customer.objects.filter(bvn=bvn).first()
        if customer:
                return Response({'exception' :'Customer with bvn {bvn} already onboarded.'} , status=status.HTTP_409_CONFLICT) 
        return super().create(validated_data)
    

              
class RiskThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskThreshold
        fields = '__all__'
        
    def to_internal_value(self, data):
        # Convert the 'country' field to uppercase if it exists in the data
        if 'country' in data:
            data['country'] = data['country'].upper()
        return super().to_internal_value(data)
    
    
class VerifyUserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['bvn']
        
