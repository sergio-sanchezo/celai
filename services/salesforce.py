# services/salesforce.py

import os
from simple_salesforce import Salesforce

class SalesforceService:
    def __init__(self, username, password, security_token, consumer_key, consumer_secret, domain="test"):
        # Inicializar Salesforce utilizando los parámetros recibidos
        self.sf = Salesforce(
            username=username,
            password=password + security_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            domain=domain
        )

    def get_user_by_phone(self, phone):
        result = self.sf.query(f"SELECT Id, Name, RUT__c, Email_Empresa__c, Phone FROM Account WHERE Phone = '{phone}' LIMIT 1")
        return self._process_result(result)

    def get_user_by_rut(self, rut):
        result = self.sf.query(f"SELECT Id, Name, RUT__c, Email_Empresa__c, Phone FROM Account WHERE RUT__c = '{rut}' LIMIT 1")
        return self._process_result(result)
    
    def get_prospect_by_phone(self, phone):
        result = self.sf.query(f"SELECT Id, FirstName, LastName FROM Lead WHERE Phone = '{phone}' LIMIT 1")
        return self._process_result(result)

    def create_prospect(self, data):
        prospect_data = {
            'FirstName': data.get('first_name', 'Sergio'),
            'LastName': data.get('last_name', 'Sanchez'),
            'Company': data.get('company', 'Sundevs'),
            'RUT__c': data.get('rut', '7172494'),
            'Phone': data['phone'],
            'Email': data['email'],
            'Consulta_o_comentario__c': data['comment'],
            'Status': 'No atendido',
            "OwnerId": "00GEk000004qNB7",

        }
        return self.sf.Lead.create(prospect_data)
    
    def create_support_case(self, data):
        case_data = {
            'Subject': 'Soporte para prospecto existente',
            'Description': data.get('Consulta_o_comentario__c', ''),
            'Status': 'Nuevo',
            'Origin': 'Web',
            "OwnerId": "00GEk000004qNB7"
        }
        return self.sf.Case.create(case_data)
        
    def create_prospect_by_campaign(self, data):
        arguments = data.get("message", {}).get("toolCalls", [])[0].get("function", {}).get("arguments", {})
        phone = arguments.get('Phone', '')  

        existing_prospect = self.get_prospect_by_phone(phone)

        if existing_prospect:
            return self.create_support_case(data)
        else:
            prospect_data = {
                'FirstName': arguments.get('FirstName', ''),
                'LastName': arguments.get('LastName', ''),
                'Company': arguments.get('Company', 'Unknown'),
                'RUT__c': arguments.get('RUT__c', ''),
                'Phone': phone,
                'Email': arguments.get('Email', ''),
                'Consulta_o_comentario__c': arguments.get('Consulta_o_comentario__c', ''),
                'Status': 'No atendido',
                "OwnerId": "00GEk000004qNB7"
            }
            return self.sf.Lead.create(prospect_data) 
        
    def _process_result(self, result):
        if result['records']:
            record = result['records'][0]
            if 'attributes' in record:
                del record['attributes']
            return record
        return {}

