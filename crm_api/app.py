import os
import sys
import logging
import pandas as pd
import math
import json
import numpy as np
from fastapi import FastAPI, Header, Query, HTTPException
from fastapi.responses import JSONResponse

# Path Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from config import crm_engine

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
log = logging.getLogger(__name__)

# App Setup
app = FastAPI(
    title='AOEM CRM API',
    description='Mock CRM API',
    version='1.0.0'
)

# API KEY
API_KEY = os.getenv('API_KEY')


# ── Auth ─────────────────────────────────────────────────────
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        log.warning(f"Unauthorised access attempt with key: {x_api_key}")
        raise HTTPException(status_code=401, detail="Unauthorised")


# ── JSON-safe serializer ─────────────────────────────────────
def safe_val(v):
    """Convert any pandas/numpy value to a JSON-serializable Python type."""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return None if math.isnan(v) else float(v)
    if isinstance(v, pd.Timestamp):
        return v.isoformat() if not pd.isnull(v) else None
    if isinstance(v, np.bool_):
        return bool(v)
    # handles datetime.date and datetime.datetime
    import datetime
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v

def df_to_records(df: pd.DataFrame) -> list:
    """Convert DataFrame to JSON-safe list of dicts."""
    return [
        {k: safe_val(v) for k, v in row.items()}
        for row in df.to_dict(orient='records')
    ]


# ── Health Check ─────────────────────────────────────────────
@app.get('/health', tags=['System'])
def health():
    return {
        'status' : 'ok',
        'service': 'AOEM CRM API',
        'version': '1.0.0'
    }


# ── GET /api/customers ───────────────────────────────────────
@app.get('/api/customers', tags=['Customers'])
def get_customers(
    page      : int = Query(default=1,   ge=1,         description='Page number'),
    limit     : int = Query(default=100, ge=1, le=500, description='Records per page'),
    x_api_key : str = Header(...)
):
    verify_api_key(x_api_key)
    try:
        offset = (page - 1) * limit

        df = pd.read_sql(f"""
            SELECT * FROM crm_customer
            ORDER BY customer_id
            LIMIT {limit} OFFSET {offset}
            """, crm_engine)

        total = int(pd.read_sql(
            "SELECT COUNT(*) AS count FROM crm_customer",
            crm_engine)['count'][0])

        total_pages = math.ceil(total / limit)

        log.info(f"Customers fetched — page {page}/{total_pages}, records: {len(df)}")

        return JSONResponse(content={
            'page'       : page,
            'limit'      : limit,
            'total'      : total,
            'total_pages': total_pages,
            'data'       : df_to_records(df)
        })

    except Exception as e:
        log.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ── GET /api/customers/{customer_id} ────────────────────────
@app.get('/api/customers/{customer_id}', tags=['Customers'])
def get_customer(
    customer_id: str,
    x_api_key  : str = Header(...)
):
    verify_api_key(x_api_key)
    try:
        df = pd.read_sql(
            "SELECT * FROM crm_customer WHERE customer_id = %(id)s",
            crm_engine,
            params={'id': customer_id}
        )

        if df.empty:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

        log.info(f"Customer {customer_id} fetched")
        return JSONResponse(content=df_to_records(df)[0])

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching customer {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ── GET /api/vehicles ────────────────────────────────────────
@app.get('/api/vehicles', tags=['Vehicles'])
def get_vehicles(
    page      : int = Query(default=1,   ge=1,         description='Page number'),
    limit     : int = Query(default=100, ge=1, le=500, description='Records per page'),
    x_api_key : str = Header(...)
):
    verify_api_key(x_api_key)
    try:
        offset = (page - 1) * limit

        df = pd.read_sql(f"""
            SELECT * FROM crm_vehicle
            ORDER BY vehicle_id
            LIMIT {limit} OFFSET {offset}
            """, crm_engine)

        total = int(pd.read_sql(
            "SELECT COUNT(*) AS count FROM crm_vehicle",
            crm_engine)['count'][0])

        total_pages = math.ceil(total / limit)

        log.info(f"Vehicles fetched — page {page}/{total_pages}, records: {len(df)}")

        return JSONResponse(content={
            'page'       : page,
            'limit'      : limit,
            'total'      : total,
            'total_pages': total_pages,
            'data'       : df_to_records(df)
        })

    except Exception as e:
        log.error(f"Error fetching vehicles: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ── GET /api/vehicles/{vehicle_id} ──────────────────────────
@app.get('/api/vehicles/{vehicle_id}', tags=['Vehicles'])
def get_vehicle(
    vehicle_id: str,
    x_api_key : str = Header(...)
):
    verify_api_key(x_api_key)
    try:
        df = pd.read_sql(
            "SELECT * FROM crm_vehicle WHERE vehicle_id = %(id)s",
            crm_engine,
            params={'id': vehicle_id}
        )

        if df.empty:
            raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

        log.info(f"Vehicle {vehicle_id} fetched")
        return JSONResponse(content=df_to_records(df)[0])

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching vehicle {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")