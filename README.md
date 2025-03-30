# Baruch's Treks

Second version of Baruch's Treks which is based on Azure Storage and Django.

## Features

- Trip management with detailed information
- Interactive maps using Mapy.cz API
- Photo uploads for trips
- Start and finish point markers on maps
- Azure Table Storage for trip data
- Azure Blob Storage for trip photos

## Deployment to Azure Web App

This project is configured for continuous deployment to Azure Web App using GitHub Actions.

### Prerequisites

1. An Azure account with an active subscription
2. An Azure Web App named "baruchstreks"
3. Azure Storage Account named "baruchstreks" with:
   - A table named "Trips"
   - A blob container for storing photos

### Setting up Continuous Deployment

1. **Create the Azure Web App**:
   - Go to the Azure Portal and create a new Web App named "baruchstreks"
   - Select Python 3.11 as the runtime stack
   - Configure the app to use Linux

2. **Create Azure Credentials**:
   - Open Azure Cloud Shell (bash) from the Azure Portal
   - Run the following command to create a service principal with Contributor role:
     ```bash
     az ad sp create-for-rbac --name "baruchstreks-github" --role contributor \
       --scopes /subscriptions/b355f86c-94b4-467b-b643-1206cbf0e24c/resourceGroups/BaruchsTreks/providers/Microsoft.Web/sites/baruchstreks
     ```
   - Replace `{subscription-id}` with your Azure subscription ID and `{resource-group}` with your resource group name
   - The command will output JSON similar to this:
     ```json
     {
       "appId": "example-app-id",
       "displayName": "baruchstreks-github",
       "password": "example-password",
       "tenant": "example-tenant-id"
     }
     ```
   - You need to transform this output into the format required by the GitHub Actions Azure login:
     ```json
     {
       "clientId": "THE-APP-ID-FROM-ABOVE",
       "clientSecret": "THE-PASSWORD-FROM-ABOVE",
       "tenantId": "THE-TENANT-FROM-ABOVE",
       "subscriptionId": "YOUR-AZURE-SUBSCRIPTION-ID"
     }
     ```

3. **Configure GitHub Secrets**:
   - In your GitHub repository, go to Settings > Secrets and Variables > Actions
   - Add the following secrets:
     - `AZURE_CREDENTIALS`: The properly formatted JSON from step 2
     - `BARUCHSTREKS_STORAGE_CONNECTION`: Your Azure Storage connection string
     - `MAPY_CZ_API_KEY`: Your Mapy.cz API key
     - `SECRET_KEY`: A secure Django secret key

4. **Configure App Settings in Azure**:
   - In the Azure Portal, go to your Web App > Configuration > Application settings
   - Add the following settings:
     - `BARUCHSTREKS_STORAGE_CONNECTION`: Your Azure Storage connection string
     - `MAPY_CZ_API_KEY`: Your Mapy.cz API key
     - `DEBUG`: Set to "False"
     - `SECRET_KEY`: A secure Django secret key
     - `ALLOWED_HOSTS`: "baruchstreks.azurewebsites.net"

5. **Push to Main Branch**:
   - When you push to the main branch, the GitHub Actions workflow will automatically:
     - Build the application
     - Collect static files
     - Deploy to Azure Web App

### Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with the required environment variables (see `.env.example`)
6. Run the development server: `python manage.py runserver`

## Security

- All sensitive information is stored in environment variables
- The `.gitignore` file is configured to prevent committing sensitive files
- Production deployment uses HTTPS with security headers
