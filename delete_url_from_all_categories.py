import json
import urllib.request
import csv
import time
import http.cookiejar

# Feed CSV file, containing single col where each row contains a single category name to look up. [n,1]
# Configure urls_to_delete_file_name var to match your csv file name
# The result will provide the contents of the categories your specify.

credential_csv_file_name = 'credentials.csv'   # CSV containing API credentials
urls_to_delete_file_name = 'urlLookup.csv'   # CSV containing urls you want to remove from all categories

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


# Read category names from CSV file
urls_to_delete = []
with open(urls_to_delete_file_name, mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if len(row) == 1:  # Ensure the row has only one element (category name)
            urls_to_delete.append(row[0].strip())

# Print the category names for debugging
print(f"Categories to lookup: {urls_to_delete}")


configured_url_to_filter = urls_to_delete

try:
    with opener.open(req) as res:
        if res.status == 200:
            print("Authentication successful.")

            # Fetch URL Categories
            categories_url = f"{BASE_URL}/urlCategories"
            req = urllib.request.Request(categories_url, headers={'Content-Type': 'application/json'})

            with opener.open(req) as res:
                if res.status == 200:
                    print("Successfully fetched URL categories.")

                    # Parse JSON response
                    all_categories = json.loads(res.read().decode('utf-8'))

                    categories_to_update = []
                    for category in all_categories:
                        matching_urls = [url for url in category.get('urls', []) if url in configured_url_to_filter]
                        if matching_urls:
                            categories_to_update.append({
                                "id": category['id'],
                                "configuredName": category['configuredName'],
                                "urls": matching_urls
                            })
                    print(f"Categories to update: {categories_to_update}")

                    # Process each category for URL removal
                    for category in categories_to_update:
                        categoryId = category['id']
                        configuredName = category['configuredName']
                        urls_to_remove = category['urls']

                        # Log details for debugging
                        print(f"Removing URLs {urls_to_remove} from category {configuredName} ({categoryId})")

                        # Prepare the data to update the category
                        action = "REMOVE_FROM_LIST"  # Action set to remove
                        update_data = json.dumps({
                            "id": categoryId,
                            "configuredName": configuredName,
                            "superCategory": "USER_DEFINED",  # Assuming all categories are 'USER_DEFINED'
                            "urls": urls_to_remove
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
                    print(f"Failed to fetch URL categories. Status code: {res.status}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error occurred: {e.code}, {e.reason}")
    content = e.read()
    print(f"Response content for debugging: {content}")