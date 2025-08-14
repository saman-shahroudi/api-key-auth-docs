/**
 * Fedshi Integration Tool - Main Application
 * 
 * A comprehensive tool for Fedshi services
 * to streamline shipment processing operations.
 */

class FedshiIntegrationApp {
    constructor() {
        this.config = null;
        this.fedshiClient = null;
        this.fedshiJwtToken = null;
        this.authenticationStatus = {
            fedshi: false
        };
        this.processingResults = {
            failed: [],
            success: [],
            data: []
        };
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            await this.loadConfiguration();
            this.setupEventListeners();
            this.updateAuthenticationStatus();
            console.log('Fedshi Integration Tool initialized successfully');
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.showMessage('Failed to initialize application. Please check the console for details.', 'error');
        }
    }

    /**
     * Load configuration from config.json
     */
    async loadConfiguration() {
        try {
            const response = await fetch('config.json');
            if (!response.ok) {
                throw new Error(`Failed to load config.json: ${response.status}`);
            }
            this.config = await response.json();
            
            // Initialize client with configuration
            this.fedshiClient = new FedshiAPIClient(
                this.config.fedshi.apiKey,
                this.config.fedshi.secretKey,
                this.config.fedshi.baseUrl
            );
            
        } catch (error) {
            console.error('Error loading configuration:', error);
            throw error;
        }
    }

    /**
     * Setup event listeners for file inputs
     */
    setupEventListeners() {
        // File input change handlers
        document.getElementById('fedshiFileInput').addEventListener('change', (e) => {
            this.handleFileSelection(e, 'fedshi');
        });
        
        document.getElementById('shipmentPackInput').addEventListener('change', (e) => {
            this.handleFileSelection(e, 'shipment');
        });
    }

    /**
     * Handle file selection
     */
    handleFileSelection(event, type) {
        const file = event.target.files[0];
        if (file) {
            console.log(`File selected for ${type} processing:`, file.name);
            this.showMessage(`File "${file.name}" selected for processing`, 'success');
        }
    }

    /**
     * Fedshi Authentication
     */
    async loginFedshi() {
        const username = document.getElementById('fedshiUsername').value;
        const password = document.getElementById('fedshiPassword').value;
        
        if (!username || !password) {
            this.showMessage('Please enter both Fedshi email and password', 'error');
            return;
        }

        this.updateStatus('fedshiAuthStatus', 'Authenticating...', 'info');

        try {
            const loginResult = await this.fedshiClient.authenticate(username, password);
            
            if (loginResult && loginResult.Token) {
                this.fedshiJwtToken = loginResult.Token;
                this.authenticationStatus.fedshi = true;
                this.updateStatus('fedshiAuthStatus', 'Authentication successful', 'success');
                this.showMessage('Fedshi authentication successful', 'success');
            } else {
                this.authenticationStatus.fedshi = false;
                this.updateStatus('fedshiAuthStatus', 'Authentication failed', 'error');
                this.showMessage('Fedshi authentication failed. Please check your credentials.', 'error');
            }
        } catch (error) {
            console.error('Fedshi authentication error:', error);
            this.authenticationStatus.fedshi = false;
            this.updateStatus('fedshiAuthStatus', 'Authentication error', 'error');
            this.showMessage(`Fedshi authentication error: ${error.message}`, 'error');
        }

        this.updateAuthenticationStatus();
    }

    /**
     * Update overall authentication status and enable/disable file operations
     */
    updateAuthenticationStatus() {
        const fedshiAuthenticated = this.authenticationStatus.fedshi;
        
        // Update overall status
        const overallStatus = document.getElementById('overallAuthStatus');
        if (fedshiAuthenticated) {
            overallStatus.textContent = 'Fedshi authenticated - File operations enabled';
            overallStatus.className = 'status overall success';
        } else {
            overallStatus.textContent = 'Please login to Fedshi to enable file operations';
            overallStatus.className = 'status overall error';
        }

        // Enable/disable file inputs and buttons
        const fileInputs = ['fedshiFileInput', 'shipmentPackInput'];
        
        fileInputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.disabled = !fedshiAuthenticated;
            }
        });

        // Enable buttons based on authentication
        document.querySelectorAll('.file-card button').forEach(button => {
            button.disabled = !fedshiAuthenticated;
        });
    }

    /**
     * Process files for Fedshi only
     */
    async processFedshiFiles() {
        const fileInput = document.getElementById('fedshiFileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showMessage('Please select a CSV file first', 'error');
            return;
        }

        this.showMessage('Processing Fedshi files...', 'info');
        
        try {
            const csvData = await this.readCSVFile(file);
            const orderIds = this.extractOrderIds(csvData);
            
            let processedCount = 0;
            let failedCount = 0;
            
            for (const orderId of orderIds) {
                try {
                    await this.processOrderFedshiOnly(orderId);
                    processedCount++;
                    this.addToSuccessLog(`Successfully processed Fedshi order: ${orderId}`);
                } catch (error) {
                    failedCount++;
                    this.addToFailedOrders(orderId);
                    console.error(`Failed to process Fedshi order ${orderId}:`, error);
                }
            }
            
            this.showMessage(`Fedshi processing complete. Success: ${processedCount}, Failed: ${failedCount}`, 'success');
            this.showTab('success');
            
        } catch (error) {
            console.error('Error processing Fedshi files:', error);
            this.showMessage(`Error processing Fedshi files: ${error.message}`, 'error');
        }
    }

    /**
     * Upload shipment pack
     */
    async uploadShipmentPack() {
        const fileInput = document.getElementById('shipmentPackInput');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showMessage('Please select a CSV file first', 'error');
            return;
        }

        this.updateShipmentPackStatus('Processing CSV file...', 'info');
        
        try {
            this.updateShipmentPackStatus('Parsing CSV file...', 'info');
            const csvData = await this.fedshiClient.parseCSVFile(file);

            this.displayCSVParsingResults(csvData);

            this.updateShipmentPackStatus('Creating shipment pack...', 'info');
            const result = await this.fedshiClient.processCSVAndCreateShipmentPack(file);
            
            if (result && result.ID) {
                const successMessage = `Shipment pack created successfully! ID: ${result.ID}, Courier: ${result.Courier}, Shipments: ${result.OrderShipments.length}`;
                this.updateShipmentPackStatus(successMessage, 'success');
                this.addToSuccessLog(`Shipment pack created: ${result.ID} (${result.OrderShipments.length} shipments)`);

                this.displayShipmentPackResults(result, csvData);
            } else {
                throw new Error('Creation failed - no ID returned');
            }
            
        } catch (error) {
            console.error('Error creating shipment pack:', error);
            const errorMessage = `Error creating shipment pack: ${error.message}`;
            this.updateShipmentPackStatus(errorMessage, 'error');
            this.displayShipmentPackError(error, file);
        }
    }

    updateShipmentPackStatus(message, type) {
        const statusElement = document.getElementById('shipmentPackStatus');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status ${type}`;
        }
    }

    displayCSVParsingResults(csvData) {
        const summaryElement = document.getElementById('shipmentPackSummaryProminent');
        if (summaryElement) {
            const timestamp = new Date().toLocaleString();
            const csvInfo = `
                <div class="csv-parse-result">
                    <p><strong>✅ CSV Parsed Successfully (${timestamp})</strong></p>
                    <p><strong>Shipment IDs Found:</strong> ${csvData.shipmentIDs.length}</p>
                    <p><strong>Courier ID:</strong> ${csvData.courierID}</p>
                </div>
            `;
            summaryElement.innerHTML = csvInfo;
        }

        const detailsElementTab = document.getElementById('shipmentPackDetails');
        if (detailsElementTab) {
            const timestamp = new Date().toLocaleString();
            const csvInfo = `
                <div class="csv-parse-result">
                    <h5>CSV Parsing Results (${timestamp})</h5>
                    <p><strong>Shipment IDs Found:</strong> ${csvData.shipmentIDs.length}</p>
                    <p><strong>Courier ID:</strong> ${csvData.courierID}</p>
                    <p><strong>Shipment IDs:</strong> ${csvData.shipmentIDs.join(', ')}</p>
                </div>
            `;
            detailsElementTab.innerHTML = csvInfo + detailsElementTab.innerHTML;
        }
    }

    displayShipmentPackResults(result, csvData) {
        const summaryElementProminent = document.getElementById('shipmentPackSummaryProminent');
        
        if (summaryElementProminent) {
            summaryElementProminent.innerHTML = `
                <div class="success-summary">
                    <p><strong>🎉 Shipment Pack Created Successfully!</strong></p>
                    <p><strong>📦 Pack ID:</strong> ${result.ID}</p>
                    <p><strong>🚚 Courier:</strong> ${result.Courier}</p>
                    <p><strong>📋 Total Shipments:</strong> ${result.OrderShipments.length}</p>
                    <p><strong>📄 From CSV:</strong> ${csvData.shipmentIDs.length} shipments, Courier ID: ${csvData.courierID}</p>
                </div>
            `;
        }

        const summaryElement = document.getElementById('shipmentPackSummary');
        const detailsElement = document.getElementById('shipmentPackDetails');
        
        if (summaryElement) {
            summaryElement.innerHTML = `
                <div class="success-summary">
                    <p><strong>Total Shipment Packs Created:</strong> 1</p>
                    <p><strong>Last Created:</strong> ${result.ID}</p>
                    <p><strong>Courier:</strong> ${result.Courier}</p>
                    <p><strong>Total Shipments:</strong> ${result.OrderShipments.length}</p>
                </div>
            `;
        }
        
        if (detailsElement) {
            const timestamp = new Date().toLocaleString();
            const resultInfo = `
                <div class="shipment-pack-result success">
                    <h5>Shipment Pack Created Successfully (${timestamp})</h5>
                    <p><strong>Pack ID:</strong> ${result.ID}</p>
                    <p><strong>Courier:</strong> ${result.Courier}</p>
                    <p><strong>Shipments:</strong> ${result.OrderShipments.length}</p>
                    <p><strong>Shipment IDs:</strong> ${result.OrderShipments.map(s => s.ID).join(', ')}</p>
                    <p><strong>CSV Data:</strong> ${csvData.shipmentIDs.length} shipments, Courier ID: ${csvData.courierID}</p>
                </div>
            `;
            detailsElement.innerHTML = resultInfo + detailsElement.innerHTML;
        }
    }

    displayShipmentPackError(error, file) {
        let errorMessage = error.message;

        if (error.errors && Array.isArray(error.errors) && error.errors.length > 0) {
            errorMessage = error.errors[0].message;
        }

        const summaryElementProminent = document.getElementById('shipmentPackSummaryProminent');
        if (summaryElementProminent) {
            const timestamp = new Date().toLocaleString();
            const errorInfo = `
                <div class="error-summary">
                    <p><strong>❌ Shipment Pack Creation Failed (${timestamp})</strong></p>
                    <p><strong>📁 File:</strong> ${file.name}</p>
                    <p><strong>⚠️ Error:</strong> ${errorMessage}</p>
                </div>
            `;
            summaryElementProminent.innerHTML = errorInfo;
        }

        const detailsElement = document.getElementById('shipmentPackDetails');
        if (detailsElement) {
            const timestamp = new Date().toLocaleString();
            const errorInfo = `
                <div class="shipment-pack-result error">
                    <h5>Shipment Pack Creation Failed (${timestamp})</h5>
                    <p><strong>File:</strong> ${file.name}</p>
                    <p><strong>Error:</strong> ${errorMessage}</p>
                </div>
            `;
            detailsElement.innerHTML = errorInfo + detailsElement.innerHTML;
        }
    }

    /**
     * Process order for Fedshi only
     */
    async processOrderFedshiOnly(orderId) {
        const fedshiResult = await this.fedshiClient.exportOrderShipmentReceipt(orderId);
        
        if (fedshiResult && fedshiResult.Content) {
            await this.downloadPDF(fedshiResult.Content, `${orderId}-Fedshi`);
        } else {
            throw new Error('No content received from Fedshi');
        }
    }

    /**
     * Read CSV file and parse content
     */
    readCSVFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const csvData = CSV.parse(e.target.result);
                    resolve(csvData);
                } catch (error) {
                    reject(new Error('Failed to parse CSV file'));
                }
            };
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    /**
     * Extract order IDs from CSV data
     */
    extractOrderIds(csvData) {
        if (!csvData || csvData.length === 0) {
            throw new Error('CSV file is empty');
        }
        
        // Assume first column contains order IDs
        const orderIds = [];
        for (let i = 1; i < csvData.length; i++) { // Skip header row
            if (csvData[i] && csvData[i][0]) {
                orderIds.push(csvData[i][0]);
            }
        }
        
        return orderIds;
    }

    /**
     * Download PDF from base64 content
     */
    downloadPDF(base64Content, filename) {
        return new Promise((resolve) => {
            const linkSource = `data:application/pdf;base64,${base64Content}`;
            const downloadLink = document.createElement("a");
            downloadLink.href = linkSource;
            downloadLink.download = `${filename}.pdf`;
            downloadLink.click();
            resolve(true);
        });
    }

    /**
     * Add order to failed orders list
     */
    addToFailedOrders(orderId) {
        this.processingResults.failed.push(orderId);
        const list = document.getElementById('failedOrdersList');
        const li = document.createElement('li');
        li.textContent = orderId;
        list.appendChild(li);
    }

    /**
     * Add message to success log
     */
    addToSuccessLog(message) {
        this.processingResults.success.push(message);
        const logContent = document.getElementById('successLogContent');
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logContent.appendChild(div);
    }

    /**
     * Show tab content
     */
    showTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab content
        const selectedContent = document.getElementById(tabName === 'failed' ? 'failedOrders' : 
                                                     tabName === 'success' ? 'successLog' : 'dataTable');
        if (selectedContent) {
            selectedContent.classList.add('active');
        }
        
        // Add active class to selected tab button
        const selectedButton = document.querySelector(`[onclick="app.showTab('${tabName}')"]`);
        if (selectedButton) {
            selectedButton.classList.add('active');
        }
    }

    /**
     * Update status element
     */
    updateStatus(elementId, message, type) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.className = `status ${type}`;
        }
    }

    /**
     * Show message to user
     */
    showMessage(message, type) {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Add to page
        document.body.appendChild(messageDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }
}

/**
 * Fedshi API Client
 */
class FedshiAPIClient {
    constructor(apiKey, secretKey, baseUrl) {
        this.apiKey = apiKey;
        this.secretKey = secretKey;
        this.baseUrl = baseUrl;
    }

    generateSignature(method, path, body, timestamp) {
        const stringToSign = `${method}\n${path}\n${body}\n${timestamp}\n${this.apiKey}`;
        return CryptoJS.HmacSHA256(stringToSign, this.secretKey).toString(CryptoJS.enc.Hex);
    }

    async authenticate(username, password) {
        const timestamp = new Date().toISOString();
        const method = 'POST';
        const path = '/api/v1/third-party/admin/login';
        const body = JSON.stringify({
            email: username,
            password: password
        });

        const signature = this.generateSignature(method, path, body, timestamp);

        const response = await fetch(`${this.baseUrl}${path}`, {
            method: 'POST',
            headers: {
                'X-API-Key': this.apiKey,
                'X-API-Signature': signature,
                'X-API-Timestamp': timestamp,
                'Content-Type': 'application/json'
            },
            body: body
        });

        if (!response.ok) {
            throw new Error(`Authentication failed: ${response.status}`);
        }

        return response.json();
    }

    async makeGraphQLRequest(query, variables = {}) {
        const timestamp = new Date().toISOString();
        const method = 'POST';
        const path = '/graphql/third-party';
        const body = JSON.stringify({ query, variables });

        const signature = this.generateSignature(method, path, body, timestamp);

        const headers = {
            'X-API-Key': this.apiKey,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp,
            'Content-Type': 'application/json'
        };

        // Add JWT token if available
        if (window.app && window.app.fedshiJwtToken) {
            headers['Authorization'] = `Bearer ${window.app.fedshiJwtToken}`;
        }

        const response = await fetch(`${this.baseUrl}${path}`, {
            method: 'POST',
            headers: headers,
            body: body
        });

        if (!response.ok) {
            throw new Error(`GraphQL request failed: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.errors) {
            throw new Error(`GraphQL Error: ${JSON.stringify(result.errors)}`);
        }

        return result.data;
    }

    async exportOrderShipmentReceipt(orderShipmentID) {
        const query = `
            query ExportOrderShipmentReceipt($ID : FID!){
                ExportOrderShipmentReceipt(OrderShipmentID: $ID){
                    Content
                    Extension
                }
            }
        `;

        const result = await this.makeGraphQLRequest(query, { ID: orderShipmentID });
        return result.ExportOrderShipmentReceipt;
    }

    async processCSVAndCreateShipmentPack(file) {
        const csvData = await this.parseCSVFile(file);
        console.log('DEBUG: processCSVAndCreateShipmentPack - Parsed CSV data:', csvData);

        if (csvData.shipmentIDs.length === 0) {
            throw new Error('No shipment IDs found in CSV file');
        }

        const query = `
            mutation AddShipmentPackV2($request: AddShipmentPackRequestV2!) {
                AddShipmentPackV2(Request: $request) {
                    ID
                    Courier
                    OrderShipments {
                        ID
                    }
                }
            }
        `;

        const variables = {
            request: {
                OrderShipmentIDs: csvData.shipmentIDs,
                DeliveryCourierID: csvData.courierID,
                Type: "shipping"
            }
        };

        const timestamp = new Date().toISOString();
        const method = 'POST';
        const path = '/graphql/third-party';

        const body = JSON.stringify({
            query: query,
            variables: variables
        });

        console.log('DEBUG: processCSVAndCreateShipmentPack - Body:', body);

        const signature = this.generateSignature(method, path, body, timestamp);
        console.log('DEBUG: processCSVAndCreateShipmentPack - Generated signature:', signature);

        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey,
            'X-API-Signature': signature,
            'X-API-Timestamp': timestamp
        };

        if (window.app && window.app.fedshiJwtToken) {
            headers['Authorization'] = `Bearer ${window.app.fedshiJwtToken}`;
            console.log('DEBUG: processCSVAndCreateShipmentPack - Added JWT token');
        }

        try {
            console.log('DEBUG: processCSVAndCreateShipmentPack - Sending request...');
            const response = await fetch(`${this.baseUrl}/graphql/third-party`, {
                method: 'POST',
                headers: headers,
                body: body
            });

            console.log('DEBUG: processCSVAndCreateShipmentPack - Response status:', response.status);
            const result = await response.json();
            console.log('DEBUG: processCSVAndCreateShipmentPack - Response:', result);

            if (result.errors) {
                // Extract the first error message for a cleaner error display
                const firstError = result.errors[0];
                throw new Error(firstError.message || 'Unknown GraphQL error');
            }

            return result.data.AddShipmentPackV2;
        } catch (error) {
            console.error('DEBUG: processCSVAndCreateShipmentPack - Error:', error);
            throw error;
        }
    }

    async parseCSVFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const csvContent = event.target.result;
                    console.log('DEBUG: parseCSVFile - CSV content:', csvContent);

                    // Parse CSV content
                    const lines = csvContent.split('\n');
                    const shipmentIDs = [];
                    let courierID = null;

                    // Skip header row and process data rows
                    for (let i = 1; i < lines.length; i++) {
                        const line = lines[i].trim();
                        if (line === '') continue;

                        const columns = line.split(',');
                        if (columns.length >= 2) {
                            const shipmentID = columns[0].trim();
                            const courier = columns[1].trim();

                            if (shipmentID && courier) {
                                shipmentIDs.push(shipmentID);
                                courierID = parseInt(courier, 10);
                            }
                        }
                    }

                    console.log('DEBUG: parseCSVFile - Extracted shipment IDs:', shipmentIDs);
                    console.log('DEBUG: parseCSVFile - Extracted courier ID:', courierID);

                    resolve({
                        shipmentIDs: shipmentIDs,
                        courierID: courierID
                    });
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FedshiIntegrationApp();
}); 