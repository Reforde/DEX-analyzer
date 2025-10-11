
import requests
import json
from typing import Optional, Dict
from config import Config


class BitqueryClient:
    """Client for interacting with Bitquery API"""
    
    def __init__(self, api_key: str):
        """
        Initialize Bitquery client
        
        Args:
            api_key: Bitquery API key
        """
        self.api_key = api_key
        self.url = Config.BITQUERY_URL
        self.timeout = Config.API_TIMEOUT
    
    def test_connection(self) -> Dict[str, any]:
        """
        Test the API connection
        
        Returns:
            Dictionary with 'success' boolean and 'message' string
        """
        query = """
        {
          EVM(network: eth) {
            Blocks(limit: {count: 1}) {
              Block {
                Number
              }
            }
          }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = json.dumps({
            "query": query,
            "variables": "{}"
        })
        
        try:
            response = requests.request("POST", self.url, headers=headers, 
                                       data=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if "errors" in data:
                    error_msg = data["errors"][0].get("message", "Unknown error")
                    return {"success": False, "message": f"API Error: {error_msg}"}
                elif "data" in data:
                    return {"success": True, "message": "Connection successful!"}
                else:
                    return {"success": False, "message": "Unexpected response format"}
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_token_price(self, network: str, token_address: str, 
                       base_address: str) -> Optional[Dict[str, float]]:
        """
        Get the latest price for a token pair
        
        Args:
            network: Network name (eth, bsc, etc.)
            token_address: Token contract address
            base_address: Base currency contract address
            
        Returns:
            Dictionary with 'price' and 'volume' or None if failed
        """
        query = """
        query ($network: evm_network!, $token: String!, $base: String!) {
          EVM(network: $network, dataset: realtime) {
            DEXTradeByTokens(
              where: {
                Trade: {
                  Currency: {SmartContract: {is: $token}}
                  Side: {Currency: {SmartContract: {is: $base}}}
                }
                TransactionStatus: {Success: true}
              }
              orderBy: {descending: Block_Time}
              limit: {count: 1}
            ) {
              Block {
                Time
              }
              Trade {
                Amount
                Price
                PriceInUSD
                Currency {
                  Symbol
                }
                Side {
                  Amount
                  Currency {
                    Symbol
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {
            "network": network,
            "token": token_address.lower(),
            "base": base_address.lower()
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = json.dumps({
            "query": query,
            "variables": json.dumps(variables)
        })
        
        try:
            response = requests.request("POST", self.url, headers=headers, 
                                       data=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if "errors" in data:
                    print(f"API Error: {data['errors']}")
                    return None
                
                if "data" in data and "EVM" in data["data"]:
                    trades = data["data"]["EVM"]["DEXTradeByTokens"]
                    
                    if trades and len(trades) > 0:
                        trade = trades[0]
                        
                        if "Trade" in trade and "Price" in trade["Trade"]:
                            price = trade["Trade"]["Price"]
                            if price and float(price) > 0:
                                amount = 0
                                if "Amount" in trade["Trade"]:
                                    amount_val = trade["Trade"]["Amount"]
                                    if amount_val:
                                        amount = float(amount_val)
                                
                                return {
                                    "price": float(price),
                                    "volume": amount
                                }
                
                return None
            
            elif response.status_code == 401:
                print("Authentication failed. Please check your API key.")
                return None
            else:
                print(f"Error response: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception in API call: {str(e)}")
            return None