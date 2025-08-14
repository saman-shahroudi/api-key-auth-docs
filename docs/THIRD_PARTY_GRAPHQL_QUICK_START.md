# Third-Party GraphQL API Quick Start Guide

## 🚀 Overview

This guide shows you how to authenticate and make GraphQL requests to the Fedshi Admin API using API key authentication. The API uses HMAC-SHA256 signatures for secure authentication.

## 🔑 Your Credentials
- **API Key**: `your-api-key-here`
- **Secret Key**: `your-128-character-secret-key-here` (64 bytes = 128 hex characters)
- **Base URL**: `https://admin-api.app.fedshi.com/graphql/third-party`

## 📋 Prerequisites

1. **API Key**: Generated from the Fedshi admin panel
2. **Secret Key**: 128-character secret key provided with your API key
3. **CryptoJS Library**: For HMAC-SHA256 signature generation (or use our standalone version)

## 🔐 Authentication

### Header Format
```javascript
{
  'X-API-Key': 'your-api-key-here',
  'X-API-Signature': 'hmac-sha256-signature',
  'X-API-Timestamp': '2024-01-01T12:00:00.000Z',
  'Content-Type': 'application/json'
}
```

### Signature Generation
```javascript
const timestamp = new Date().toISOString();
const method = 'POST';
const path = '/graphql/third-party';
const body = JSON.stringify({ query, variables });
const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${apiKey}`;
const signature = CryptoJS.HmacSHA256(stringToSign, secretKey).toString(CryptoJS.enc.Hex);
```

## 📝 GraphQL Examples

### 1. Export Order Shipment Receipt

**Query:**
```graphql
query ExportOrderShipmentReceipt($ID: FID!) {
  ExportOrderShipmentReceipt(OrderShipmentID: $ID) {
    Content
    Extension
  }
}
```

**Variables:**
```json
{
  "ID": "ABC123456789"
}
```

**JavaScript Example:**
```javascript
async function exportOrderShipmentReceipt(orderShipmentID) {
  const apiKey = 'your-api-key-here';
  const secretKey = 'your-128-character-secret-key-here';
  const baseUrl = 'https://admin-api.app.fedshi.com/graphql/third-party';
  
  const query = `
    query ExportOrderShipmentReceipt($ID: FID!) {
      ExportOrderShipmentReceipt(OrderShipmentID: $ID) {
        Content
        Extension
      }
    }
  `;
  
  const variables = { ID: orderShipmentID };
  const timestamp = new Date().toISOString();
  const method = 'POST';
  const path = '/graphql/third-party';
  const body = JSON.stringify({ query, variables });
  
  // Generate signature
  const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${apiKey}`;
  const signature = CryptoJS.HmacSHA256(stringToSign, secretKey).toString(CryptoJS.enc.Hex);
  
  // Make request
  const response = await fetch(baseUrl, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      'X-API-Signature': signature,
      'X-API-Timestamp': timestamp,
      'Content-Type': 'application/json'
    },
    body: body
  });
  
  const result = await response.json();
  
  if (result.data && result.data.ExportOrderShipmentReceipt) {
    const { Content, Extension } = result.data.ExportOrderShipmentReceipt;
    
    // Convert base64 to PDF
    const pdfBuffer = Buffer.from(Content, 'base64');
    
    // Save or process the PDF
    console.log('PDF generated successfully');
    console.log('File extension:', Extension);
    console.log('Content length:', Content.length);
    
    return { Content, Extension };
  } else {
    throw new Error('Failed to export receipt: ' + JSON.stringify(result.errors));
  }
}

// Usage
exportOrderShipmentReceipt('ABC123456789')
  .then(result => {
    console.log('Receipt exported successfully');
    // Save PDF to file
    const fs = require('fs');
    fs.writeFileSync('shipment_receipt.pdf', Buffer.from(result.Content, 'base64'));
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

**Python Example:**
```python
import requests
import hmac
import hashlib
import json
from datetime import datetime

def export_order_shipment_receipt(order_shipment_id):
    api_key = 'your-api-key-here'
    secret_key = 'your-128-character-secret-key-here'
    base_url = 'https://admin-api.app.fedshi.com/graphql/third-party'
    
    query = """
    query ExportOrderShipmentReceipt($ID: FID!) {
      ExportOrderShipmentReceipt(OrderShipmentID: $ID) {
        Content
        Extension
      }
    }
    """
    
    variables = {"ID": order_shipment_id}
    timestamp = datetime.utcnow().isoformat() + 'Z'
    method = 'POST'
    path = '/graphql/third-party'
    body = json.dumps({"query": query, "variables": variables})
    
    # Generate signature
    string_to_sign = f"{method}\n{path}\n{body}\n{timestamp}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Make request
    headers = {
        'X-API-Key': api_key,
        'X-API-Signature': signature,
        'X-API-Timestamp': timestamp,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(base_url, headers=headers, data=body)
    result = response.json()
    
    if 'data' in result and result['data']['ExportOrderShipmentReceipt']:
        content = result['data']['ExportOrderShipmentReceipt']['Content']
        extension = result['data']['ExportOrderShipmentReceipt']['Extension']
        
        # Save PDF
        import base64
        with open(f'shipment_receipt.{extension}', 'wb') as f:
            f.write(base64.b64decode(content))
        
        print(f"Receipt saved as shipment_receipt.{extension}")
        return result['data']['ExportOrderShipmentReceipt']
    else:
        raise Exception(f"Failed to export receipt: {result.get('errors', 'Unknown error')}")

# Usage
try:
    result = export_order_shipment_receipt('ABC123456789')
    print("Receipt exported successfully")
except Exception as e:
    print(f"Error: {e}")
```

### 2. Upload Shipment Pack (File Upload)

**Mutation:**
```graphql
mutation UploadCSV($file: Upload!) {
  UploadShipmentPack(Request: {CsvFile: $file}) {
    ID
  }
}
```

**JavaScript Example (with FormData):**
```javascript
async function uploadShipmentPack(csvFile) {
  const apiKey = 'your-api-key-here';
  const secretKey = 'your-128-character-secret-key-here';
  const baseUrl = 'https://admin-api.app.fedshi.com/graphql/third-party';
  
  const query = `
    mutation UploadCSV($file: Upload!) {
      UploadShipmentPack(Request: {CsvFile: $file}) {
        ID
      }
    }
  `;
  
  const variables = { file: null }; // placeholder for FormData
  const timestamp = new Date().toISOString();
  const method = 'POST';
  const path = '/graphql/third-party';
  const body = JSON.stringify({ query, variables });
  
  // Generate signature
  const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${apiKey}`;
  const signature = CryptoJS.HmacSHA256(stringToSign, secretKey).toString(CryptoJS.enc.Hex);
  
  // Create FormData for file upload
  const formData = new FormData();
  formData.append('operations', JSON.stringify({
    query: query,
    variables: { file: null }
  }));
  formData.append('map', JSON.stringify({
    0: ['variables.file']
  }));
  formData.append('0', csvFile);
  
  // Make request
  const response = await fetch(baseUrl, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      'X-API-Signature': signature,
      'X-API-Timestamp': timestamp
      // Don't set Content-Type for FormData
    },
    body: formData
  });
  
  const result = await response.json();
  
  if (result.data && result.data.UploadShipmentPack) {
    console.log('Shipment pack uploaded successfully');
    console.log('ID:', result.data.UploadShipmentPack.ID);
    return result.data.UploadShipmentPack;
  } else {
    throw new Error('Failed to upload shipment pack: ' + JSON.stringify(result.errors));
  }
}

// Usage
const fileInput = document.getElementById('csvFile');
const file = fileInput.files[0];

uploadShipmentPack(file)
  .then(result => {
    console.log('Upload successful, ID:', result.ID);
  })
  .catch(error => {
    console.error('Upload failed:', error.message);
  });
```

## 🔧 Complete JavaScript Client

```javascript
class FedshiGraphQLClient {
  constructor(apiKey, secretKey, baseUrl = 'https://admin-api.app.fedshi.com/graphql/third-party') {
    this.apiKey = apiKey;
    this.secretKey = secretKey;
    this.baseUrl = baseUrl;
  }
  
  generateSignature(method, path, body, timestamp) {
    const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${this.apiKey}`;
    return CryptoJS.HmacSHA256(stringToSign, this.secretKey).toString(CryptoJS.enc.Hex);
  }
  
  async makeRequest(query, variables = {}) {
    const timestamp = new Date().toISOString();
    const method = 'POST';
    const path = '/graphql/third-party';
    const body = JSON.stringify({ query, variables });
    
    const signature = this.generateSignature(method, path, body, timestamp);
    
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'X-API-Key': this.apiKey,
        'X-API-Signature': signature,
        'X-API-Timestamp': timestamp,
        'Content-Type': 'application/json'
      },
      body: body
    });
    
    const result = await response.json();
    
    if (result.errors) {
      throw new Error(`GraphQL Error: ${JSON.stringify(result.errors)}`);
    }
    
    return result.data;
  }
  
  async exportOrderShipmentReceipt(orderShipmentID) {
    const query = `
      query ExportOrderShipmentReceipt($ID: FID!) {
        ExportOrderShipmentReceipt(OrderShipmentID: $ID) {
          Content
          Extension
        }
      }
    `;
    
    const variables = { ID: orderShipmentID };
    const result = await this.makeRequest(query, variables);
    return result.ExportOrderShipmentReceipt;
  }
  
  async uploadShipmentPack(file) {
    const query = `
      mutation UploadCSV($file: Upload!) {
        UploadShipmentPack(Request: {CsvFile: $file}) {
          ID
        }
      }
    `;
    
    const variables = { file: null };
    const timestamp = new Date().toISOString();
    const method = 'POST';
    const path = '/graphql/third-party';
    const body = JSON.stringify({ query, variables });
    
    const signature = this.generateSignature(method, path, body, timestamp);
    
    const formData = new FormData();
    formData.append('operations', JSON.stringify({
      query: query,
      variables: { file: null }
    }));
    formData.append('map', JSON.stringify({
      0: ['variables.file']
    }));
    formData.append('0', file);
    
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'X-API-Key': this.apiKey,
        'X-API-Signature': signature,
        'X-API-Timestamp': timestamp
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (result.errors) {
      throw new Error(`GraphQL Error: ${JSON.stringify(result.errors)}`);
    }
    
    return result.data.UploadShipmentPack;
  }
}

// Usage
const client = new FedshiGraphQLClient(
  'your-api-key-here',
  'your-128-character-secret-key-here'
);

// Export receipt
client.exportOrderShipmentReceipt('ABC123456789')
  .then(receipt => {
    console.log('Receipt:', receipt);
    // Save PDF
    const pdfBuffer = Buffer.from(receipt.Content, 'base64');
    require('fs').writeFileSync('receipt.pdf', pdfBuffer);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });

// Upload shipment pack
const fileInput = document.getElementById('csvFile');
client.uploadShipmentPack(fileInput.files[0])
  .then(result => {
    console.log('Upload successful, ID:', result.ID);
  })
  .catch(error => {
    console.error('Upload failed:', error.message);
  });
```

## ⚠️ Important Notes

1. **Timestamp**: Must be in RFC3339 format and within 5 minutes of server time
2. **Signature**: Must be generated using HMAC-SHA256 with your secret key
3. **Rate Limiting**: API calls are rate-limited per API key
4. **HTTPS Only**: All requests must use HTTPS
5. **Keep Secrets Safe**: Never share your secret key in client-side code
6. **File Uploads**: Use FormData for file uploads, don't set Content-Type header
7. **Error Handling**: Always check for GraphQL errors in the response

## 🆘 Common Issues

### "Signature verification failed"
- Check that your secret key is correct
- Ensure timestamp is within 5 minutes of server time
- Verify the signature string format matches exactly

### "API key not found"
- Verify your API key is correct
- Check that the API key is active and not expired

### "File upload failed"
- Ensure you're using FormData for file uploads
- Don't set Content-Type header for FormData requests
- Check file size limits

### "GraphQL validation error"
- Verify your query syntax
- Check that all required variables are provided
- Ensure variable types match the schema

## 📞 Support

If you encounter any issues:
1. Check the browser console for detailed error messages
2. Verify your API credentials are correct
3. Ensure your timestamp is current
4. Contact support with error details and API key ID (not the secret key) 