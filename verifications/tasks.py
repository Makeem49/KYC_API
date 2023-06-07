from celery import shared_task
from verifications.utils import send_bank_authorization_link

from app.celery import app

@shared_task
def send_link_message(phone_number):
    message = """
    Hello from simbard HQ, Kindly authorize us your account information by clicking on the below link. 
    https://app.okra.ng/izAhzrV8y
    
    Thanks  
    """
    
    send_bank_authorization_link(phone_number, message)
    return 'Done'
