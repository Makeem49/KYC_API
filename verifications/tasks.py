from celery import shared_task
from verifications.utils import send_bank_authorization_link

from app.celery import app

@shared_task
def send_link_message(phone_number):
    message = """
    Hello from simbard HQ, Kindly authorize us your account information by clicking on the below link. 
    Click the below link, fill the form with correct information. 

    https://app.creditchek.africa/customer/onboarding?type=short&appId=5293878414&appLink=eFd1ZNdJda&app_id=64aac9d453a97b63508946e7&status=true
    
    Please use your salary account. 
    
    Thanks  
    """
    
    send_bank_authorization_link(phone_number, message)
    return 'Done'
