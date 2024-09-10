from simple_salesforce import Salesforce

# TODO: Replace with envs
sf = Salesforce(username="sundevs@netline.net.netline", password="NetlineIA@123ku6KPaqc87uPFKYCOeiaDtcY2", consumer_key="3MVG9j6uMOMC1DNgX0ameohUtWQ1ty1Ue_i0hffxZpyLP9ph1kneWvriHqsM826sp56epAmQK_QRp9.UqGEwW", consumer_secret="F1459C64D77D67F1DF7CA4694BD5C504B1B774114E5A2FF526815CAE0286B62E", domain="test")

def getUserByPhone(phone):
    result = sf.query(f"SELECT Id, Name, RUT__c, Email_Empresa__c, Phone FROM Account WHERE Phone = '{phone}' LIMIT 1")
    if result['records']:
        record = result['records'][0]
        # Remove the 'attributes' key from the record
        if 'attributes' in record:
            del record['attributes']
        return record
    return {}

def getUserByRUT(rut):
    result = sf.query(f"SELECT Id, Name, RUT__c, Email_Empresa__c, Phone FROM Account WHERE RUT__c = '{rut}' LIMIT 1")
    if result['records']: 
        record = result['records'][0]
        # Remove the 'attributes' key from the record
        if 'attributes' in record:
            del record['attributes']
        return record
    return {}

def createProspect(data):
    #
    return result