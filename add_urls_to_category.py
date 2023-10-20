import urllib.request
import urllib.error
import json
import time
import csv
from http.cookiejar import CookieJar

# Feed CSV file, with urls to add and configure urls_to_add_file_name var to match file name
# File needs to contain single col where First row is 'URL' and each row proceeding contains a single url name to add. [n,1]
# Given this is a more sensitive operation, look to lines 81-88.
# You will need to adjust: categoryID, action according to the opperation (add or remove URL), configuredName (Category name), superCategory
# Please refrence the lines (81-88) for further instruction on how to configure properly.

credential_csv_file_name = 'credentials.csv'   # CSV containing API credentials
urls_to_add_file_name = 'approvedToAdd.csv'    # CSV containing URLS you are looking to add

def obfuscateApiKey(api_key):
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = ""
    for i in range(len(n)):
        key += api_key[int(n[i])]
    for j in range(len(r)):
        key += api_key[int(r[j])+2]
    return key, now


# Read URLs from CSV file
urls_to_add = []
with open(urls_to_add_file_name, 'r') as infile:
    reader = csv.reader(infile)
    next(reader)  # Skip header
    for row in reader:
        urls_to_add.append(row[0])

# Read credentials from CSV file
credentials = {}
with open(credential_csv_file_name, mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if len(row) >= 2:  # Check that the row has at least two elements
            credentials[row[0].strip()] = row[1].strip()  # Using .strip() to remove any extra spaces
        else:
            print(f"Skipping incomplete or empty row: {row}")

# Print the contents of the credentials dictionary for debugging
print(f"Contents of credentials dictionary: {credentials}")

try:
    BASE_URL = credentials['BASE_URL']
    API_KEY = credentials['API_KEY']
    USERNAME = credentials['USERNAME']
    PASSWORD = credentials['PASSWORD']
except KeyError as e:
    print(f"KeyError: {e}. Make sure this key exists in the credentials dictionary.")

# Obfuscate API key and get timestamp
obfuscated_api_key, timestamp = obfuscateApiKey(API_KEY)

# Initialize a CookieJar and build an opener with HTTPCookieProcessor
cookie_jar = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

# Authenticate
auth_url = f"{BASE_URL}/authenticatedSession"
auth_data = json.dumps({
    "username": USERNAME,
    "password": PASSWORD,
    "apiKey": obfuscated_api_key,
    "timestamp": str(timestamp)
}).encode('utf-8')

req = urllib.request.Request(auth_url, data=auth_data, headers={'Content-Type': 'application/json'})

try:
    with opener.open(req) as res:
        if res.status == 200:
            print("Authentication successful.")
            
            # Prepare the data to update the category
            categoryId = "CUSTOM_34"  # Replace "CUSTOM_34 with your specific categoryID. Will follow similar format."
            action = "ADD_TO_LIST"  # Or "REMOVE_FROM_LIST" based on your requirement

            update_data = json.dumps({
                "id": categoryId,
                "configuredName": "EARB Approved",     # Replace contents to the right of "configuredName" with your category name
                "superCategory": "USER_DEFINED",       # Replace contents to the right of "superCategory" with the super category of your category. Very unlikely to not be USER_DEFINED
                "urls": urls_to_add
            }).encode('utf-8')

            # Make a PUT request to update the category
            update_category_url = f"{BASE_URL}/urlCategories/{categoryId}"
            query_parameters = {'action': action}
            url_with_query = f"{update_category_url}?{urllib.parse.urlencode(query_parameters)}"
            
            req = urllib.request.Request(url_with_query, data=update_data, method='PUT', headers={'Content-Type': 'application/json'})

            with opener.open(req) as res:
                if res.status == 200:
                    print("Successfully updated the URL category.")
                    print(json.dumps(json.loads(res.read().decode('utf-8')), indent=4))
                else:
                    print(f"Failed to update the URL category. Status code: {res.status}")
        else:
            print(f"Authentication failed. Status code: {res.status}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error occurred: {e.code}, {e.reason}")
    content = e.read()
    print(f"Response content for debugging: {content.decode('utf-8')}")