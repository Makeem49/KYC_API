import requests
import os 

from verifications.models import CustomerIncomeData

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


class RetrieveUserIncomeData(object):
    """This """
    def __init__(self, bvn, phone=None) -> None:
        self.bvn = bvn
        self.base_url = 'https://api.creditchek.africa/v1/'
        self.credit_check_token = '3bv3Dn7HF/X4OEJOlp+Sa3/rbUkMEBsJlOGJyHv7tWV9nnAgIitZC6B2DiqsdGi4'
        self.headers = {"token": self.credit_check_token}
        
        
    def send_identity_request(self, endpoint):
        """method for retieving identity data"""
        query_param = {}
        query_param['bvn'] = self.bvn
        response = requests.post(f"{self.base_url}{endpoint}", params=query_param, headers=self.headers)
        return response
    
    
    def send_income_request(self, endpoint, borrower_id):
        """Method for retrieving income data"""
        url = f'{self.base_url}{endpoint}/{borrower_id}'
        print(url)
        response = requests.get(f"{self.base_url}{endpoint}/{borrower_id}", headers=self.headers) 
        return response
    
    
    def extract_bvn_data(self, resp_data):
        """Help to extract user personal data from response data from third party API"""
        data = resp_data.get('data')
        gender = 'M' if data.get("gender") == 'Male' else 'F'
        
        return {
            "first_name" : data.get("firstName"),
            "last_name" : data.get("lastName"),
            "middle_name" : data.get("middleName"),
            "dob" : data.get("dateOfBirth"),
            "email" : data.get("email"),
            "is_verify" : True,
            "bvn" : data.get("bvn"),
            "phone" : str(data.get("phones")[0]) if data.get('phones') else 'null',
            "address" : data.get("address"),
            "marital_status" : data.get("maritalStatus"),
            "photo_id" : data.get("photo"),
            "gender" : gender,
            "nationality" : data.get("nationality"),
            "status" : 'PENDING',
            "residential_address" : data.get("residentialAddress"),
            "lga_origin" : data.get("lgaOfOrigin"),
            "lga_residence" : data.get("lgaOfResidence"),
            "nin" : data.get("nin"),
            "watchlist" : data.get("watchListed")   
        }
        
    def extract_income_data(self, data):
        """Hlep to retrieve user income data through an API"""
        income_data = data.get('data')
        
        edti = income_data.get('EDTI')
    
        if edti:
            return {
                'average_monthly_income' : edti.get('average_monthly_income'),
                'total_money_received' : edti.get('totalMoneyReceive'),
                'total_money_spent' : edti.get('totalmoneySpents'),
                'eligibility_amount' : edti.get('eligibleAmount'),
                'debt_to_income' : edti.get('annual_edti'),
                'debt_to_income_reason' : edti.get('DTI_reason')
            } 
        return {}


    def save_identity_to_db(self, data, user):
        """This method help to save extracted data to db"""
        # customer = Customer.objects.create(**data)
        
        user.first_name = data.get("first_name")
        user.last_name = data.get("last_name")
        user.middle_name = data.get("middle_name")
        user.dob = data.get("dob")
        user.email = data.get("email")
        user.is_verify = True
        user.bvn = data.get("bvn")
        user.phone = data.get("phone")
        user.address = data.get("address")
        user.marital_status = data.get("marital_status")
        user.photo_id = data.get("photo_id")
        user.gender = data.get('gender')
        user.nationality = data.get("nationality")
        user.status = data.get('status')
        user.residential_address = data.get("residential_address")
        user.lga_origin = data.get("lga_origin")
        user.lga_residence = data.get("lga_residence")
        user.nin = data.get("nin")
        user.watchlist = data.get("watchlist")   
        user.save()
        return user
    
    def save_income_to_db(self, data, user):
        """This method help to save extracted data to db"""
        data['customer'] = user
        income = CustomerIncomeData.objects.create(**data)
        return income
        
        
# user = RetrieveUserIncomeData('22375568132')
# identity = user.send_identity_request('identity/delete-borrower')
# print(identity.json())

# income = user.send_income_request('income/insight-data', '64ceb7196813f703053d21d8')
# data = income.json()
# print(data)
# income_data = user.extract_income_data(data)
# print(income_data)

# print(income.json())
# # url = 'https://api.creditchek.africa/v1/income/api/process-income'

# income = user.send_income_request('income/api/process-income/', '64ceb7196813f703053d21d8')
# print(income.json())


# resp = requests.get('https://api.creditchek.africa/v1/income/insight-data/64ceb7196813f703053d21d8', 
#                     headers={'token' : '3bv3Dn7HF/X4OEJOlp+Sa3/rbUkMEBsJlOGJyHv7tWV9nnAgIitZC6B2DiqsdGi4'})

# print(resp.json())