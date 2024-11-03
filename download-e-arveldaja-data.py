import base64
import hashlib
import hmac
import itertools
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests

import config as conf


def get_auth_headers(url: str) -> Dict[str, str]:
    """
    Generates the required authentication headers for API requests.

    Parameters:
    - url (str): The path of the API endpoint without the /v1 prefix (e.g., "/journals/62307/document_user").

    Returns:
    - dict: A dictionary containing the required authentication headers.
    """
    query_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    key_bytes = conf.API_KEY_PASSWORD.encode('utf-8')
    message_bytes = f"{conf.API_KEY_ID}:{query_time}:/v1{url}".encode('utf-8')
    hmac_digest = hmac.new(key_bytes, message_bytes, hashlib.sha384).digest()
    signature_base64 = base64.b64encode(hmac_digest).decode('utf-8')
    x_auth_key = f"{conf.API_KEY_PUBLIC_VALUE}:{signature_base64}"

    headers = {
        'X-AUTH-QUERYTIME': query_time,
        'X-AUTH-KEY': x_auth_key,
        'Content-Type': 'application/json',
    }

    return headers


def get_all_paged_records(endpoint: str, params: Optional[Dict[str, Union[str, int]]] = None) -> List[Dict[str, Any]]:
    """
    Get all paginated data from an API endpoint page by page.

    Parameters:
    - endpoint (str): The API endpoint to fetch records from.
    - params (dict, optional): Additional parameters for the request.

    Returns:
    - list: A list of dictionaries containing the records.
    """
    records: List[Dict[str, Any]] = []
    page = 1
    while True:
        params = params or {}
        params['page'] = page
        url = f"{conf.BASE_URL}{endpoint}"
        headers = get_auth_headers(endpoint)

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get data from {endpoint}: {e}")
            break

        try:
            data = response.json()
        except ValueError:
            print(f"Invalid JSON response from {endpoint}")
            break

        records.extend(data.get('items', []))

        if page >= data.get('total_pages', 1):
            break

        page += 1

    return records


def get_single_response(endpoint: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    """
    Get all data from an API endpoint that returns a single response.

    Parameters:
    - endpoint (str): The API endpoint to fetch data from.

    Returns:
    - dict or list: The data from the response as a dictionary or list of dictionaries, or None if an error occurred.
    """
    url = f"{conf.BASE_URL}{endpoint}"
    headers = get_auth_headers(endpoint)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get data from {endpoint}: {e}")
        raise
    except ValueError:
        print(f"Invalid JSON response from {endpoint}")
        raise

    return None


def save_records_to_json(filename: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
    """
    Save structured data to a JSON file with 2-space indent.

    Parameters:
    - filename (str): The filename to save the data.
    - data (dict or list): The data to be saved.
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)


def download_attachment(record_id: Union[str, int], attachment_endpoint: str,
                        not_found_error_message: str) -> Optional[Dict[str, Any]]:
    """
    Download attachment associated with a specific record.

    Parameters:
    - record_id (int): The unique identifier of the record.
    - attachment_endpoint (str): The endpoint template for attachments.

    Returns:
    - dict or None: The attachment data as a dictionary, or None if no attachment is found.
    """
    endpoint = attachment_endpoint.format(record_id=record_id)
    url = f"{conf.BASE_URL}{endpoint}"
    headers = get_auth_headers(endpoint)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
        if e.response is not None and e.response.status_code == 409:
            error_data = e.response.json()
            if error_data.get('code') == 1 and error_data.get('messages') and error_data['messages'][0] == not_found_error_message:
                print(f"No attachment found for record {record_id}")
                return None
        print(f"Failed to download attachment for record {record_id}: {e}")
        raise
    except ValueError:
        print(f"Invalid JSON response for attachment of record {record_id}")
        raise

    return None


def main() -> None:
    """
    Main function to retrieve all relevant data and attachments.
    """
    os.makedirs("output", exist_ok=True)

    paged_endpoint_names = [
        "sale_invoices",
        "clients",
        "products",
        "projects",
        "purchase_invoices",
        "transactions",
        "journals", # may take long in case of many records
    ]

    endpoints_with_attachments = {
        "journals",
        "sale_invoices",
        "purchase_invoices",
        "transactions",
    }

    for name in paged_endpoint_names:
        endpoint = f'/{name}'
        print(f'Downloading and saving records for endpoint "{name}"...')
        records = get_all_paged_records(endpoint)
        save_records_to_json(f"output/{name}.json", records)

        if name in endpoints_with_attachments:
            print(f'Downloading and saving attachments for endpoint "{name}"...')
            for record in records:
                record_id = record.get('id')
                if not record_id:
                    print(f"Record without ID found in {name}, skipping attachment download.")
                    continue

                attachment = download_attachment(record_id,
                        f'{endpoint}/{record_id}/document_user', "No file found.")
                if attachment:
                    save_records_to_json(f"output/{name}_{record_id}_attachment.json", attachment)

                # Confirmed sale invoices have extra downloads: system generated PDF and delivery options.
                if name == "sale_invoices" and record['status'] == 'CONFIRMED':
                    pdf = download_attachment(record_id,
                            f'{endpoint}/{record_id}/pdf_system', None) # None as it is an error if the PDF is not found
                    if pdf:
                        save_records_to_json(f"output/{name}_{record_id}_system_pdf.json", pdf)
                    delivery_options = get_single_response(f'{endpoint}/{record_id}/delivery_options')
                    if delivery_options:
                        save_records_to_json(f"output/{name}_{record_id}_delivery_options.json", delivery_options)

    array_endpoint_names = [
        "account_dimensions",
        "accounts",
        "bank_accounts",
        "currencies",
        "invoice_series",
        "purchase_articles",
        "sale_articles",
        "templates",
    ]

    single_response_endpoint_names = [
        "invoice_info",
        "vat_info",
    ]

    for name in itertools.chain(single_response_endpoint_names, array_endpoint_names):
        endpoint = f'/{name}'
        print(f'Downloading and saving records for endpoint "{name}"...')
        records = get_single_response(endpoint)
        save_records_to_json(f"output/{name}.json", records)


if __name__ == "__main__":
    main()
