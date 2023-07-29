import json
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q


from .serializers import (CustomerListSerializer, SendCustomerInviteSerializer,
                        CustomerSerializer, WaitListSerializer, CustomerUpdateSerializer, 
                        OnBoardingSerializer, RiskThresholdSerializer)
from .models import Customer, RiskThreshold
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
            send_link_message(phone)
            return Response(data=f'Reminder Invite link sent to {phone}', status=status.HTTP_201_CREATED)
                   
        if serializer.is_valid():            
            number = serializer.validated_data.get("phone")
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
    
    
# class OkraWebhookEventNotification(APIView):
#     def get(self, request, format=None):
#         return Response(status=status.HTTP_200_OK)

#     def post(self, request, format=None):
#         try:
#             payload = json.loads(request.body.decode('utf-8'))
#             callback_type = payload.get('callback_type')

#             if callback_type in (constants.AUTH, constants.TRANSACTIONS, constants.ACCOUNTS):
#                 return Response(status=status.HTTP_200_OK)

#             identity = payload.get('identity')
#             customer_bvn = payload.get('customerBvn')
#             customer_id = payload.get('customerId')

#             if identity:
#                 phone = identity.get('phone')[0]
#                 customer, created = Customer.objects.get_or_create(phone=phone, defaults={'bvn': customer_bvn, 'customer_id': customer_id})
#                 if created:
#                     # New customer created, perform additional setup if needed
#                     pass
#             else:
#                 customer = Customer.objects.filter(Q(bvn=customer_bvn) | Q(customer_id=customer_id)).first()

#             print(customer)
#             if customer:
#                 if customer.complete_onboarding:
#                     return Response({'exception': 'Customer already onboarded. Contact admin to request a new link.'}, 
#                                     status=status.HTTP_201_CREATED)

#                 if callback_type == constants.IDENTITY:
#                     data = fetch_identity(customer.customer_id)
#                     fetch_income(customer.customer_id, customer)
#                     payload = fetch_balance(customer.customer_id)
#                     customer.fill_account_balance(payload)
#                     customer.first_name = data.get('first_name')
#                     customer.last_name = data.get('last_name')
#                     customer.dob = data.get('dob')
#                     customer.gender = data.get('gender')
#                     customer.email = data.get('email')
#                     customer.address = data.get('address')
#                     customer.phone = phone  # Set the phone number if not present in the customer object
#                     customer.save()
#                 return Response(status=status.HTTP_201_CREATED)

#             return Response({'exception': 'Customer does not exist'}, status=status.HTTP_404_NOT_FOUND)

#         except json.JSONDecodeError:
#             return Response({'exception': 'Invalid JSON payload'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'exception': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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
    

class RiskThresholdView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer
    
    
class UdateRiskThresholdView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer