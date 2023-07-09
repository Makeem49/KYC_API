import json
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q


from .serializers import (CustomerListSerializer, SendCustomerInviteSerializer,
                        CustomerSerializer, WaitListSerializer, CustomerUpdateSerializer)
from .models import Customer, CustomerIncomeData
from .tasks import send_link_message
from . import constants

from .utils import fetch_balance, fetch_identity, fetch_income


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
    
    
class OkraWebhookEventNotification(APIView):
    def get(self, request, format=None):
        return Response(status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            callback_type = payload.get('callback_type')

            if callback_type in (constants.AUTH, constants.TRANSACTIONS, constants.ACCOUNTS):
                return Response(status=status.HTTP_200_OK)

            identity = payload.get('identity')
            customer_bvn = payload.get('customerBvn')
            customer_id = payload.get('customerId')

            if identity:
                phone = identity.get('phone')[0]
                customer, created = Customer.objects.get_or_create(phone=phone, defaults={'bvn': customer_bvn, 'customer_id': customer_id})
                if created:
                    # New customer created, perform additional setup if needed
                    pass
            else:
                customer = Customer.objects.filter(Q(bvn=customer_bvn) | Q(customer_id=customer_id)).first()

            print(customer)
            if customer:
                if customer.complete_onboarding:
                    return Response({'exception': 'Customer already onboarded. Contact admin to request a new link.'}, 
                                    status=status.HTTP_201_CREATED)

                if callback_type == constants.IDENTITY:
                    data = fetch_identity(customer.customer_id)
                    print(data)
                    customer.first_name = data.get('first_name')
                    customer.last_name = data.get('last_name')
                    customer.dob = data.get('dob')
                    customer.gender = data.get('gender')
                    customer.email = data.get('email')
                    customer.address = data.get('address')
                    customer.phone = phone  # Set the phone number if not present in the customer object
                    customer.save()
                elif callback_type == constants.BALANCE:
                    payload = fetch_balance(customer.customer_id)
                    # customer.fill_account_balance(payload)
                elif callback_type == constants.INCOME:
                    fetch_income(customer.customer_id, customer)
                    # CustomerIncomeData.fill_income_data(payload, customer)
                return Response(status=status.HTTP_201_CREATED)

            return Response({'exception': 'Customer does not exist'}, status=status.HTTP_404_NOT_FOUND)

        except json.JSONDecodeError:
            return Response({'exception': 'Invalid JSON payload'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'exception': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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
    
    
    
class FetchBalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = ''
    
    def post(self, request, format=None):
        payload = json.loads(request.body.decode('utf-8'))
        phone = payload.get('phone')
        id = payload.get('id')
        
        # get customer from db
        customer = Customer.objects.filter(phone=phone).first()
              
        # fetch balance base on customer db 
        
    
class FetchIncomeListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = ''
