import requests
from verifications.models import CustomerIncomeData
from okra_py.balance import OkraBalance
from okra_py.income import OkraIncome
from okra_py.identity import OkraIdentify

okra_balance_api = OkraBalance('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NDZiMDcxY2RmYzkyYTI5NWYxOWVjODkiLCJpYXQiOjE2ODQ3NjQ3Mzd9.s44IlyX1RjlUxmmGBjNH47y9YKh_yWUsdpsblTMPz34')
okra_income_api = OkraIncome('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NDZiMDcxY2RmYzkyYTI5NWYxOWVjODkiLCJpYXQiOjE2ODQ3NjQ3Mzd9.s44IlyX1RjlUxmmGBjNH47y9YKh_yWUsdpsblTMPz34')
okra_identity_api = OkraIdentify('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NDZiMDcxY2RmYzkyYTI5NWYxOWVjODkiLCJpYXQiOjE2ODQ3NjQ3Mzd9.s44IlyX1RjlUxmmGBjNH47y9YKh_yWUsdpsblTMPz34')

# Your Account SID and Auth Token from console.twilio.com
def send_bank_authorization_link(number,message_body):
    
    url = "https://api.ng.termii.com/api/sms/send"
    payload = {
            "to": number,
            "from": 'Simbard',
            "sms": message_body,
            "type": "plain",
            "channel": "generic",
            "api_key": "TLNTkMa8aHkMzrf0jte0uBPVAV5ksh0Qu74FrjpBLkt935suSQvONZPTCMHSuQ",
    }

    headers = {
    'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json=payload)
    
    return True


def fetch_balance(customer_id):
    resp = okra_balance_api.get_by_customer(customer_id=customer_id, limit=2)
    data = resp.json()
    return data
	
 
def fetch_identity(customer_id):
    resp = okra_identity_api.get_by_customer(customer_id)
    obj = resp.json()
    print(obj, '00000000000000000')
    data = obj.get('data')
    user = {}
    
    if data:
        identity = data.get('identity')
        if identity:
            data = identity[0]
            user['dob'] = data.get('dob')
            user['bvn'] = data.get('bvn')
            user['gender'] = data.get('gender').upper()
            
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            
            if firstname and lastname:
                user['first_name'] = data.get('firstname')
                user['last_name'] = data.get('lastname')
                user['middle_name'] = data.get('middlename')
                
            else:
                name = data.get('customer').get('name').split(' ')
                user['first_name'] = name[0]
                user['last_name'] = name[1]
                
            user['phone'] = data.get('phone')[0]
            user['email'] = data.get('email')
            user['address'] = data.get('address')[0]
   
    return user 
        
 
def fetch_income(customer_id, customer):
    resp = okra_income_api.get_by_customer(customer_id=customer_id)
    obj = resp.json()
    data = obj.get('data')
    income = data.get('income')
    print(income)

    if income:
        user_income_data = income[0]
        confidence = user_income_data.get('confidence').strip('%')
        last_two_years_income = user_income_data.get('last_two_years_income')
        last_year_income = user_income_data.get('last_year_income')
        
        streams = user_income_data.get('streams')
        if streams:
            stream = streams[0]
            monthly_amount = stream.get('monthly_income')
            source = stream.get('income_type')
            average_monthly_income = stream.get('avg_monthly_income')
            
            
        customer_income = CustomerIncomeData.objects.create(
                                confidence=confidence, 
                                monthly_amount=monthly_amount,
                                source=source,
                                average_monthly_income=average_monthly_income,
                                last_two_years_income=last_two_years_income, 
                                last_year_income=last_year_income,
                                customer=customer
                                )
        

 
# fetch_balance('64994a384c62fd003b1e0f73')
# fetch_income('64994a384c62fd003b1e0f73', 'dd')
# fetch_identity('64994a384c62fd003b1e0f73')