import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,URL

load_dotenv()

def get_engine(database):
    url = URL.create(
        drivername= 'postgresql+psycopg2',
        username= os.getenv('DB_USER'),
        password= os.getenv('DB_PASSWORD'),
        host= os.getenv('DB_HOST'),
        port= os.getenv('DB_PORT'),
        database= database
    )

    return create_engine(url)

warehouse_engine = get_engine('aoem_warehouse')
crm_engine = get_engine('crm_db')
erp_engine = get_engine('erp_db')

