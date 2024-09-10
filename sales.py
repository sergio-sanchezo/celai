from simple_salesforce import Salesforce
import json


sf = Salesforce(username="sundevs@netline.net.netline", password="NetlineIA@123ku6KPaqc87uPFKYCOeiaDtcY2", consumer_key="3MVG9j6uMOMC1DNgX0ameohUtWQ1ty1Ue_i0hffxZpyLP9ph1kneWvriHqsM826sp56epAmQK_QRp9.UqGEwW", consumer_secret="F1459C64D77D67F1DF7CA4694BD5C504B1B774114E5A2FF526815CAE0286B62E", domain="test")

# First 5 records from the Account object
result = sf.query("SELECT Id, Name, FirstName, LastName, RUT__c, Phone FROM Account LIMIT 5")


print(json.dumps(result, indent=4))

from services.salesforce import getUserByPhone

result = getUserByPhone("+56352280778").get("records", [{}])[0].get("Name", "Unknown")

print("="*30)
print(result)

# # First 5 records from the Account object
# account_fields  = sf.Account.describe()

# # write the data to a file
# with open('account_fields.json', 'w') as f:
#     f.write(json.dumps(account_fields, indent=4))

# # Extract the field names, type and label from the fields and write to a file, read it from account_fields.json
# with open('account_fields.json', 'r') as f:
#     account_fields = json.load(f)

# fields = []
# for field in account_fields['fields']:
#     fields.append({
#         'name': field['name'],
#         'type': field['type'],
#         'label': field['label']
#     })

# # write the data to a file
# with open('account_fields_extracted.json', 'w') as f:
#     f.write(json.dumps(fields, indent=4))
