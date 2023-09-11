from celery import shared_task
from verifications.utils import send_bank_authorization_link

from app.celery import app

@shared_task
def send_link_message(phone_number):
    message = """
    As Salam Alaikum, you've requested to perform the KYC by AlQasswa to issue your Umrah Visa. We need to verify:
    1. Employment Status
    2. Income Status
    3. Account Balance

    Please complete the form below by clicking on the link below.

    https://app.creditchek.africa/customer/onboarding?type=short&appId=5293878414&appLink=eFd1ZNdJda&app_id=64aac9d453a97b63508946e7&status=true
    
    
    Thanks  
    """
    
    send_bank_authorization_link(phone_number, message)
    return 'Done'
