# Third-Party API Access System

## Overview

This document describes the comprehensive third-party API access system that provides secure, flexible, and scalable access to our APIs for external partners and integrations.

## Architecture

The system implements a **multi-layered security approach** with the following components:

### 1. **API Key Authentication Layer**
- **HMAC-SHA256 Signature Verification**: All requests must be signed using individual API key secrets
- **Timestamp Validation**: Prevents replay attacks with 5-minute clock skew tolerance
- **IP Whitelisting**: Restrict access to specific IP addresses or ranges
- **Endpoint Restrictions**: Control which endpoints each API key can access

### 2. **GraphQL Operation Validation Layer**
- **Operation-Level Authorization**: Control which GraphQL queries and mutations each API key can execute
- **Flexible Pattern Matching**: Support for exact matches, wildcards, and prefix patterns
- **Named Operation Support**: Validate both operation names and query content

### 3. **JWT Authentication Layer (Optional)**
- **Dual Authentication**: Support for both API key and JWT authentication simultaneously
- **User Session Management**: Enable user-specific queries when JWT is provided
- **Backward Compatibility**: API key-only clients continue to work

## Security Features

### API Key Management
```go
type APIKeyEntity struct {
    ID               uint64
    Name             string    // Unique constraint: (Name, FakeDelete)
    APIKey           string    // Unique constraint: (APIKey, FakeDelete)
    SecretKey        string    // 128 hex characters (64 bytes)
    Status           string
    AllowedIPs       []string
    AllowedEndpoints []string
    AllowedOperations []string
    ExpiresAt        *time.Time
    LastUsedAt       *time.Time
    CreatedAt        time.Time
    UpdatedAt        *time.Time
    FakeDelete       bool
}
```

**Key Constraints:**
- **Name Uniqueness**: API key names must be unique across the system
- **API Key Uniqueness**: API key values must be unique across the system
- **Secret Key Length**: 128 hex characters (64 bytes) for enhanced security

### **Empty Allowed Lists Behavior**

The system follows a **"Allow All"** approach when allowed lists are empty:

| Restriction | Empty List Behavior | Example |
|-------------|-------------------|---------|
| **AllowedIPs** | ✅ **ALL IPs are allowed** | `[]` → Any IP can access |
| **AllowedEndpoints** | ✅ **ALL endpoints are allowed** | `[]` → Any endpoint can be accessed |
| **AllowedOperations** | ✅ **ALL GraphQL operations are allowed** | `[]` → Any GraphQL query/mutation is allowed |

**Security Philosophy:**
- **Empty lists = No restrictions** (Allow All)
- **Non-empty lists = Explicit restrictions** (Deny by default, Allow only specified items)
- **This provides flexibility** for API keys that need broad access

**Example Configurations:**

```json
// API Key with NO restrictions (allows everything)
{
  "AllowedIPs": [],
  "AllowedEndpoints": [],
  "AllowedOperations": []
}

// API Key with IP restrictions only
{
  "AllowedIPs": ["192.168.1.100", "10.0.0.0/8"],
  "AllowedEndpoints": [],
  "AllowedOperations": []
}

// API Key with endpoint restrictions only
{
  "AllowedIPs": [],
  "AllowedEndpoints": ["/api/v1/third-party/export-order-shipment-receipt/*"],
  "AllowedOperations": []
}

// API Key with GraphQL operation restrictions only
{
  "AllowedIPs": [],
  "AllowedEndpoints": [],
  "AllowedOperations": ["admin-api:Users", "admin-api:Orders"]
}

// API Key with all restrictions
{
  "AllowedIPs": ["192.168.1.100"],
  "AllowedEndpoints": ["/api/v1/third-party/*"],
  "AllowedOperations": ["admin-api:Users"]
}
```

### Individual Secret Key System

Each API key now has its own unique secret key for enhanced security:

- **Individual Secrets**: Each API key has a unique 64-byte secret key (128 hex characters)
- **Auto-Generation**: Secret keys are automatically generated when creating new API keys
- **Secure Storage**: Secret keys are never exposed through the API
- **Isolation**: Compromising one API key doesn't affect others

### GraphQL Operation Validation

The system supports flexible operation validation patterns with **app-specific operation names** to avoid conflicts between admin-api and web-api:

#### **App-Specific Operation Names**

Since both admin-api and web-api might have operations with the same name (e.g., `Users`), the system creates unique identifiers by combining the app name with the operation name:

| App | Operation | Unique Identifier |
|-----|-----------|-------------------|
| admin-api | Users | `admin-api:Users` |
| web-api | Users | `web-api:Users` |

#### **Exact Match**
```json
{
  "AllowedOperations": ["admin-api:Users", "web-api:Home", "admin-api:CreateUser"]
}
```

#### **Wildcard Patterns**
```json
{
  "AllowedOperations": ["admin-api:User*", "web-api:Product*", "*"]
}
```

#### **Prefix Matching**
```json
{
  "AllowedOperations": ["admin-api:Get*", "web-api:Create*", "admin-api:Update*"]
}
```

### **How It Works**

1. **App Detection**: Uses `service.DI().App().Name` to get the current app name
2. **Operation Extraction**: Parses GraphQL query to extract actual query/mutation names
3. **Unique Identifier**: Creates `{app-name}:{operation-name}` format
4. **Pattern Matching**: Checks against allowed operations list
5. **Backward Compatibility**: Also checks operation name without app prefix

### **Operation Extraction**

The system extracts **actual field names** from GraphQL queries using multiple strategies:

1. **Named Operations**: `query GetOrders { Orders { ... } }` → `Orders`
2. **Anonymous Operations**: `query { Orders { ... } }` → `Orders`
3. **No Query Keyword**: `{ Orders { ... } }` → `Orders`
4. **Mutations**: `mutation CreateBlock { CreateBlock { ... } }` → `CreateBlock`

### **Example Validations**

```graphql
# This query would be allowed if "admin-api:Orders" is in AllowedOperations
query GetOrders {
  Orders(Request: OrderListRequest) {
    Rows { ID OrderNumber }
  }
}

# This query would be allowed if "admin-api:Orders" is in AllowedOperations
query {
  Orders(Request: OrderListRequest) {
    Rows { ID OrderNumber }
  }
}

# This query would be allowed if "admin-api:Orders" is in AllowedOperations
{
  Orders(Request: OrderListRequest) {
    Rows { ID OrderNumber }
  }
}

# This mutation would be allowed if "admin-api:CreateBlock" is in AllowedOperations
mutation CreateBlock {
  CreateBlock(Request: CreateBlockInput!) {
    ID Title Content
  }
}
```

### **Operation Name Examples**

| GraphQL Query Format | Extracted Operation | App-Specific Identifier |
|---------------------|-------------------|------------------------|
| `query GetOrders { Orders { ... } }` | `Orders` | `admin-api:Orders` |
| `query { Orders { ... } }` | `Orders` | `admin-api:Orders` |
| `{ Orders { ... } }` | `Orders` | `admin-api:Orders` |
| `mutation CreateBlock { CreateBlock { ... } }` | `CreateBlock` | `admin-api:CreateBlock` |
| `query GetHome { Home { ... } }` | `Home` | `web-api:Home` |
| `{ Home { ... } }` | `Home` | `web-api:Home` |

### **Backward Compatibility**

- Existing API keys without app-specific operations will work
- Operations without app prefix are still supported
- REST endpoints are not affected by operation validation

### Authentication Flow

```
1. API Key Validation (Required)
   ├── Validate API key exists and is active
   ├── Check signature using HMAC-SHA256 with individual secret key
   ├── Validate timestamp (prevent replay attacks)
   ├── Check IP restrictions
   ├── Check endpoint permissions
   └── Check GraphQL operation permissions

2. JWT Validation (Optional)
   ├── If Authorization header present
   ├── Validate JWT token
   ├── Set up user session
   └── Enable @requireLogin directives

3. Request Processing
   ├── GraphQL query execution
   ├── Rate limiting checks
   └── Response with rate limit info
```

## API Usage Examples

### **REST API Example**

```bash
curl -X GET "http://127.0.0.1:6001/api/v1/third-party/export-order-shipment-receipt/123" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Signature: generated-signature" \
  -H "X-API-Timestamp: 2024-01-15T10:30:00Z"
```

### **GraphQL API Example**

```bash
curl -X POST "http://127.0.0.1:6002/graphql/third-party" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Signature: generated-signature" \
  -H "X-API-Timestamp: 2024-01-15T10:30:00Z" \
  -d '{
    "query": "query GetUsers { Users { ID Name } }",
    "operationName": "GetUsers"
  }'
```

### **Dual Authentication Example**

```bash
curl -X POST "http://127.0.0.1:6002/graphql/third-party" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Signature: generated-signature" \
  -H "X-API-Timestamp: 2024-01-15T10:30:00Z" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "query": "query GetUser { User { ID Name } }"
  }'
```

### **Third-Party Admin Login Example**

```bash
curl -X POST "http://127.0.0.1:6002/api/v1/third-party/admin/login" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Signature: generated-signature" \
  -H "X-API-Timestamp: 2024-01-15T10:30:00Z" \
  -d '{
    "email": "admin@example.com",
    "password": "admin_password"
  }'
```

## Configuration

### **Environment Variables**

The system uses individual secret keys for each API key, so no master secret environment variable is needed.

### **Database Schema**

```sql
-- API keys table with individual secret keys
CREATE TABLE api_keys (
    ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    APIKey VARCHAR(64) NOT NULL UNIQUE,
    SecretKey VARCHAR(64) NOT NULL,  -- Individual secret key
    Status VARCHAR(20) NOT NULL,
    AllowedIPs JSON,
    AllowedEndpoints JSON,
    AllowedOperations JSON,
    ExpiresAt TIMESTAMP NULL,
    LastUsedAt TIMESTAMP NULL,
    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP NULL,
    FakeDelete BOOLEAN NOT NULL DEFAULT FALSE
);
```

## Logging and Monitoring

### **Structured Logging**

All API key access attempts are logged with detailed information:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "SUCCESS",
  "ip_address": "192.168.1.100",
  "method": "POST",
  "endpoint": "/graphql/third-party",
  "api_key_id": 123,
  "api_key_name": "Partner Integration",
  "api_key_masked": "7955d98d...8ad2",
  "user_agent": "curl/7.68.0",
  "response_time_ms": 45,
  "request_id": "req-123"
}
```

### **Failure Reasons**

- `missing_required_headers`: Missing API key, signature, or timestamp
- `invalid_timestamp`: Timestamp too old or in future
- `api_key_not_found`: API key doesn't exist
- `inactive_api_key`: API key is not active
- `expired_api_key`: API key has expired
- `ip_not_allowed`: IP address not in whitelist
- `endpoint_not_allowed`: Endpoint not in allowed list
- `operation_not_allowed`: GraphQL operation not permitted
- `invalid_signature`: HMAC signature verification failed

## Security Best Practices

### **API Key Management**
- Regularly rotate API keys
- Set appropriate expiration dates
- Monitor API key usage patterns
- Use individual secret keys for each API key

### **Secret Key Management**
- **Never expose secret keys through the API**
- **Use secure channels** for sharing secret keys with clients
- **Rotate secret keys** periodically for high-security applications
- **Store secret keys securely** on the client side

### **IP Restrictions**
- Whitelist only necessary IP addresses
- Use CIDR notation for IP ranges
- Regularly review and update IP lists

### **Operation Permissions**
- Follow principle of least privilege
- Grant only necessary GraphQL operations
- Use wildcard patterns carefully
- Regularly audit operation permissions

### **Signature Security**
- Keep individual secret keys secure and confidential
- Use different secret keys for different environments
- Regularly rotate secret keys
- Monitor for signature validation failures

## Testing

### **Test Scripts**

Use the provided test scripts to verify functionality:

```bash
# Set the secret key for your API key
export API_KEY_SECRET='your_individual_secret_key'

# Python test script
python3 test_api_key_auth.py

# Manual curl testing
curl -X POST "http://127.0.0.1:6002/graphql/third-party" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Signature: $(generate_signature)" \
  -H "X-API-Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -d '{"query": "query { Home { Total } }"}'
```

### **Test Cases**

1. **Valid API Key**: Should succeed with proper signature
2. **Invalid API Key**: Should fail with 401
3. **Expired API Key**: Should fail with 401
4. **Invalid Signature**: Should fail with 401
5. **Invalid Timestamp**: Should fail with 401
6. **IP Not Allowed**: Should fail with 403
7. **Endpoint Not Allowed**: Should fail with 403
8. **Operation Not Allowed**: Should fail with 403
9. **Dual Authentication**: Should work with both API key and JWT
10. **Rate Limiting**: Should respect rate limits
11. **Third-Party Admin Login**: Should work with API key authentication

## Troubleshooting

### **Common Issues**

1. **"Invalid signature"**: Check individual secret key and signature generation
2. **"Timestamp too old"**: Check system clock synchronization
3. **"Operation not allowed"**: Verify GraphQL operation is in allowed list
4. **"IP not allowed"**: Check IP whitelist configuration
5. **"JWT authentication failed"**: Verify JWT token validity
6. **"Missing secret key"**: Ensure API key has a secret key in database

### **Debug Information**

Enable debug logging to see detailed request processing:

```go
log.Printf("[API_KEY_ACCESS] Attempt - IP: %s, Endpoint: %s %s, API Key: %s",
    clientIP, method, endpoint, maskAPIKey(apiKey))
```

## Migration Guide

### **From Master Secret to Individual Secret Keys**

1. **Database Migration**: Add `SecretKey` column to `api_keys` table
2. **Generate Secret Keys**: Create unique secret keys for existing API keys
3. **Update Clients**: Share new secret keys securely with API key owners
4. **Update Code**: Remove master secret references
5. **Test Thoroughly**: Verify all functionality works with individual secrets

### **Adding GraphQL Operation Validation**

1. **Database Migration**: Add `AllowedOperations` column to `api_keys` table
2. **Update Entities**: Add field to `APIKeyEntity` and domain model
3. **Update GraphQL Schema**: Regenerate models with new field
4. **Update Middleware**: Add operation validation logic
5. **Test Thoroughly**: Verify all existing functionality still works

### **Backward Compatibility**

- Existing API keys without `AllowedOperations` will work (no restrictions)
- Empty `AllowedOperations` array means no restrictions
- REST endpoints are not affected by operation validation
- Individual secret keys provide better security isolation

## Future Enhancements

### **Planned Features**
- **Real-time Monitoring**: Live dashboard for API key usage
- **Secret Key Rotation**: Automated secret key rotation
- **Advanced Analytics**: Detailed usage analytics and reporting
- **Webhook Support**: Real-time notifications for API key events

---

This system provides a robust, secure, and flexible foundation for third-party API access while maintaining backward compatibility and supporting future enhancements. 