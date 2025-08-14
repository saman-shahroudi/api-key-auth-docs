# Third-Party API Client Examples

This directory contains client SDKs and examples for integrating with the Third-Party API.

## 📁 Files

- `third_party_client.py` - Complete Python SDK with sync and async support
- `third_party_client.js` - JavaScript/Node.js SDK
- `simple_example.py` - Basic usage example
- `batch_processing.py` - Batch processing example
- `requirements.txt` - Python dependencies
- `README.md` - This file

## 🐍 Python Client

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install requests aiohttp
```

### Basic Usage

```python
from third_party_client import ThirdPartyAPIClient

# Initialize client
client = ThirdPartyAPIClient(
    api_key='your_api_key_here',
    secret_key='your_individual_secret_key_here',  # Individual secret key for this API key
    base_url='https://url.com'
)

# Export a receipt
receipt = client.export_order_shipment_receipt('ABC123')

# Save to file
client.save_receipt_to_file(receipt, 'receipt.pdf')
```

### Async Usage (Faster for multiple requests)

```python
import asyncio
from third_party_client import ThirdPartyAPIClientAsync

async def main():
    client = ThirdPartyAPIClientAsync(
        api_key='your_api_key_here',
        secret_key='your_individual_secret_key_here'  # Individual secret key
    )
    
    # Export multiple receipts concurrently
    receipts = await asyncio.gather(*[
        client.export_order_shipment_receipt('ABC123'),
        client.export_order_shipment_receipt('DEF456'),
        client.export_order_shipment_receipt('GHI789')
    ])

asyncio.run(main())
```

### Environment Variables

You can use environment variables for configuration:

```bash
export API_KEY="your_api_key_here"
export API_KEY_SECRET="your_individual_secret_key_here"
export BASE_URL="https://api.loveyourself.co.uk"
```

Then in your code:

```python
import os

client = ThirdPartyAPIClient(
    api_key=os.getenv('API_KEY'),
    secret_key=os.getenv('API_KEY_SECRET'),
    base_url=os.getenv('BASE_URL')
)
```

## 🟨 JavaScript Client

### Installation

```bash
npm install crypto
```

### Usage

```javascript
const ThirdPartyAPIClient = require('./third_party_client.js');

const client = new ThirdPartyAPIClient(
    'your_api_key_here',
    'your_individual_secret_key_here',  // Individual secret key
    'https://url.com'
);

// Export a receipt
client.exportOrderShipmentReceipt('ABC123')
    .then(receipt => {
        console.log('Receipt generated:', receipt);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

## 🚀 Running Examples

### Simple Example

```bash
# Set environment variables
export API_KEY="your_api_key"
export API_KEY_SECRET="your_individual_secret_key"

# Run the example
python simple_example.py
```

### Batch Processing

```bash
# Process multiple receipts
python batch_processing.py
```

## 🔧 API Endpoints

### Export Order Shipment Receipt

- **Method**: `GET`
- **Path**: `/api/v1/third-party/export-order-shipment-receipt/{orderShipmentID}`
- **Headers**: 
  - `X-API-Key`: Your API key
  - `X-API-Signature`: HMAC signature
  - `X-API-Timestamp`: RFC3339 timestamp

### Third-Party Admin Login

- **Method**: `POST`
- **Path**: `/api/v1/third-party/admin/login`
- **Headers**: 
  - `X-API-Key`: Your API key
  - `X-API-Signature`: HMAC signature
  - `X-API-Timestamp`: RFC3339 timestamp
- **Body**: `{"email": "admin@example.com", "password": "admin_password"}`
- **Response**: JWT access token and refresh token

### GraphQL Third-Party Endpoint

- **Method**: `POST`
- **Path**: `/graphql/third-party`
- **Headers**: 
  - `X-API-Key`: Your API key
  - `X-API-Signature`: HMAC signature
  - `X-API-Timestamp`: RFC3339 timestamp
  - `Authorization`: Bearer JWT token (optional)

### Response Format

```json
{
  "success": true,
  "data": {
    "content": "base64_encoded_pdf_content",
    "extension": "pdf"
  }
}
```

## 🔐 Authentication

The API uses HMAC-SHA256 signature authentication with an **individual secret key system**:

1. **Generate timestamp**: Current time in RFC3339 format
2. **Create signature string**: `{method}\n{path}\n{body}\n{timestamp}\n{api_key}`
3. **Generate HMAC**: SHA256 hash using the individual secret key for this API key
4. **Send headers**: Include API key, signature, and timestamp

### 🔒 Individual Secret Key System

- **Individual Secrets**: Each API key has its own unique 32-byte secret key
- **Auto-Generation**: Secret keys are automatically generated when creating new API keys
- **Secure Storage**: Secret keys are never exposed through the API
- **Isolation**: Compromising one API key doesn't affect others

### 🔒 Secret Management

- **Individual Secret Keys**: Each API key has its own unique secret key
- **Secure Distribution**: Secret keys must be shared through secure channels (not via API)
- **Environment Variable**: Store individual secret keys securely in environment variables
- **Security**: Database breaches don't expose all secrets (only individual ones)

See `docs/API_KEY_SECRET_SYSTEM.md` for detailed information about the individual secret key approach.

## ⚡ Performance Tips

### For Multiple Requests

1. **Use async client** for better performance
2. **Batch requests** when possible
3. **Reuse client instances** instead of creating new ones

### Example: Async Batch Processing

```python
import asyncio
from third_party_client import ThirdPartyAPIClientAsync

async def process_receipts(shipment_ids):
    client = ThirdPartyAPIClientAsync(api_key, secret_key)
    
    # Process all receipts concurrently
    tasks = [
        client.export_order_shipment_receipt(sid) 
        for sid in shipment_ids
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Usage
shipment_ids = ['ABC123', 'DEF456', 'GHI789']
results = asyncio.run(process_receipts(shipment_ids))
```

## 🛠️ Error Handling

### Common Errors

- **401 Unauthorized**: Invalid API key or signature
- **403 Forbidden**: IP not allowed or endpoint not permitted
- **404 Not Found**: Order shipment doesn't exist
- **429 Too Many Requests**: Rate limit exceeded

### Error Handling Example

```python
try:
    receipt = client.export_order_shipment_receipt('ABC123')
    client.save_receipt_to_file(receipt, 'receipt.pdf')
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - check API key and secret key")
    elif e.response.status_code == 403:
        print("Access denied - check IP restrictions")
    elif e.response.status_code == 404:
        print("Order shipment not found")
    else:
        print(f"HTTP error: {e.response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## 📊 Monitoring

The API provides usage statistics and audit logs:

- All requests are logged with timestamps
- IP addresses are recorded for security
- Failed authentication attempts are tracked
- Usage patterns can be monitored

## 🔒 Security Best Practices

1. **Keep secrets secure**: Never commit API secrets to version control
3. **Rotate keys regularly**: Update API keys and secret keys periodically
4. **Monitor usage**: Check API usage logs for suspicious activity
5. **Use IP restrictions**: Limit API access to specific IP addresses
6. **Individual secrets**: Use individual secret keys for each API key
7. **Secure distribution**: Share secret keys through secure channels only

## 📞 Support

For API support and questions:

- Check the main documentation: `docs/THIRD_PARTY_API_ACCESS.md`
- Review the secret key system: `docs/API_KEY_SECRET_SYSTEM.md`
- Review error messages for troubleshooting
- Contact the development team for assistance 