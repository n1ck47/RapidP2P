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
