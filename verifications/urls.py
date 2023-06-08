from django.urls import path
from .views import (CustomerDetailView, SMSLinkView, OkraWebhookEventNotification, 
                    CustomerListView, CustomerUpdateView, WaitListView)

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer_list_view'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail_view'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer_update_view'),
    path('user/sms/', SMSLinkView.as_view(), name='customer_detail_view'), 
    path('notifications/', OkraWebhookEventNotification.as_view(), name='notification_view'),
    path('waitlist/', WaitListView.as_view(), name='wait_list_view') 
]