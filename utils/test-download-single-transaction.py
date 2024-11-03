import requests
import json
import hmac
import hashlib
import base64
from datetime import datetime

API_KEY_PUBLIC_VALUE = 'aWQ9OTI3NDMwNWZhYjQ3NDgzNzg0NTkwNTUyNzU5MGUwZGQmZGlnZXN0PWZlOTUxMDc0MmFjMWVhZjZlOThmZTZlMWJkMTllNjU3OWY4NGNkOTU4MzE4ZmM1YmEwZjI4NDUxYjEwZDY4MzI='
API_KEY_ID = '9274305fab474837845905527590e0dd'
API_KEY_PASSWORD = '28198cf21d8a4f6fa33fc07bc87bc92c'
BASE_URL = 'https://demo-rmp-api.rik.ee/v1'

def get_auth_headers(url):
    """
    Generates the required authentication headers for API requests.

    Parameters:
    - url (str): The path of the API endpoint without the /v1 prefix (e.g., "/journals/62307/document_user").

    Returns:
    - dict: A dictionary containing the required authentication headers.
    """
    query_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    key_bytes = API_KEY_PASSWORD.encode('utf-8')
    message_bytes = f"{API_KEY_ID}:{query_time}:/v1{url}".encode('utf-8')
    hmac_digest = hmac.new(key_bytes, message_bytes, hashlib.sha384).digest()
    signature_base64 = base64.b64encode(hmac_digest).decode('utf-8')
    x_auth_key = f"{API_KEY_PUBLIC_VALUE}:{signature_base64}"

    headers = {
        'X-AUTH-QUERYTIME': query_time,
        'X-AUTH-KEY': x_auth_key,
        'Content-Type': 'application/json',
    }

    return headers

def download_first_transaction():
    """
    Downloads the first transaction available and prints it in JSON format.
    """
    url = "/transactions"
    full_url = f"{BASE_URL}{url}"
    headers = get_auth_headers(url)

    response = requests.get(full_url, headers=headers, params={'page': 1})

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            first_transaction = data['items'][0]
            print(json.dumps(first_transaction, indent=4))
        else:
            print("No transactions found.")
    else:
        print(f"Failed to retrieve transactions: {response.status_code} - {response.text}")

if __name__ == "__main__":
    download_first_transaction()
