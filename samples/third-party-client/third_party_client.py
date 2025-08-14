"""
Third-Party API Client SDK for Python

This SDK provides easy access to the Fedshi third-party API endpoints
using API key authentication with HMAC signature verification.
"""

import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Dict, Optional, Any
import requests


class ThirdPartyAPIClient:
    """
    Python client for Fedshi Third-Party API
    
    Provides authenticated access to third-party endpoints using
    API key authentication with HMAC signature verification.
    """
    
    def __init__(self, api_key: str, master_secret: str, base_url: str = "https://your-domain.com"):
        """
        Initialize the client with API credentials
        
        Args:
            api_key (str): The API key provided by Fedshi
            master_secret (str): The master secret for signature generation
            base_url (str): Base URL of the API (default: production)
        """
        self.api_key = api_key
        self.master_secret = master_secret.encode('utf-8')  # Convert to bytes for HMAC
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def generate_signature(self, method: str, path: str, body: str, timestamp: str) -> str:
        """
        Generate HMAC signature for request authentication
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            path (str): API endpoint path
            body (str): Request body (empty for GET requests)
            timestamp (str): RFC3339 timestamp
            
        Returns:
            str: Hex-encoded HMAC signature
        """
        # Create string to sign: method + path + body + timestamp + api_key
        string_to_sign = f"{method}\n{path}\n{body}\n{timestamp}\n{self.api_key}"
        
        # Create HMAC signature using SHA256 with master secret
        hmac_obj = hmac.new(self.master_secret, string_to_sign.encode('utf-8'), hashlib.sha256)
        return hmac_obj.hexdigest()
    
    def make_request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an authenticated request to the API
        
        Args:
            method (str): HTTP method
            path (str): API endpoint path
            body (Dict, optional): Request body
            
        Returns:
            Dict: API response
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response contains an error
        """
        # Generate timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Prepare body
        body_string = json.dumps(body) if body else ''
        
        # Generate signature
        signature = self.generate_signature(method, path, body_string, timestamp)
        
        # Prepare headers
        headers = {
            'X-API-Key': self.api_key,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
            'Content-Type': 'application/json'
        }
        
        # Make request
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=body_string if body_string else None,
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Try to extract error message from response
            error_msg = "Unknown error"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', error_msg)
                except (ValueError, KeyError):
                    error_msg = e.response.text or error_msg
            
            raise requests.RequestException(f"API request failed: {e} - {error_msg}")
    
    def export_order_shipment_receipt(self, order_shipment_id: str) -> Dict[str, Any]:
        """
        Export order shipment receipt as PDF
        
        Args:
            order_shipment_id (str): The FID of the order shipment
            
        Returns:
            Dict: Response containing base64 PDF data
        """
        path = f"/api/v1/third-party/export-order-shipment-receipt/{order_shipment_id}"
        return self.make_request('GET', path)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics (if available)
        
        Returns:
            Dict: Usage statistics
        """
        path = "/api/v1/third-party/usage-stats"
        return self.make_request('GET', path)
    
    def save_receipt_to_file(self, receipt_data: Dict[str, Any], filename: str) -> None:
        """
        Save receipt PDF data to a file
        
        Args:
            receipt_data (Dict): Response from export_order_shipment_receipt
            filename (str): Output filename
        """
        import base64
        
        if 'data' not in receipt_data or 'content' not in receipt_data['data']:
            raise ValueError("Invalid receipt data format")
        
        # Decode base64 content
        pdf_content = base64.b64decode(receipt_data['data']['content'])
        
        # Write to file
        with open(filename, 'wb') as f:
            f.write(pdf_content)
        
        print(f"PDF saved as {filename}")


class ThirdPartyAPIClientAsync:
    """
    Async version of the Third-Party API Client
    
    Uses aiohttp for asynchronous HTTP requests
    """
    
    def __init__(self, api_key: str, master_secret: str, base_url: str = "https://your-domain.com"):
        """
        Initialize the async client with API credentials
        
        Args:
            api_key (str): The API key provided by Fedshi
            master_secret (str): The master secret for signature generation
            base_url (str): Base URL of the API (default: production)
        """
        self.api_key = api_key
        self.master_secret = master_secret.encode('utf-8')
        self.base_url = base_url.rstrip('/')
    
    def generate_signature(self, method: str, path: str, body: str, timestamp: str) -> str:
        """Generate HMAC signature (same as sync version)"""
        string_to_sign = f"{method}\n{path}\n{body}\n{timestamp}\n{self.api_key}"
        hmac_obj = hmac.new(self.master_secret, string_to_sign.encode('utf-8'), hashlib.sha256)
        return hmac_obj.hexdigest()
    
    async def make_request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an authenticated async request to the API
        
        Args:
            method (str): HTTP method
            path (str): API endpoint path
            body (Dict, optional): Request body
            
        Returns:
            Dict: API response
        """
        import aiohttp
        
        # Generate timestamp and signature
        timestamp = datetime.utcnow().isoformat() + 'Z'
        body_string = json.dumps(body) if body else ''
        signature = self.generate_signature(method, path, body_string, timestamp)
        
        # Prepare headers
        headers = {
            'X-API-Key': self.api_key,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=body_string if body_string else None
            ) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                    raise aiohttp.ClientError(f"API request failed: {response.status} - {error_msg}")
                
                return await response.json()
    
    async def export_order_shipment_receipt(self, order_shipment_id: str) -> Dict[str, Any]:
        """Async version of export_order_shipment_receipt"""
        path = f"/api/v1/third-party/export-order-shipment-receipt/{order_shipment_id}"
        return await self.make_request('GET', path)


def example_sync():
    """Example usage of the synchronous client"""
    # Initialize client
    client = ThirdPartyAPIClient(
        api_key='your_api_key_here',
        secret='your_secret_here',
        base_url='https://api.loveyourself.co.uk'
    )
    
    try:
        # Export a shipment receipt
        receipt = client.export_order_shipment_receipt('ABC123')
        print('Receipt generated successfully')
        print(f'Content length: {len(receipt["data"]["content"])}')
        print(f'File extension: {receipt["data"]["extension"]}')
        
        # Save the PDF to a file
        client.save_receipt_to_file(receipt, 'shipment_receipt.pdf')
        
    except requests.RequestException as e:
        print(f'Error: {e}')


async def example_async():
    """Example usage of the asynchronous client"""
    # Initialize async client
    client = ThirdPartyAPIClientAsync(
        api_key='your_api_key_here',
        secret='your_secret_here',
        base_url='https://api.loveyourself.co.uk'
    )
    
    try:
        # Export multiple receipts concurrently
        import asyncio
        
        tasks = [
            client.export_order_shipment_receipt('ABC123'),
            client.export_order_shipment_receipt('DEF456'),
            client.export_order_shipment_receipt('GHI789')
        ]
        
        receipts = await asyncio.gather(*tasks)
        
        for i, receipt in enumerate(receipts):
            print(f'Receipt {i+1} generated successfully')
            print(f'Content length: {len(receipt["data"]["content"])}')
        
    except Exception as e:
        print(f'Error: {e}')


def example_with_error_handling():
    """Example with comprehensive error handling"""
    client = ThirdPartyAPIClient(
        api_key='your_api_key_here',
        secret='your_secret_here'
    )
    
    try:
        receipt = client.export_order_shipment_receipt('ABC123')
        client.save_receipt_to_file(receipt, 'receipt.pdf')
        
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the API server")
    except requests.exceptions.Timeout:
        print("Timeout error: Request took too long")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication error: Invalid API key or signature")
        elif e.response.status_code == 403:
            print("Authorization error: Access denied")
        elif e.response.status_code == 404:
            print("Not found: Order shipment does not exist")
        else:
            print(f"HTTP error: {e.response.status_code}")
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"Data error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run synchronous example
    example_sync()
    
    # Run async example (if asyncio is available)
    try:
        import asyncio
        asyncio.run(example_async())
    except ImportError:
        print("aiohttp not installed. Install with: pip install aiohttp")
    
    # Run error handling example
    example_with_error_handling() 