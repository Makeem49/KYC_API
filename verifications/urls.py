from django.urls import path
from .views import (CustomerDetailView, SMSLinkView,  
                    CustomerListView, CustomerUpdateView, WaitListView, RiskThresholdView, UdateRiskThresholdView)

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer_list_view'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail_view'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer_update_view'),
    path('user/sms/', SMSLinkView.as_view(), name='customer_detail_view'), 
    path('waitlist/', WaitListView.as_view(), name='wait_list_view'),
    path('risk_threshold/', RiskThresholdView.as_view(), name='risk_threshold'),
    path('risk_threshold_update/<int:pk>', UdateRiskThresholdView.as_view(), name='risk_threshold_update'),
]