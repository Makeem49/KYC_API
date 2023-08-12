import json
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
import django.http


from .serializers import (CustomerListSerializer, SendCustomerInviteSerializer,
                        CustomerSerializer, WaitListSerializer, CustomerUpdateSerializer, 
                        VerifyUserViewSerializer, RiskThresholdSerializer, OnBoardingSerializer, 
                        RiskThresholdUpdateSerializer)
from .models import Customer, RiskThreshold
from .tasks import send_link_message
from . import constants
from .utils import RetrieveUserIncomeData


class SMSLinkView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = SendCustomerInviteSerializer(data=request.data)
        phone = serializer.initial_data.get('phone')
        bvn = serializer.initial_data.get('bvn')
        customer = Customer.objects.filter(phone=phone, bvn=bvn).first()
        if customer:   
            send_link_message(phone)
            return Response(data=f'Reminder Invite link sent to {phone}', status=status.HTTP_201_CREATED)
                   
        if serializer.is_valid():            
            number = serializer.validated_data.get("phone")
            bvn = serializer.validated_data.get('bvn', None)
            nationality = serializer.validated_data.get('nationality')
            
            if nationality == constants.NIGERIA and not bvn:
                'if country is Nigeria and bvn is not given return a error response requesting for bvn'               
                return Response({'error' : 'BVN number is required for users in Nigeria'}, status=status.HTTP_406_NOT_ACCEPTABLE) 
            
            if len(bvn) != constants.BVN_LENGTH:
                'if bvn lenght is not 11 numbers, return error'
                return Response({'error' : 'BVN number is 11 character long.'}, status=status.HTTP_406_NOT_ACCEPTABLE)             
            
            risk_country_threshold = RiskThreshold.objects.filter(country=nationality).first()
            # This will be run is background using celery
            send_link_message(number)
            serializer.validated_data['risk_country_threshold'] = risk_country_threshold
            serializer.validated_data["is_invited"] = True
            serializer.validated_data['status'] = constants.INVITED
            serializer.save()
            return Response(data=f'Invite link send to {number}', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'pk'


class CustomerListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerListSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'pk'

    def get_queryset(self):
        customers = Customer.objects.exclude(customerincomedata__pk__isnull=True)
        param = self.request.query_params.get('status')
        if param:
            customers = customers.exclude(customerincomedata__pk__isnull=True).filter(status=param)
        return customers
    
    
    
class CustomerOnBoard_view(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OnBoardingSerializer
    pagination_class = LimitOffsetPagination
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
class EventNotification(APIView):
    def post(self, request, format=None):
        request_data = request.data
        event = request_data.get('event')
        data = request_data.get('data')
        print(request_data, 'request data')
        bvn = data.get('bvn')
        borrower_id = data.get('borrowerId') 

        customer = Customer.objects.filter(Q(bvn=bvn) | Q(borrower_id=borrower_id)).first()
        if event == constants.PDF_UPLOAD:
            print(borrower_id, 'borrower id')
            customer.borrower_id = borrower_id
            customer.save()
            print(customer.borrower_id, 'saved borrower id')
            if customer:
                user = RetrieveUserIncomeData(bvn)
                resp = user.send_identity_request('identity/verifyData')   
            try:
                data = resp.json()                    
                user_data = user.extract_bvn_data(data)
                user.save_identity_to_db(user_data, customer)
                print('saved')
            except Exception as e:
                print(f'An error occured {e}')
                raise Exception(e)
            
            data = user.send_income_request('income/insight-data', borrower_id)
            try:
                data = data.json()
                user_income = user.extract_income_data(data)
                user = user.save_income_to_db(user_income, customer)
                print('income saved')
            except Exception as e:
                print(f'Error occur in income {e}')                   
        return Response(status=status.HTTP_200_OK)
    

class CustomerUpdateView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        instance_come = instance.customerincomedata_set.all()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if instance_come:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response({'error' : 'User can not be update because he/she is still on waitlist'}, status=status.HTTP_400_BAD_REQUEST)
        
class WaitListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = WaitListSerializer
    
    def get_queryset(self):
        customers = Customer.objects.filter(status='INVITED')
        return customers
        
    
class RiskThresholdView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer
    
    def post(self, request, *args, **kwargs):
        data = request.data
        countries = data.get('countries')

        if countries:
            for country_data in countries:
                serializer = self.serializer_class(data=country_data)
                if serializer.is_valid(raise_exception=True):
                    country = serializer.validated_data.get('country')
                            
                instance, created = RiskThreshold.objects.update_or_create(
                    country=country,
                    defaults=serializer.validated_data
                )
                
                if not created:
                    updated_serializer = self.serializer_class(instance, data=country_data)
                    updated_serializer.is_valid(raise_exception=True)
                    instance = updated_serializer.save()
            
            countries = RiskThreshold.objects.all()
            serializer = RiskThresholdSerializer(countries, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error' : 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self, request, *args, **kwargs):
        countries = RiskThreshold.objects.all()
        serializer = RiskThresholdSerializer(countries, many=True)
        return Response(serializer.data)
    