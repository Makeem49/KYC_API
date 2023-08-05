import requests
import os 

# from verifications.models import Customer

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
        response = requests.post(f"{self.base_url}{endpoint}/{borrower_id}", headers=self.headers) 
        return response
    
    
    def extract_bvn_data(self, data):
        """Help to extract user personal data from response data from third party API"""
        return {
            "first_name" : data.get("firstName"),
            "last_name" : data.get("lastName"),
            "middle_name" : data.get("middleName"),
            "dob" : data.get("dateOfBirth"),
            "email" : data.get("email"),
            "is_verify" : True,
            "bvn" : data.get("bvn"),
            "phone" : str(data.get("phones")),
            "address" : data.get("address"),
            "marital_status" : data.get("maritalStatus"),
            "photo_id" : data.get("photo"),
            "gender" : data.get("gender"),
            "nationality" : data.get("nationality"),
            "borrower_id" : data.get("_id"),
            "status" : 'PENDING',
            "residential_address" : data.get("residentialAddress"),
            "lga_origin" : data.get("lgaOfOrigin"),
            "lga_residence" : data.get("lgaOfResidence"),
            "nin" : data.get("nin"),
            "watchlist" : data.get("watchListed")   
        }
        
    def extract_income_data(self, data):
        """Hlep to retrieve user income data through an API"""
        insight = data.get('insight')
        linked_account = insight.get('linkedFinancialAccounts')
        
        if linked_account:
            institution = linked_account.get('institution')
            bank = institution.get('name')
            bank_code = institution.get('bankCode')
            account_type = institution.get('type')
            
            bvn = linked_account.get('bvn')
            balance = linked_account.get('balance')
            account_type = linked_account.get('type')
            account_number = linked_account.get('accountNumber')
            
            return {
                'average_monthly_income' : insight.get('avgMonthlyIncome'),
                'total_money_received' : insight.get('totalmoneyReceive'),
                'total_money_spent' : insight.get('totalmoneySpents'),
                'eligibility_amount' : insight.get('eligibleAmount'),
                'debt_to_income' : insight.get('DTI'),
                'debt_to_income_reason' : insight.get('DTI_reason'),
                'bank_code' : bank_code,
                'type' : account_type,
                'balance' : balance,
                'account_number' : account_number, 
                'bvn' : bvn, 
                'bank' : bank
            } 
        return {}


    def save_identity_to_db(self, data):
        """This method help to save extracted data to db"""
        data = self.extract_bvn_data(data)
        # customer = Customer.objects.create(**data)
        
        
    
    
        
user = RetrieveUserIncomeData('22375568132')
data = user.send_identity_request('identity/verifyData')
try:
    data = data.json()
    print(data)
    user_data = user.extract_bvn_data(data)
    # print(user_data)
except Exception as e:
    print(f'An error occured {e}')
    
    
income = user.send_income_request('income/insight-data', '64c62b2095eb0dbf55bce821')

print(income)