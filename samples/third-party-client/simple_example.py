#!/usr/bin/env python3
"""
Simple example of using the LYS Third-Party API Client

This script demonstrates basic usage of the API client to export
order shipment receipts.
"""

from third_party_client import ThirdPartyAPIClient
import base64
import os


def main():
    # Configuration - Replace with your actual credentials
    API_KEY = os.getenv('API_KEY', 'your_api_key')
    MASTER_SECRET = os.getenv('MASTER_SECRET', 'master_secret')
    BASE_URL = os.getenv('BASE_URL', 'https://url.com/')
    
    # Order shipment ID to export (replace with actual FID)
    ORDER_SHIPMENT_ID = 'SHIPMENT_ID'
    
    # Initialize the client
    print("Initializing API client...")
    client = ThirdPartyAPIClient(
        api_key=API_KEY,
        master_secret=MASTER_SECRET,
        base_url=BASE_URL
    )
    
    try:
        # Export the receipt
        print(f"Exporting receipt for order shipment: {ORDER_SHIPMENT_ID}")
        receipt = client.export_order_shipment_receipt(ORDER_SHIPMENT_ID)
        
        # Check if the request was successful
        if receipt.get('success'):
            print("✅ Receipt generated successfully!")
            
            # Get receipt data
            data = receipt['data']
            content = data['content']
            extension = data['extension']
            
            print(f"📄 File extension: {extension}")
            print(f"📊 Content size: {len(content)} characters")
            
            # Save to file
            filename = f"receipt_{ORDER_SHIPMENT_ID}.{extension}"
            client.save_receipt_to_file(receipt, filename)
            print(f"💾 Receipt saved as: {filename}")
            
            # Optional: Display file size
            file_size = os.path.getsize(filename)
            print(f"📁 File size: {file_size} bytes")
            
        else:
            print("❌ Failed to generate receipt")
            print(f"Error: {receipt.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 