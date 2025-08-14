/**
 * Third-Party API Client SDK
 * 
 * This SDK provides easy access to the third-party API endpoints
 * using API key authentication with HMAC signature verification.
 */

const crypto = require('crypto');

class ThirdPartyAPIClient {
    /**
     * Initialize the client with API credentials
     * @param {string} apiKey - The API key provided by Fedshi
     * @param {string} secret - The secret key for signature generation
     * @param {string} baseUrl - Base URL of the API (default: production)
     */
    constructor(apiKey, secret, baseUrl = 'https://your-domain.com') {
        this.apiKey = apiKey;
        this.secret = secret;
        this.baseUrl = baseUrl;
    }

    /**
     * Generate HMAC signature for request authentication
     * @param {string} method - HTTP method (GET, POST, etc.)
     * @param {string} path - API endpoint path
     * @param {string} body - Request body (empty for GET requests)
     * @param {string} timestamp - RFC3339 timestamp
     * @returns {string} - Hex-encoded HMAC signature
     */
    generateSignature(method, path, body, timestamp) {
        const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${this.apiKey}`;
        const hmac = crypto.createHmac('sha256', this.secret);
        hmac.update(stringToSign);
        return hmac.digest('hex');
    }

    /**
     * Make an authenticated request to the API
     * @param {string} method - HTTP method
     * @param {string} path - API endpoint path
     * @param {Object} body - Request body (optional)
     * @returns {Promise<Object>} - API response
     */
    async makeRequest(method, path, body = null) {
        const timestamp = new Date().toISOString();
        const bodyString = body ? JSON.stringify(body) : '';
        
        const signature = this.generateSignature(method, path, bodyString, timestamp);
        
        const headers = {
            'X-API-Key': this.apiKey,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
            'Content-Type': 'application/json'
        };

        const url = `${this.baseUrl}${path}`;
        
        const response = await fetch(url, {
            method,
            headers,
            body: bodyString || undefined
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorData.error || 'Unknown error'}`);
        }

        return response.json();
    }

    /**
     * Export order shipment receipt as PDF
     * @param {string} orderShipmentID - The FID of the order shipment
     * @returns {Promise<Object>} - Response containing base64 PDF data
     */
    async exportOrderShipmentReceipt(orderShipmentID) {
        const path = `/api/v1/third-party/export-order-shipment-receipt/${orderShipmentID}`;
        return this.makeRequest('GET', path);
    }

    /**
     * Get API usage statistics (if available)
     * @returns {Promise<Object>} - Usage statistics
     */
    async getUsageStats() {
        const path = '/api/v1/third-party/usage-stats';
        return this.makeRequest('GET', path);
    }
}

// Example usage
async function example() {
    const client = new ThirdPartyAPIClient(
        'your_api_key_here',
        'your_secret_here',
        'https://api.loveyourself.co.uk'
    );

    try {
        // Export a shipment receipt
        const receipt = await client.exportOrderShipmentReceipt('ABC123');
        console.log('Receipt generated successfully');
        console.log('Content length:', receipt.data.content.length);
        console.log('File extension:', receipt.data.extension);
        
        // Save the PDF to a file
        const fs = require('fs');
        const pdfBuffer = Buffer.from(receipt.data.content, 'base64');
        fs.writeFileSync('shipment_receipt.pdf', pdfBuffer);
        console.log('PDF saved as shipment_receipt.pdf');
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Node.js usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThirdPartyAPIClient;
}

// Browser usage
if (typeof window !== 'undefined') {
    window.ThirdPartyAPIClient = ThirdPartyAPIClient;
} 