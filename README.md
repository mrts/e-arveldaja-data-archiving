# e-Arveldaja data archiving

Python app that uses the [e-Arveldaja](https://e-arveldaja.rik.ee/) API to download all available records, including clients, products, sale and purchase invoices, transactions, bank accounts, journals and other financial data. It also retrieves associated document attachments. All data is saved as JSON files.

## Documentation

See the e-Arveldaja API documentation here:
- [e-Arveldaja API overview (in Estonian)](https://abiinfo.rik.ee/e-arveldaja/e-arveldaja-api/)
- [Technical documentation for developers (in Estonian)](https://abiinfo.rik.ee/node/304/)
- [API documentation](https://demo-rmp-api.rik.ee/api.html)
- [OpenAPI specification](https://demo-rmp-api.rik.ee/openapi.yaml)

Additionally, you can use the `utils/filter-get-endpoints.py` script to generate a list of `GET` endpoints along with their response schemas. The current output as of 2024-11-02 is available in `utils/get-endpoints.txt`.

## API access setup in e-Arveldaja

To set up API access, refer to the official guide:
- [API key generation guide (in Estonian)](https://abiinfo.rik.ee/e-arveldaja/e-arveldaja-api/e-arveldaja-api-votme-genereerimine)

To enable access from any IP address, you can use `0.0.0.0/0` as the allowed IP range. However, note that this setting should be used with caution as it allows unrestricted access.

## Setup

1. Clone or download the repository to your local machine.
2. Configure the script using the provided example configuration:
   ```sh
   cp example-config.py config.py
   ```
   Then edit `config.py` to set your API credentials:
   - `API_KEY_PUBLIC_VALUE`
   - `API_KEY_ID`
   - `API_KEY_PASSWORD`
   - Ensure `BASE_URL` is set correctly for the e-Arveldaja API server.

## Running the script

To run the script, use the following commands:
```bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python download-e-arveldaja-data.py
```
This will create the `output` directory and save all records as JSON files there.

## Output

- All data will be saved as JSON files in the `output` directory.
- Each record type (e.g., clients, products) will have its own JSON file (e.g., `clients.json`, `products.json`).
- Attachments will be saved as separate JSON files with record type and record ID in the file name (e.g., `sale_invoices_4363_attachment.json`).

## License

This project is licensed under the MIT License.
