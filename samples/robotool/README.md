# Fedshi Integration Tool

A comprehensive web-based tool for Fedshi services to streamline shipment processing operations.

## Overview

This tool provides a unified interface for:
- **Fedshi Integration**: Export order shipment receipts and upload shipment packs using API key authentication
- **Batch Processing**: Process multiple orders from CSV files
- **File Management**: Download and manage shipment documents

## Features

- 🔐 **Secure Authentication**: Secure login for Fedshi services using API key and email/password
- 📊 **CSV Processing**: Batch process orders from CSV files
- 📄 **Document Export**: Export shipment receipts as PDF files
- 📦 **Shipment Pack Upload**: Upload CSV files to create shipment packs
- 📱 **Modern UI**: Clean, responsive interface with real-time status updates

## Setup

### Prerequisites
- Modern web browser with JavaScript enabled
- Valid Fedshi API credentials
- Valid Fedshi account credentials (email and password)

### Configuration
1. Edit `config.json` to update your API credentials:
   - Replace `YOUR_FEDSHI_API_KEY_HERE` with your actual Fedshi API key
   - Replace `YOUR_FEDSHI_SECRET_KEY_HERE` with your actual Fedshi secret key
2. Ensure all required files are in the same directory
3. Start the local development server: `python server.py`
4. Open your browser and navigate to `http://localhost:8080`

### File Structure
```
FedshiIntegrationTool/
├── index.html              # Main application interface
├── app.js                  # Core application logic
├── config.json             # Configuration file (API keys, URLs)
├── styles.css              # Application styles
├── lib/
│   └── csv.min.js          # CSV parsing library
├── data/
│   └── sample-orders.csv   # Sample CSV file for testing
├── server.py               # Local development server
└── README.md               # This file
```

## Usage

### 1. Authentication
- **Fedshi Login**: Enter your Fedshi email and password
- Fedshi service must be authenticated before file operations are enabled

### 2. File Operations
- **Fedshi Files**: Download shipment receipts for orders from Fedshi
- **Shipment Pack Upload**: Upload CSV files to create new shipment packs

### 3. Processing
- Select a CSV file containing order IDs
- The tool will automatically:
  - Export shipment receipts from Fedshi
  - Download all documents locally
  - Track failed orders in the list

## API Integration

### Fedshi API
- **Authentication**: API Key + HMAC-SHA256 signature + JWT token
- **Endpoints**: 
  - GraphQL for shipment receipts and pack uploads
  - REST for admin login
- **Features**: Export PDFs, upload shipment packs

## Security

- API keys and secrets are stored in `config.json` (keep this file secure)
- **Important**: Replace placeholder values in `config.json` with your actual credentials
- All API communications use HTTPS
- JWT tokens are managed securely in memory
- No credentials are stored in browser storage
- Never commit real API keys to version control

## Troubleshooting

### Common Issues
1. **Authentication Failed**: Check credentials in config.json and ensure placeholder values are replaced
2. **CORS Errors**: Use the provided `server.py` script to run locally
3. **File Upload Fails**: Verify Fedshi service is authenticated
4. **Network Errors**: Check internet connection and API endpoints
5. **Port Already in Use**: Try a different port or stop other services
6. **Configuration Errors**: Ensure `config.json` contains valid API keys, not placeholder values

### Debug Mode
Open browser developer tools (F12) to view detailed logs and error messages.

## Development

### Adding New Features
1. Update `config.json` with new API endpoints
2. Add new methods to the `FedshiClient` class
3. Update the UI in `index.html`
4. Add corresponding styles in `styles.css`

### Testing
- Use the sample CSV file for testing
- Verify all authentication flows work correctly
- Test file upload and download functionality

## License

This tool is provided as-is for internal use. Please ensure compliance with Fedshi API terms of service.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for error messages
3. Verify API credentials and endpoints
4. Contact the development team for assistance
