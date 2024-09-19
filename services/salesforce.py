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
    # Extraer los campos necesarios de los "arguments"
    prospect_data = {
        'FirstName': data.get('first_name', 'Sergio'),
        'LastName': data.get('last_name', 'Sanchez'),
        'Company': data.get('company', 'Sundevs'),
        'RUT__c': data.get('rut', '7172494'),
        'Phone': data['phone'],
        'Email': data['email'],
        'Consulta_o_comentario__c': data['comment'],
        'Status': 'No atendido'
    }
    # Crear el prospecto en Salesforce
    result = sf.Lead.create(prospect_data)
    return result

def createProspectCampaign(data):

    arguments = data.get("message", {}).get("toolCalls", [])[0].get("function", {}).get("arguments", {})
    
    prospect_data = {
        'FirstName': arguments.get('FirstName', ''),
        'LastName': arguments.get('LastName', ''),
        'Company': arguments.get('Company', 'Unknown'),
        'RUT__c': arguments.get('RUT__c', ''),
        'Phone': arguments.get('Phone', ''),
        'Email': arguments.get('Email', ''),
        'Consulta_o_comentario__c': arguments.get('Consulta_o_comentario__c', ''),
        'Status': 'No atendido',
        'IsConverted': False
    }

    result = sf.Lead.create(prospect_data)
    
    return result
