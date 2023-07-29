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
        fields = ['phone', 'nationality']
        
    def to_internal_value(self, data):
        # Convert the 'country' field to uppercase if it exists in the data
        if 'nationality' in data:
            data['nationality'] = data['nationality'].upper()
        return super().to_internal_value(data)
        
    def create(self, validated_data):
        number = self.validated_data.get('phone')
        customer = Customer.objects.filter(phone=number).first()
        if customer:
            if customer.complete_onboarding:
                return Response(data=f'Invite link send to {number}', status=status.HTTP_201_CREATED)
                
            # if customer.complete_onboarding:
            #     return Response({'exception' :'Customer already onboarded, contact admin to request for a new link.'} , status=status.HTTP_409_CONFLICT) 
                
        return super().create(validated_data)
    


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields  = '__all__'
        
        
class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields  = ['status']
        

class CustomerListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    confidence = serializers.SerializerMethodField(read_only=True)
    source = serializers.SerializerMethodField(read_only=True)
    monthly_amount = serializers.SerializerMethodField(read_only=True)
    account_age_months = serializers.SerializerMethodField(read_only=True)
    average_monthly_income = serializers.SerializerMethodField(read_only=True)
    last_two_years_income = serializers.SerializerMethodField(read_only=True)
    last_year_income = serializers.SerializerMethodField(read_only=True)
    last_year_income = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = Customer
        fields = ['id','name', 'verification_country', 'available_balance', 'status', 
                  'last_year_income', 'last_year_income', 'average_monthly_income', 'account_age_months', 
                  'monthly_amount', 'source', 'last_two_years_income', 'confidence']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_source(self, obj):
        return obj.customerincomedata.source
    
    def get_confidence(self, obj):
        return obj.customerincomedata.confidence
    
    def get_monthly_amount(self, obj):
        return obj.customerincomedata.monthly_amount
    
    def get_average_monthly_income(self, obj):
        return obj.customerincomedata.average_monthly_income
    
    def get_account_age_months(self, obj):
        return obj.customerincomedata.account_age_months
    
    def get_last_two_years_income(self, obj):
        return obj.customerincomedata.last_two_years_income
    
    def get_last_year_income(self, obj):
        return obj.customerincomedata.last_year_income



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
    