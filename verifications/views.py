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
                        VerifyUserViewSerializer, RiskThresholdSerializer, OnBoardingSerializer)
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
            bvn = serializer.validated_data.get('bvn')
            nationality = serializer.validated_data.get('nationality')
            
            risk_country_threshold = RiskThreshold.objects.filter(country=nationality).first()
            # This will be run is background using celery
            send_link_message(number)
            serializer.validated_data['risk_country_threshold'] = risk_country_threshold
            serializer.validated_data["is_invited"] = True
            serializer.validated_data['status'] = constants.INVITED
            serializer.save()
            return Response(data=f'Invite link send to {number}', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class VerifyUserView(APIView):
#     """This endpoint send a post request to get the user information from the thrid party API we integrated."""
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         serializer = VerifyUserViewSerializer(data=request.data)
#         bvn = serializer.validated_data.get('bvn')
        
#         try:
#             customer = Customer.objects.get(bvn=bvn)
#         except:
#             return Response({'exception': 'User not found. User bvn need to be register, before he/she identity can ba available'}, status=status.HTTP_404_NOT_FOUND)
        

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
        bvn = data.get('bvn')
        borrower_id = data.get('borrowerId') 

        customer = Customer.objects.filter(bvn=bvn).first()

        if event == constants.PDF_UPLOAD:
            if customer:
                user = RetrieveUserIncomeData(bvn)
                data = user.send_identity_request('identity/verifyData')                
                try:
                    data = data.json()
                    user_data = user.extract_bvn_data(data)
                    user.save_identity_to_db(user_data)
                except Exception as e:
                    print(f'An error occured {e}')
            
        elif event == constants.INCOME_TRANSACTION:
            if customer:
                user = RetrieveUserIncomeData(bvn)
                data = user.send_income_request('income/insight-data', borrower_id)
        
                try:
                    data = data.json()
                    user_income = user.extract_income_data(data)
                    user = user.save_income_to_db(user_income)
                except:
                    print('Error occur in income')                  
        return Response(status=status.HTTP_200_OK)

class CustomerUpdateView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerUpdateSerializer
        
class WaitListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = WaitListSerializer
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
class RiskThresholdView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer
    
    def post(self, request, *args, **kwargs):
        data = request.data
        
        for risk_country in data:
            serializer = self.serializer_class(risk_country)
            if serializer.is_valid():
                data = serializer.save()                    
        return Response(data='', status=status.HTTP_201_CREATED)
    
    
    

class UdateRiskThresholdView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer
    