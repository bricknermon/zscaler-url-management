import json
import urllib.request
import csv
import time
import http.cookiejar

# Use to validate credentials are properly set up. 
# Simply run after specifying credential_csv_file_name with your credentials file name. 
# If works, "Authentication successful" will appear.
# If authentication fails, you will be prompted with an error code and any message that is contained with the error.

credential_csv_file_name = 'credentials.csv'   # CSV containing API credentials

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
            print("Successfully authenticated.")
        # You are now authenticated and can make subsequent API calls.
        else:
            print(f"Authentication failed. Status code: {res.status_}, Reason: {res.reason}")
            print("Response content for debugging:", res.content)

except urllib.error.HTTPError as e:
    print(f"HTTP Error occurred: {e.code}, {e.reason}")
    content = e.read()
    print(f"Response content for debugging: {content.decode('utf-8')}")