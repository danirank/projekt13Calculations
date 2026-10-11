
module appService '../../infrastructure/modules/appservice.bicep' = {
  name: 'projekt13-calculations-AppService'
  params: {
    appName: 'projekt13-calculations'
    linuxFxVersion: 'PYTHON|3.12'
    appCommandLine: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app'
    sku: 'F1'
    tier: 'Free'
  }
  
}
