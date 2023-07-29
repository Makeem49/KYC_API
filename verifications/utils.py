import requests
import os 

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


# def fetch_balance(customer_id):
#     resp = okra_balance_api.get_by_customer(customer_id=customer_id, limit=2)
#     data = resp.json()
#     return data
	
 
# def fetch_identity(customer_id):
#     resp = okra_identity_api.get_by_customer(customer_id)
#     obj = resp.json()
#     print(obj, '00000000000000000')
#     data = obj.get('data')
#     user = {}
    
#     if data:
#         identity = data.get('identity')
#         if identity:
#             data = identity[0]
#             user['dob'] = data.get('dob')
#             user['bvn'] = data.get('bvn')
#             user['gender'] = data.get('gender').upper()
            
#             firstname = data.get('firstname')
#             lastname = data.get('lastname')
            
#             if firstname and lastname:
#                 user['first_name'] = data.get('firstname')
#                 user['last_name'] = data.get('lastname')
#                 user['middle_name'] = data.get('middlename')
                
#             else:
#                 name = data.get('customer').get('name').split(' ')
#                 user['first_name'] = name[0]
#                 user['last_name'] = name[1]
                
#             user['phone'] = data.get('phone')[0]
#             user['email'] = data.get('email')
#             user['address'] = data.get('address')[0]
   
#     return user 
        
 
# def fetch_income(customer_id, customer):
#     resp = okra_income_api.get_by_customer(customer_id=customer_id)
#     obj = resp.json()
#     data = obj.get('data')
#     income = data.get('income')

#     if income:
#         user_income_data = income[0]
#         confidence = user_income_data.get('confidence').strip('%')
#         last_two_years_income = user_income_data.get('last_two_years_income')
#         last_year_income = user_income_data.get('last_year_income')
        
#         streams = user_income_data.get('streams')
#         if streams:
#             stream = streams[0]
#             monthly_amount = stream.get('monthly_income')
#             source = stream.get('income_type')
#             average_monthly_income = stream.get('avg_monthly_income')
            
            
#         customer_income = CustomerIncomeData.objects.create(
#                                 confidence=confidence, 
#                                 monthly_amount=monthly_amount,
#                                 source=source,
#                                 average_monthly_income=average_monthly_income,
#                                 last_two_years_income=last_two_years_income, 
#                                 last_year_income=last_year_income,
#                                 customer=customer
#                                 )
        

 
# def verification_by_bvn(bvn):
#     base_url = os.getenv('CREDIT_CHECK_BASE_URL')
#     response = requests.post(f"{base_url}/{'endpoint'}", params={'bvn':bvn})
#     try:
#         data = response.json() 
#     except:
#         return {}
#     return data


