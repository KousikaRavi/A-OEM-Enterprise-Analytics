import os
import sys
import logging
import pandas as pd
import math
from fastapi import FastAPI,Header,Query,HTTPException
from fastapi.responses import JSONResponse

# Path Setup 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from config import crm_engine


# Logging
logging.basicConfig(
    level= logging.INFO,
    format= '%(asctime)s | %(levelname)s | %(message)s'
)

log = logging.getLogger(__name__)


# App Setup
app = FastAPI(
    title= 'AOEM CRM API',
    description= 'Mock CRM API',
    version= '1.0.0'
)

# API KEY
API_KEY = os.getenv('API_KEY')

# Auth Function
def verify_api_key(x_api_key: str= Header(...)):
    if x_api_key != API_KEY:
        logging.warning(f"Unauthorised access with key {x_api_key}")
        raise HTTPException(status_code=401,detail="Unauthorised")

# Health Check Endpoint
@app.get('/health',tags=['System'])
def health():
    return {'status': 'ok',
            'service' : 'AOEM CRM API',
            'version' : '1.0.0'}

# Get Customers Endpoint
@app.get('/api/customers',tags=['Customers'])
def get_customers(
    page : int = Query(default=1 ,ge=1,description='Page Number'),
    limit : int =Query(default=100 ,ge=1,le=500 ,description='Records per Page'),
    x_api_key : str = Header (...)
):
    verify_api_key(x_api_key)
    try:
        # Pagination Logic
        offset = (page-1)*limit

        # Read DB into df
        df = pd.read_sql(f"""
            SELECT * FROM crm_customer
            ORDER BY customer_id
            LIMIT {limit}
            OFFSET {offset}             
            """,crm_engine)
        
        total = pd.read_sql(
            "SELECT count(*) as count FROM crm_customer",
            crm_engine)['count'][0]
        
        # Total Pages Calculation
        total_pages = total//limit

        log.info(f"Customers fetched - page {page}/{total_pages}, records: {len(df)}")

        return {
            'page'          : page,
            'limit'         : limit,
            'total'         : total,
            'total_pages'   : total_pages,
            'data'          : df.to_dict(orient='records')
        }
    except Exception as e :
        log.error(f"Error fetching Customers: {e}")
        raise HTTPException(status_code=500 , detail="Internal Server error")
    
# Get Customer Ids details
@app.get('api/customers/{customer_id}',tags=['Customers'])
def get_customer(customer_id : str ,x_api_key : str = Header (...)):
    verify_api_key(x_api_key)
    try:
        df = pd.read_sql(
            "SELECT * FROM crm_customer WHERE customer_id = %(id)s",
            crm_engine,
            params= {'id':customer_id}
            )
        if df.empty:
            raise HTTPException (status_code=404 ,detail=f'Customer {customer_id} not found')
        
        log.info(f'{customer_id} fetched')

        return df.to_dict(orient='records')[0]

    except HTTPException:
        raise
    except Exception as e :
        log.error(f'Error fetching customer {customer_id} : {e}')
        raise HTTPException (status_code=500,detail="Internal Server Error")
    

# Get Vehicles
@app.get('api/vehicle',tags=["Vehicles"])
def get_vehicles(
    page : int = Query(default= 1,ge=1),
    limit : int = Query(default=100,ge=1,le=500),
    x_api_key : str = Header (...)
):
    try:  
        verify_api_key(x_api_key)

        offset = (page -1)* limit

        df = pd.read_sql(
            "SELECT * FROM crm_vehicle ORDER BY vehicle_id LIMIT = {limit} OFFSET = {offset}",
            crm_engine )
        
        total = pd.read_sql("SELECT count(*) FROM crm_vehcile",crm_engine)['count'][0]

        total_pages = math.ceil(total // limit )

        log.info("Vehicles fetched - {page}/{total_pages}")

        return {
            'page' : page,
            'limit' : limit,
            'total' : total,
            'total_pages' : total_pages,
            'data' : df.to_dict(orient='records')
        }
    
    except:
        log.error()



