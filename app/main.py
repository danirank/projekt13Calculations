from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI()

app.include_router(router)



#all_single_rows = getSingleRows(row)


