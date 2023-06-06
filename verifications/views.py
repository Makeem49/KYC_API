import json
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (CustomerListSerializer, SendCustomerInviteSerializer,
                        CustomerSerializer, WaitListSerializer, CustomerUpdateSerializer)
from .models import Customer, CustomerIncomeData
from .tasks import send_link_message
from . import constants


class SMSLinkView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = SendCustomerInviteSerializer(data=request.data)
        phone = serializer.initial_data.get('phone')
        customer = Customer.objects.filter(phone=phone).first()
        if customer:   
            if not customer.complete_onboarding:
                send_link_message(phone)
                return Response(data=f'Reminder Invite link sent to {phone}', status=status.HTTP_201_CREATED)
            
            if customer.complete_onboarding:
                return Response({'exception' :'Customer already onboarded, contact admin to request for a new link.'} , status=status.HTTP_409_CONFLICT) 
        
        if serializer.is_valid():            
            number = serializer.validated_data.get("phone")
            # This will be run is background using celery
            send_link_message(number)
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
    

class OkraEventNotification(APIView):

    def post(self, request, format=None):
        request_data = request.body
        decode_data = request_data.decode('utf-8')
        payload = json.loads(decode_data)
        callback_type = payload.get('callback_type')
        data = {}
        identity = payload.get('identity')
        email = payload.get('customerEmail')[0]
        if identity:
            phone = identity.get('phone')[0]
            customer = Customer.objects.filter(phone=phone).first()
        else:
            customer = Customer.objects.filter(email=email).first()
        
        if customer.complete_onboarding:
            return Response({'exception' :'Customer already onboarded, contact admin to request for a new link.'} , status=status.HTTP_409_CONFLICT)

        if customer:
            if callback_type == constants.IDENTITY:
                customer.fill_customer_detail(payload, data, customer)
            elif callback_type == constants.BALANCE:
                customer.fill_account_balance(payload, customer)
            elif callback_type == constants.INCOME:
                CustomerIncomeData.fill_income_data(payload, customer)
        
            return Response(status=status.HTTP_201_CREATED)
        return Response({'exception': 'Phone number does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    
class CustomerUpdateView(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerUpdateSerializer
    
    
class WaitListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = WaitListSerializer
    
    