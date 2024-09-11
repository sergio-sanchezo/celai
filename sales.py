# salesforce_service.py
from simple_salesforce import Salesforce
import json
from services.salesforce import getUserByPhone, getUserByRUT

# Initialize Salesforce connection
def init_salesforce():
    return Salesforce(
        username="sundevs@netline.net.netline",
        password="NetlineIA@123ku6KPaqc87uPFKYCOeiaDtcY2",
        consumer_key="3MVG9j6uMOMC1DNgX0ameohUtWQ1ty1Ue_i0hffxZpyLP9ph1kneWvriHqsM826sp56epAmQK_QRp9.UqGEwW",
        consumer_secret="F1459C64D77D67F1DF7CA4694BD5C504B1B774114E5A2FF526815CAE0286B62E",
        domain="test"
    )

# Fetch the first 5 records from the Account object
def fetch_accounts():
    sf = init_salesforce()
    result = sf.query("SELECT Id, Name, FirstName, LastName, RUT__c, Phone, Empresa_1__c FROM Account LIMIT 5")
    return result

# Save query results to a file
def save_query_results():
    result = fetch_accounts()
    with open('account_records.json', 'w') as f:
        json.dump(result, f, indent=4)

# Extract and save Account fields to a file
def extract_and_save_account_fields():
    sf = init_salesforce()
    account_fields = sf.Account.describe()

    with open('account_fields.json', 'w') as f:
        json.dump(account_fields, f, indent=4)

    # fields = [{'name': field['name'], 'type': field['type'], 'label': field['label']} for field in account_fields['fields']]

    # with open('account_fields_extracted.json', 'w') as f:
    #     json.dump(fields, f, indent=4)


def fetch_all_account_fields():
    sf = init_salesforce()
    # Get the description of the Account object, which includes all fields
    account_description = sf.Account.describe()
    
    # Extract the list of field names
    field_names = [field['name'] for field in account_description['fields']]
    
    # Create the SOQL query dynamically to get the last 5 created records
    query = f"SELECT {', '.join(field_names)} FROM Account ORDER BY CreatedDate DESC LIMIT 5"
    
    # Execute the query
    result = sf.query(query)
    
    return result



if __name__ == "__main__":
    # Fetch and write to a file the all fields of the Account object
    # result = fetch_all_account_fields()
    # with open('account_fields_all.json', 'w') as f:
    #     json.dump(result, f, indent=4)

    result = getUserByPhone("+56352280777")
    print(result if result else "Not found")

