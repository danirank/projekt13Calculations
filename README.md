# CalculationsApi Azure Function

The API uses the Python v2 Azure Functions programming model. Its HTTP routes
preserve the existing gateway contract:

- `GET /api/`
- `POST /api/reduce`
- `POST /api/data`

## Run locally

Install Python dependencies, Azure Functions Core Tools v4, and Azurite. Copy
`local.settings.json.example` to `local.settings.json`, start Azurite, then run:

```powershell
python -m pip install -r requirements.txt
func start
```

## Deploy

Deploy `infrastructure/deploy.bicep` to the target resource group. It provisions
a Flex Consumption plan, storage and Application Insights. Then publish this
directory with Azure Functions Core Tools:

```powershell
az deployment group create --resource-group <resource-group> --template-file infrastructure/deploy.bicep
func azure functionapp publish <functionAppName>
```

Point the API Gateway's `ServiceUrls:Calculations` setting at the resulting
Function App URL. Routes retain the `/api` prefix supplied by the Functions
host, so the gateway's existing `/api/`, `/api/reduce`, and `/api/data` calls
continue to work.
