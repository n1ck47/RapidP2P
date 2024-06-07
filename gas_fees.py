# file: get_gas_fees.py

import requests

def get_gas_fees(api_key):
    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == '1':  # Successful response
        safe_gas_price = data['result']['SafeGasPrice']
        propose_gas_price = data['result']['ProposeGasPrice']
        fast_gas_price = data['result']['FastGasPrice']
        
        return {
            "SafeGasPrice": safe_gas_price,
            "ProposeGasPrice": propose_gas_price,
            "FastGasPrice": fast_gas_price
        }
    else:
        raise Exception("Error fetching gas fees from Etherscan")

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual Etherscan API key
    api_key = '7JDC8S1TS4QCWWJ8P7TTR6U7UGBFFFH9R1'
    gas_fees = get_gas_fees(api_key)
    print("Safe Gas Price:", gas_fees["SafeGasPrice"])
    print("Proposed Gas Price:", gas_fees["ProposeGasPrice"])
    print("Fast Gas Price:", gas_fees["FastGasPrice"])
