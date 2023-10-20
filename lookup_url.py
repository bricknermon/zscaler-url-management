import json
import urllib.request
import csv
import time
import http.cookiejar

# Feed CSV file, containing single col where each row contains a url to look up. [n,1]
# Configure url_to_search_file_name var to the file name of your csv file
# The result will provide details containing Assigned URL categories and any security alerts of each specified URL

credential_csv_file_name = 'credentials.csv'   # CSV containing API credentials
url_to_search_file_name = 'urlLookup.csv'      # CSV containing URLS you want to look up further inforamtion on

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



# Create a CookieJar object to handle cookies
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

# Obfuscate API key and get timestamp
obfuscated_api_key, timestamp = obfuscateApiKey(API_KEY)

# Authenticate
auth_url = f"{BASE_URL}/authenticatedSession"
auth_data = {
    "username": USERNAME,
    "password": PASSWORD,
    "apiKey": obfuscated_api_key,
    "timestamp": str(timestamp)
}

req = urllib.request.Request(auth_url, data=json.dumps(auth_data).encode('utf-8'), headers={'Content-Type': 'application/json'})


# Read URLs from CSV file
urls_to_lookup = []
with open(url_to_search_file_name, mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if len(row) == 1:  # Ensure the row has only one element (URL)
            urls_to_lookup.append(row[0].strip())
            
# Print the URLs for debugging
print(f"URLs to lookup: {urls_to_lookup}")

try:
    with opener.open(req) as res:
        if res.status == 200:
            print("Successfully authenticated.")

             # URL Lookup
            lookup_url = f"{BASE_URL}/urlLookup"
            req = urllib.request.Request(lookup_url, data=json.dumps(urls_to_lookup).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
            with opener.open(req) as res:
                if res.status == 200:
                    print("Successfully fetched URL categories.")
                    print(json.dumps(json.loads(res.read().decode('utf-8')), indent=4))
                else:
                    print(f"Failed to look up URL categories. Status code: {res.status}")
        else:
            print(f"Authentication failed. Status code: {res.status}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error occurred: {e.code}, {e.reason}")
    content = e.read()
    print(f"Response content for debugging: {content.decode('utf-8')}")