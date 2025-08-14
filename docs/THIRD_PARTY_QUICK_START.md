# 🔐 Third-Party API Access - Quick Start Guide

## Overview
This guide provides comprehensive information for third-party developers to access our API using API key authentication. The system supports both REST and GraphQL endpoints with secure authentication mechanisms.

## 🌍 Environment URLs

### Demo Environment
- **Admin API Base URL**: `https://admin-api.demo.fedshi.ice.global`
- **Web API Base URL**: `https://web-api.demo.fedshi.ice.global`

### Production Environment
- **Admin API Base URL**: `https://admin-api.app.fedshi.com`
- **Web API Base URL**: `https://web-api.app.fedshi.com`

## 🔑 Your Credentials
- **API Key**: `your-api-key-here`
- **Secret Key**: `your-128-character-secret-key-here` (64 bytes = 128 hex characters)

> **Note**: You will receive your specific API key, secret key, and allowed operations via email. Each API key has its own unique secret key for enhanced security.

## 📋 Required Headers
Every request must include these headers:

| Header | Description | Example |
|--------|-------------|---------|
| `X-API-Key` | Your API key | `your-api-key-here` |
| `X-API-Signature` | HMAC-SHA256 signature | `a1b2c3d4e5f6...` |
| `X-API-Timestamp` | RFC3339 timestamp | `2024-01-15T10:30:45Z` |
| `Content-Type` | Request content type | `application/json` |

## 🔐 Authentication Flow

### 1. API Key Authentication (Required for all requests)
All requests must be signed using your API key and secret key.

### 2. User Authentication (Required for protected operations)
Some GraphQL operations and REST endpoints require user authentication. You must:

1. **Login via REST endpoint** to get JWT token
2. **Include JWT token** in `Authorization: Bearer <token>` header for protected operations

## 🔐 Signature Generation

### String to Sign Format:
```
{HTTP_METHOD}\n{API_PATH}\n{REQUEST_BODY}\n{TIMESTAMP}\n{API_KEY}
```

### Example for GET request:
```
GET
/api/v1/third-party/export-order-shipment-receipt/NZQVP

2024-01-15T10:30:45Z
your-api-key-here
```

### Example for POST request with body(you can import this curl request to Postman):
```
curl --location 'https://admin-api.app.fedshi.com/graphql/third-party' \
--header 'X-API-Timestamp: 2025-07-30T15:34:31.596Z' \
--header 'X-API-Key: 88cab090f0e98a958970f7470cd322c2faff377905ed044a40706d4b066fb004' \
--header 'X-API-Signature: f3b925594f4e401f881e9427b199047446cf13306c63a4ca9d1fd8432874eb0c' \
--header 'Content-Type: application/json' \
--data '{"query":"\n      query ExportOrderShipmentReceipt($ID: FID!) {\n ExportOrderShipmentReceipt(OrderShipmentID: $ID) {\n Content\n Extension\n }\n }\n ","variables":{"ID":"NBFGO"}}'
```

Generate HMAC-SHA256 signature using your individual secret key.

## 🚀 API Endpoints

### REST API Endpoints

#### Third-Party Admin Login
- **Endpoint**: `POST /api/v1/third-party/admin/login`
- **Authentication**: API Key only
- **Purpose**: Get JWT token for protected operations
- **Required for**: Operations that need user context (e.g., `CreateOrderReconciliationV2`)

### GraphQL Endpoints

#### Third-Party GraphQL
- **Endpoint**: `POST /graphql/third-party`
- **Authentication**: API Key + Optional JWT Token
- **Purpose**: Access to all GraphQL operations
- **Required for**: All GraphQL operations

## 📝 Code Examples

### Python Implementation

```python
import hashlib
import hmac
import time
from datetime import datetime
import requests
import json

class ThirdPartyAPIClient:
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.jwt_token = None
    
    def generate_signature(self, method, path, body=""):
        timestamp = datetime.utcnow().isoformat() + 'Z'
        string_to_sign = f"{method}\n{path}\n{body}\n{timestamp}\n{self.api_key}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    def get_headers(self, method, path, body=""):
        signature, timestamp = self.generate_signature(method, path, body)
        
        headers = {
            'X-API-Key': self.api_key,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
            'Content-Type': 'application/json'
        }
        
        # Add JWT token if available for protected operations
        if self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
        
        return headers
    
    def login(self, email, password):
        """Login to get JWT token for protected operations"""
        method = 'POST'
        path = '/api/v1/third-party/admin/login'
        body = json.dumps({
            'Email': email,
            'Password': password
        })
        
        headers = self.get_headers(method, path, body)
        
        response = requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            data=body
        )
        
        if response.status_code == 200:
            result = response.json()
            self.jwt_token = result['data']['Token']
            return result
        else:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
    
    def make_graphql_request(self, query, variables=None):
        """Make GraphQL request"""
        method = 'POST'
        path = '/graphql/third-party'
        
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
        
        body = json.dumps(payload)
        headers = self.get_headers(method, path, body)
        
        response = requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            data=body
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"GraphQL request failed: {response.status_code} - {response.text}")
    
    def get_order_shipments(self, request_params=None):
        """Query OrderShipments"""
        query = """
        query OrderShipments($Request: OrderShipmentListRequest) {
            OrderShipments(Request: $Request) {
                OrderShipments {
                    ID
                    DeliveryStatus
                    DeliveryDate
                    OrderID
                    Date
                    ShipmentPrice
                    PayablePrice
                    User {
                        ID
                        Name
                        Email
                    }
                    Order {
                        ID
                        Total
                    }
                }
                Total
            }
        }
        """
        
        variables = {'Request': request_params} if request_params else {}
        return self.make_graphql_request(query, variables)
    
    def create_order_reconciliation_v2(self, request_data):
        """Create OrderReconciliationV2"""
        query = """
        mutation CreateOrderReconciliationV2($Request: CreateOrderReconciliationRequestV2!) {
            CreateOrderReconciliationV2(Request: $Request) {
                ID
                Courier
                Status
                NumberOfShipments
                TotalPaymentAmount
                TotalShippingCost
                CreatedAt
                UpdatedAt
            }
        }
        """
        
        variables = {'Request': request_data}
        return self.make_graphql_request(query, variables)

# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = ThirdPartyAPIClient(
        api_key="your-api-key-here",
        secret_key="your-128-character-secret-key-here",
        base_url="https://admin-api.app.fedshi.com"  # or demo URL
    )
    
    try:
        # Login to get JWT token (required for CreateOrderReconciliationV2)
        login_result = client.login("admin@example.com", "admin_password")
        print("Login successful:", login_result)
        
        # Query OrderShipments (API key only)
        shipments = client.get_order_shipments({
            "Page": 1,
            "PageSize": 10,
            "DeliveryStatus": ["delivered", "failed"]
        })
        print("OrderShipments:", shipments)
        
        # Create OrderReconciliationV2 (requires JWT token)
        reconciliation_data = {
            "SuccessfulOrderShipmentIDs": ["123", "456"],
            "FailedOrderShipmentIDs": [],
            "RejectedOrderShipmentIDs": [],
            "Courier": "FedEx"
        }
        
        result = client.create_order_reconciliation_v2(reconciliation_data)
        print("Reconciliation created:", result)
        
    except Exception as e:
        print(f"Error: {e}")
```

### JavaScript/Node.js Implementation

```javascript
const crypto = require('crypto');

class ThirdPartyAPIClient {
    constructor(apiKey, secretKey, baseUrl) {
        this.apiKey = apiKey;
        this.secretKey = secretKey;
        this.baseUrl = baseUrl;
        this.jwtToken = null;
    }
    
    generateSignature(method, path, body = '') {
        const timestamp = new Date().toISOString();
        const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${this.apiKey}`;
        
        const signature = crypto
            .createHmac('sha256', this.secretKey)
            .update(stringToSign)
            .digest('hex');
        
        return { signature, timestamp };
    }
    
    getHeaders(method, path, body = '') {
        const { signature, timestamp } = this.generateSignature(method, path, body);
        
        const headers = {
            'X-API-Key': this.apiKey,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
            'Content-Type': 'application/json'
        };
        
        // Add JWT token if available for protected operations
        if (this.jwtToken) {
            headers['Authorization'] = `Bearer ${this.jwtToken}`;
        }
        
        return headers;
    }
    
    async login(email, password) {
        const method = 'POST';
        const path = '/api/v1/third-party/admin/login';
        const body = JSON.stringify({
            Email: email,
            Password: password
        });
        
        const headers = this.getHeaders(method, path, body);
        
        const response = await fetch(`${this.baseUrl}${path}`, {
            method: 'POST',
            headers: headers,
            body: body
        });
        
        if (response.ok) {
            const result = await response.json();
            this.jwtToken = result.data.Token;
            return result;
        } else {
            throw new Error(`Login failed: ${response.status} - ${await response.text()}`);
        }
    }
    
    async makeGraphQLRequest(query, variables = null) {
        const method = 'POST';
        const path = '/graphql/third-party';
        
        const payload = { query };
        if (variables) {
            payload.variables = variables;
        }
        
        const body = JSON.stringify(payload);
        const headers = this.getHeaders(method, path, body);
        
        const response = await fetch(`${this.baseUrl}${path}`, {
            method: 'POST',
            headers: headers,
            body: body
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`GraphQL request failed: ${response.status} - ${await response.text()}`);
        }
    }
    
    async getOrderShipments(requestParams = null) {
        const query = `
            query OrderShipments($Request: OrderShipmentListRequest) {
                OrderShipments(Request: $Request) {
                    OrderShipments {
                        ID
                        DeliveryStatus
                        DeliveryDate
                        OrderID
                        Date
                        ShipmentPrice
                        PayablePrice
                        User {
                            ID
                            Name
                            Email
                        }
                        Order {
                            ID
                            Total
                        }
                    }
                    Total
                }
            }
        `;
        
        const variables = requestParams ? { Request: requestParams } : {};
        return await this.makeGraphQLRequest(query, variables);
    }
    
    async createOrderReconciliationV2(requestData) {
        const query = `
            mutation CreateOrderReconciliationV2($Request: CreateOrderReconciliationRequestV2!) {
                CreateOrderReconciliationV2(Request: $Request) {
                    ID
                    Courier
                    Status
                    NumberOfShipments
                    TotalPaymentAmount
                    TotalShippingCost
                    CreatedAt
                    UpdatedAt
                }
            }
        `;
        
        const variables = { Request: requestData };
        return await this.makeGraphQLRequest(query, variables);
    }
}

// Usage Example
async function main() {
    // Initialize client
    const client = new ThirdPartyAPIClient(
        'your-api-key-here',
        'your-128-character-secret-key-here',
        'https://admin-api.app.fedshi.com' // or demo URL
    );
    
    try {
        // Login to get JWT token (required for CreateOrderReconciliationV2)
        const loginResult = await client.login('admin@example.com', 'admin_password');
        console.log('Login successful:', loginResult);
        
        // Query OrderShipments (API key only)
        const shipments = await client.getOrderShipments({
            Page: 1,
            PageSize: 10,
            DeliveryStatus: ['delivered', 'failed']
        });
        console.log('OrderShipments:', shipments);
        
        // Create OrderReconciliationV2 (requires JWT token)
        const reconciliationData = {
            SuccessfulOrderShipmentIDs: ['123', '456'],
            FailedOrderShipmentIDs: [],
            RejectedOrderShipmentIDs: [],
            Courier: 'FedEx'
        };
        
        const result = await client.createOrderReconciliationV2(reconciliationData);
        console.log('Reconciliation created:', result);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run the example
main();
```

## 🔒 Security Considerations

### API Key Security
- **Never expose your secret key** in client-side code
- **Keep your secret key secure** and don't share it
- **Rotate your secret key** periodically if needed

### JWT Token Security
- **Store JWT tokens securely** in your application
- **Don't expose JWT tokens** in client-side code
- **Handle token expiration** gracefully

### Request Security
- **Always use HTTPS** in production
- **Validate timestamps** to prevent replay attacks

## ⚠️ Important Notes

1. **Timestamp**: Must be in RFC3339 format and within 5 minutes of server time
2. **Signature**: Must be generated using HMAC-SHA256 with your individual secret key
4. **HTTPS Only**: All requests must use HTTPS in production
5. **Keep Secrets Safe**: Never share your secret key in client-side code
6. **Unique Names**: API key names must be unique across the system

## 🆘 Common Issues

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Check API key and signature |
| `403 Forbidden` | Verify endpoint permissions and JWT token |
| `400 Bad Request` | Check timestamp format and validity |
| `422 Validation Error` | Verify request payload structure |

## 📞 Support

If you encounter any issues, please contact us with:
- Your API key (first 8 characters)
- Error message
- Request timestamp
- Endpoint you're trying to access
- Environment (demo/production)

---

**Ready to start?** Use the credentials provided via email and the code examples above to make your first API call! 🚀

## 📚 Additional Resources

- **Admin API** (used in the admin panel) – GraphQL schema available at: `https://admin-api.demo.fedshi.ice.global/`
- **Web API** (used by client apps such as iOS and Android) – GraphQL schema available at: `https://web-api.demo.fedshi.ice.global/`