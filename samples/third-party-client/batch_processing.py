#!/usr/bin/env python3
"""
Batch Processing Example

This script demonstrates how to process multiple order shipment receipts
in batch using the Fedshi Third-Party API Client.
"""

import asyncio
import os
import time
from typing import List
from third_party_client import ThirdPartyAPIClient, ThirdPartyAPIClientAsync


def batch_process_sync(order_shipment_ids: List[str]):
    """
    Process multiple receipts synchronously
    """
    # Configuration
    API_KEY = os.getenv('API_KEY', 'your_api_key_here')
    MASTER_SECRET = os.getenv('MASTER_SECRET', 'your_master_secret_here')
    BASE_URL = os.getenv('BASE_URL', 'https://api.loveyourself.co.uk')
    
    client = ThirdPartyAPIClient(API_KEY, MASTER_SECRET, BASE_URL)
    
    print(f"🔄 Processing {len(order_shipment_ids)} receipts synchronously...")
    start_time = time.time()
    
    successful = 0
    failed = 0
    
    for i, shipment_id in enumerate(order_shipment_ids, 1):
        try:
            print(f"📄 Processing {i}/{len(order_shipment_ids)}: {shipment_id}")
            
            receipt = client.export_order_shipment_receipt(shipment_id)
            
            if receipt.get('success'):
                filename = f"receipt_{shipment_id}.pdf"
                client.save_receipt_to_file(receipt, filename)
                print(f"✅ Success: {shipment_id} -> {filename}")
                successful += 1
            else:
                print(f"❌ Failed: {shipment_id} - {receipt.get('error', 'Unknown error')}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error processing {shipment_id}: {e}")
            failed += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n📊 Batch Processing Complete!")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Average time per receipt: {duration/len(order_shipment_ids):.2f} seconds")


async def batch_process_async(order_shipment_ids: List[str]):
    """
    Process multiple receipts asynchronously (much faster!)
    """
    # Configuration
    API_KEY = os.getenv('API_KEY', 'your_api_key_here')
    MASTER_SECRET = os.getenv('MASTER_SECRET', 'your_master_secret_here')
    BASE_URL = os.getenv('BASE_URL', 'https://api.loveyourself.co.uk')
    
    client = ThirdPartyAPIClientAsync(API_KEY, MASTER_SECRET, BASE_URL)
    
    print(f"🔄 Processing {len(order_shipment_ids)} receipts asynchronously...")
    start_time = time.time()
    
    # Create tasks for all receipts
    tasks = []
    for shipment_id in order_shipment_ids:
        task = process_single_receipt_async(client, shipment_id)
        tasks.append(task)
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Count results
    successful = sum(1 for result in results if result is True)
    failed = len(results) - successful
    
    print(f"\n📊 Async Batch Processing Complete!")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Average time per receipt: {duration/len(order_shipment_ids):.2f} seconds")
    
    # Show speed improvement
    sync_estimate = len(order_shipment_ids) * 2  # Assume 2 seconds per request
    speedup = sync_estimate / duration if duration > 0 else 0
    print(f"🚀 Speed improvement: ~{speedup:.1f}x faster than sequential processing")


async def process_single_receipt_async(client, shipment_id: str) -> bool:
    """
    Process a single receipt asynchronously
    """
    try:
        receipt = await client.export_order_shipment_receipt(shipment_id)
        
        if receipt.get('success'):
            # Save the receipt (synchronous operation)
            filename = f"receipt_{shipment_id}.pdf"
            
            # Decode and save
            import base64
            content = receipt['data']['content']
            pdf_content = base64.b64decode(content)
            
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            
            print(f"✅ {shipment_id} -> {filename}")
            return True
        else:
            print(f"❌ {shipment_id} - {receipt.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {shipment_id}: {e}")
        return False


def main():
    # Example order shipment IDs (replace with actual FIDs)
    order_shipment_ids = [
        'ABC123',
        'DEF456', 
        'GHI789',
        'JKL012',
        'MNO345',
        'PQR678',
        'STU901',
        'VWX234'
    ]
    
    print("🚀 Fedshi Third-Party API Batch Processing Example")
    print("=" * 50)
    
    # Check if aiohttp is available for async processing
    try:
        import aiohttp
        print("\n1️⃣ Running ASYNC batch processing (recommended)...")
        asyncio.run(batch_process_async(order_shipment_ids))
        
        print("\n2️⃣ Running SYNC batch processing for comparison...")
        batch_process_sync(order_shipment_ids)
        
    except ImportError:
        print("⚠️  aiohttp not installed. Install with: pip install aiohttp")
        print("📦 Running SYNC batch processing only...")
        batch_process_sync(order_shipment_ids)


if __name__ == "__main__":
    main() 