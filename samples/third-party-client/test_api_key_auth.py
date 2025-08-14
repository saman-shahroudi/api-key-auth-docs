#!/usr/bin/env python3
"""
Test script for API key authentication
"""

import hashlib
import hmac
import json
import requests
from datetime import datetime

def generate_signature(method, path, body, api_key, master_secret, timestamp):
    """Generate HMAC-SHA256 signature"""
    string_to_sign = f"{method}\n{path}\n{body}\n{timestamp}\n{api_key}"
    signature = hmac.new(
        master_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def demonstrate_token_usage(login_token):
    """Demonstrate how to use the JWT token obtained from third-party login"""
    print("\n" + "="*70)
    print("🔑 DEMONSTRATION: Using JWT Token from Third-Party Login")
    print("="*70)
    
    # Configuration - Replace with your actual values
    API_KEY = "YOUR_API_AKY"  # Replace with actual API key from database
    
    # Get the secret key from environment variable
    import os
    API_KEY_SECRET = os.getenv('API_KEY_SECRET', "your_api_key_secret_here")
    
    if API_KEY_SECRET == "your_api_key_secret_here":
        print("⚠️  WARNING: Please set the API_KEY_SECRET environment variable")
        print("   Example: export API_KEY_SECRET='your_actual_secret_key'")
        return
    
    # Example: Use the token to make a GraphQL query
    test_query = {
        "base_url": "http://127.0.0.1:6001",
        "name": "Admin API - Using Login Token for GraphQL Query",
        "method": "POST",
        "path": "/graphql/third-party",
        "body": json.dumps({
            "query": """
            query {
              Users(Request: {
                Page: 1,
                PageSize: 5
              }) {
                Rows {
                  ID
                  Name
                  Email
                }
                Total
              }
            }
            """
        }),
        "headers": {
            "Authorization": f"Bearer {login_token}"
        }
    }
    
    # Generate timestamp and signature for API key auth
    timestamp = datetime.utcnow().isoformat() + 'Z'
    signature = generate_signature(
        test_query['method'],
        test_query['path'],
        test_query['body'],
        API_KEY,
        API_KEY_SECRET, # Use the individual secret key
        timestamp
    )
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'X-API-Signature': signature,
        'X-API-Timestamp': timestamp,
        'Authorization': f'Bearer {login_token}'
    }
    
    try:
        url = f"{test_query['base_url']}{test_query['path']}"
        print(f"Making authenticated request to: {url}")
        
        response = requests.post(
            url,
            headers=headers,
            data=test_query['body']
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS! Token is working correctly")
            print(f"Response: {response.text[:200]}...")
        else:
            print("❌ FAILED! Token might be invalid or expired")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_key_auth():
    # Configuration - Replace with your actual values
    API_KEY = "7955d98d73934bf57c49a242a0ca09386fdbef61a2ea194fdc6a61de08cd8ad2"  # Replace with actual API key from database
    API_KEY_SECRET = "399cdc6de88e376352094d02a619fabd8250825a95c31a2f1b966fb9139ba8b6"  # Replace with actual secret key from database

    
    WEB_JWT_TOKEN = "eyJhbGdvIjoiSFMyNTYiLCJ0eXBlIjoiSldUIn0=.eyJleHAiOiIxNzUzODIzODMzIiwiaWF0IjoiMTc1MzczNzQzMyIsImp0aSI6IkFDQ0VTUzoxODY6NTY4Y2Y3OTgtNDhmMy00MDQwLTkxMTItNjIxOTg4MDEyYmYzIiwic3ViIjoiMTg2In0=.2hDlnLHGehhIwUs_eCNcepCgtpa7c7neU_2Z0quBwhs="
    ADMIN_JWT_TOKEN = "eyJhbGdvIjoiSFMyNTYiLCJ0eXBlIjoiSldUIn0=.eyJleHAiOiIxNzUzODc5NjkwIiwiaWF0IjoiMTc1Mzc5MzI5MCIsImp0aSI6IkFDQ0VTUzo2MTozODU3MDJiMy0yZjlhLTQyYTEtOTIxNC1lMGQyMDAwNWE4ZDgiLCJzdWIiOiI2MSJ9._4TaJbE0FQ5erL5ybBTpCP99aY6K63APAC1sWZ1p97g="

    # Test endpoints
    test_endpoints = [
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Third Party Login (Success)",
            "method": "POST",
            "path": "/api/v1/third-party/admin/login",
            "body": json.dumps({
                "Email": "saman.shahroudi@ice.global",
                "Password": "Saman%1991"
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Third Party Login (Invalid Credentials)",
            "method": "POST",
            "path": "/api/v1/third-party/admin/login",
            "body": json.dumps({
                "Email": "saman.shahroudi@ice.global",
                "Password": "wrongpassword"
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Third Party Login (Invalid Email)",
            "method": "POST",
            "path": "/api/v1/third-party/admin/login",
            "body": json.dumps({
                "Email": "nonexistent@example.com",
                "Password": "adminpassword123"
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - CreateAPIKey with Admin Session",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                mutation {
                  CreateAPIKey(Request: {
                    Name: "Test API Key",
                    AllowedIPs: ["192.168.1.1", "127.0.0.1"],
                    ExpiresAt: "2025-07-24T22:00:35Z"
                  }) {
                    ExpiresAt
                    LastUsedAt
                    UpdatedAt
                  }
                }
                """
            }),
            "headers": {
                "Authorization": f"Bearer {ADMIN_JWT_TOKEN}"
            }
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - CreateAPIKey without Admin Session (should fail)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                mutation {
                  CreateAPIKey(Request: {
                    Name: "Test API Key",
                    AllowedIPs: ["192.168.1.1", "127.0.0.1"],
                    ExpiresAt: "2025-07-24T22:00:35Z"
                  }) {
                    ExpiresAt
                    LastUsedAt
                    UpdatedAt
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "REST Third Party Endpoint",
            "method": "GET",
            "path": "/api/v1/third-party/export-order-shipment-receipt/test123",
            "body": ""
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Named Query (GetOrders)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                query GetOrders {
                  Orders(Request: {
                    Page: 1,
                    PageSize: 10
                  }) {
                    Rows {
                      ID
                      OrderNumber
                    }
                    Total
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Anonymous Query (Orders)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                {
                  Orders(Request: { Page: 1, PageSize: 10 }) {
                    Orders {
                      ID
                    }
                    Total
                  }
                }
                """
            }),
            "headers": {
                        "Authorization": f"Bearer {ADMIN_JWT_TOKEN}"
            }
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - No Query Keyword (Orders)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                {
                  Orders(Request: {
                    Page: 1,
                    PageSize: 10
                  }) {
                    Rows {
                      ID
                      OrderNumber
                    }
                    Total
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Named Mutation (CreateBlock)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                mutation CreateBlock {
                  CreateBlock(Request: {
                    Title: "Test Block",
                    Content: "Test Content"
                  }) {
                    ID
                    Title
                    Content
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Anonymous Mutation (CreateBlock)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                mutation {
                  CreateBlock(Request: {
                    Title: "Test Block",
                    Content: "Test Content"
                  }) {
                    ID
                    Title
                    Content
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6002",
            "name": "Web API - Named Query (GetHome)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                query GetHome {
                  Home(Request: {
                    Page: 1,
                    PageSize: 10
                  }) {
                    HomeItems {
                      ID
                      __typename
                      ... on Product {
                        Name
                      }
                      ... on Advertisement {
                        Title
                      }
                    }
                    Total
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6002",
            "name": "Web API - Anonymous Query (Home)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                query {
                  Home(Request: {
                    Page: 1,
                    PageSize: 10
                  }) {
                    HomeItems {
                      ID
                      __typename
                      ... on Product {
                        Name
                      }
                      ... on Advertisement {
                        Title
                      }
                    }
                    Total
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6002",
            "name": "Web API - No Query Keyword (Home)",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                {
                  Home(Request: {
                    Page: 1,
                    PageSize: 10
                  }) {
                    HomeItems {
                      ID
                      __typename
                      ... on Product {
                        Name
                      }
                      ... on Advertisement {
                        Title
                      }
                    }
                    Total
                  }
                }
                """
            })
        },
        {
            "base_url": "http://127.0.0.1:6002",
            "name": "Web API - User Query with JWT",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                mutation {
                      CreateAPIKey(Request:{
                        Name:"Test API Key",
                        AllowedIPs: ["192.168.1.1", "127.0.0.1"]
                        ExpiresAt: "2025-07-24T22:00:35Z"
                      }) {
                        ExpiresAt
                        LastUsedAt
                        UpdatedAt
                      }
                    }
                """
            }),
            "use_jwt": True
        },
        {
            "base_url": "http://127.0.0.1:6002",
            "name": "Admin API - Create API Key",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                mutation CreateAPIKey {
                  CreateAPIKey(Request: {
                    Name: "Test API Key",
                    AllowedIPs: ["192.168.1.1", "127.0.0.1"],
                    AllowedEndpoints: ["/graphql/third-party"],
                    AllowedOperations: ["admin-api:Users", "admin-api:Orders"],
                    ExpiresAt: "2025-07-24T22:00:35Z"
                  }) {
                    ID
                    Name
                    Key
                    Status
                    AllowedIPs
                  }
                }
                """
            }),
            "use_jwt": True
        },
        {
            "base_url": "http://127.0.0.1:6001",
            "name": "Admin API - Create API Key",
            "method": "POST",
            "path": "/graphql/third-party",
            "body": json.dumps({
                "query": """
                query GetProductAnalytic($id: FID!) { ProductAnalytic(ProductID: $id) { DeliveryRateInfo { __typename ...ProductAnalyticInfoFragment } RPSInfo { __typename ...ProductAnalyticInfoFragment } } } fragment ProductAnalyticInfoFragment on ProductAnalyticInfo { Value Visible }
                """
            }),
            "use_jwt": True
        }
    ]
    
    for test in test_endpoints:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"URL: {test['base_url']}{test['path']}")
        print(f"Body: {test['body']}")
        
        # Generate timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Generate signature
        signature = generate_signature(
            test['method'],
            test['path'], 
            test['body'],
            API_KEY,
            API_KEY_SECRET, # Use the individual secret key
            timestamp
        )

        print(API_KEY)
        print(signature)
        print(timestamp)
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Linux"',
            'Referer': f"{test['base_url']}/",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'accept': 'application/json, multipart/mixed',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'X-API-Key': API_KEY,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
        }
        
        # Add JWT token for JWT required endpoints
        if test.get('use_jwt', False):
            headers['authorization'] = f'Bearer {WEB_JWT_TOKEN}'
            print("🔐 Using JWT token for authentication")
        elif test.get('use_jwt') is False:
            print("🚫 No JWT token - should fail with auth error")
        
        # Add custom headers if specified
        if 'headers' in test:
            headers.update(test['headers'])
            print(f"🔧 Added custom headers: {list(test['headers'].keys())}")
        
        # Make request
        try:
            url = f"{test['base_url']}{test['path']}"
            print(f"Making request to: {url}")
            
            response = requests.request(
                test['method'],
                url,
                headers=headers,
                data=test['body'] if test['method'] == 'POST' else None
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")  # First 500 chars
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                
                # If this is a login request and it's successful, extract the token for demonstration
                if "admin/login" in test['path'] and response.status_code == 200:
                    try:
                        response_data = response.json()
                        if 'data' in response_data and 'Token' in response_data['data']:
                            login_token = response_data['data']['Token']
                            print(f"🔑 Login successful! Token obtained: {login_token[:20]}...")
                            print("💡 You can now use this token for subsequent API calls with Authorization: Bearer <token>")
                            demonstrate_token_usage(login_token) # Call the new function
                    except:
                        pass
            else:
                print("❌ FAILED!")
                if test.get('use_jwt') is False:
                    print("   (Expected failure - JWT authentication required)")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing API Key Authentication with Different GraphQL Formats")
    print("=" * 70)
    test_api_key_auth() 