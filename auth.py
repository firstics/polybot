from py_clob_client.client import ClobClient
import os
import asyncio

host = "https://clob.polymarket.com"
chain_id = 137 # Polygon mainnet


async def main():
    client = ClobClient(
        host=host,
        chain_id=chain_id,
        key=private_key  # Signer enables L1 methods
    )

    # Gets API key, or else creates
    api_creds = client.create_or_derive_api_creds()

    print("API Credentials:", api_creds)

if __name__ == "__main__":
    asyncio.run(main())

# api_creds = {
#     "apiKey": "8112620c-4d1b-6fb7-6518-b5fc3eb4ed88",
#     "secret": "JmgUrJO_GTnH3wEN7K3OJDE1w0y5AdGMSjdO4uhlx0A=",
#     "passphrase": "abc343b30a59c0d22b6d7ede6e3a39228e738143372c6745a0350fd5a5b87385"
# }