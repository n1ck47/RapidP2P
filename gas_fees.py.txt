import requests

def get_blocknative_gas_fees(chain="ethereum"):
    """
    Fetches real-time gas fees from the Blocknative Gas Estimator API.

    Args:
        chain (str, optional): The blockchain to retrieve gas fees for.
            Defaults to "ethereum". Supported options include "ethereum"
            and "polygon".

    Returns:
        dict: A dictionary containing gas fee estimates for different
            confirmation timeframes (e.g., "fast", "safeLow", "standard").
            Keys represent the confirmation speed, and values represent
            the gas price (in gwei) for that speed.

    Raises:
        ValueError: If an unsupported chain is provided.
        requests.exceptions.RequestException: If an error occurs during the API request.
    """

    supported_chains = ["ethereum", "polygon"]
    if chain not in supported_chains:
        raise ValueError(f"Unsupported chain: {chain}. Supported chains: {', '.join(supported_chains)}")

    url = f"https://api.blocknative.com/gasprices/v1/{chain}"
    headers = {
        "Authorization": "YOUR_API_KEY"  # Replace with your Blocknative API key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        data = response.json()
        return data["gasPrices"]

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching gas fees: {e}") from e

# Example usage (replace YOUR_API_KEY with your actual API key)
if _name_ == "_main_":
    try:
        gas_fees = get_blocknative_gas_fees(chain="ethereum")
        print("Ethereum Gas Fees:")
        for speed, price in gas_fees.items():
            print(f"\t{speed}: {price} gwei")
    except ValueError as e:
        print(f"An error occurred: {e}")