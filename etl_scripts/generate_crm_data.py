import os
import sys
import random
import string
import logging
import pandas as pd
from faker import Faker
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# ── Path setup ───────────────────────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import warehouse_engine, erp_engine, crm_engine

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
log = logging.getLogger(__name__)

# ── Faker setup ──────────────────────────────────────────────
fake = Faker('en_US')
Faker.seed(42)
random.seed(42)

# ── Pull reference data ──────────────────────────────────────
log.info("Pulling reference data from warehouse and erp...")

states_df   = pd.read_sql("SELECT state_id, state_name FROM dim_state", warehouse_engine)
district_df = pd.read_sql("""
    SELECT d.district_name, d.pincode, s.state_name
    FROM dim_district d
    JOIN dim_state s ON d.state_id = s.state_id
""", warehouse_engine)
dealer_df   = pd.read_sql("SELECT dealer_id FROM erp_dealer", erp_engine)

states            = states_df['state_name'].tolist()
dealer_ids        = dealer_df['dealer_id'].tolist()
state_districts   = district_df.groupby('state_name')['district_name'].apply(list).to_dict()
district_pincodes = district_df.set_index('district_name')['pincode'].to_dict()

log.info(f"States loaded: {len(states)}")
log.info(f"Dealers loaded: {len(dealer_ids)}")

# ── Helper functions ─────────────────────────────────────────
def gen_id(prefix, number):
    return f"{prefix}{str(number).zfill(4)}"

def dirty_state(state):
    """Introduce real-world state name dirt 20% of time"""
    if random.random() < 0.20:
        return random.choice([
            state.lower(),
            state.upper(),
            state + " ",
            state.replace(" ", "")
        ])
    return state

def dirty_phone():
    """Introduce multiple real-world phone formats"""
    digits = ''.join(random.choices(string.digits, k=10))
    if random.random() < 0.15:
        return random.choice([None, "XXXXXXXXXX", digits[:6]])
    return random.choice([
        f"+91 {digits[:5]} {digits[5:]}",
        f"+91-{digits}",
        f"0{digits}",
        f"{digits[:5]}-{digits[5:]}",
        digits,
        f"({digits[:4]}) {digits[4:]}",
    ])

def dirty_date(clean_date):
    """Introduce mixed date formats 25% of time"""
    if random.random() < 0.25:
        return random.choice([
            clean_date.strftime('%d/%m/%Y'),
            clean_date.strftime('%m-%d-%Y'),
            clean_date.strftime('%d-%m-%Y'),
            clean_date.strftime('%B %d, %Y'),
        ])
    return str(clean_date)

def dirty_dealer_id():
    """Return invalid dealer_id 5% of time"""
    if random.random() < 0.05:
        return f"INVALID{random.randint(100,999)}"
    return random.choice(dealer_ids)

# ── Constants ────────────────────────────────────────────────
INDUSTRIES     = ['Manufacturing','Logistics','Construction',
                  'Agriculture','Mining','Retail','Warehousing']
STAGES         = ['Prospect','Lead','Customer']
STAGE_WEIGHTS  = [0.15, 0.20, 0.65]
MODELS         = ['8FG25','7FG30','8FG35','7RG20','6RG25','THD40','THD50','7HBW3']
FUELS          = ['Electric','LPG','Diesel','Petrol']
WARRANTY_TYPES = ['Standard','Extended','Comprehensive']
CAPACITIES     = [1000,1500,2000,2500,3000,4000]

# ── Generate Customers ───────────────────────────────────────
log.info("Generating customers...")
customers = []

for i in range(1, 951):
    state      = random.choice(states)
    districts  = state_districts.get(state, ['Unknown'])
    district   = random.choice(districts)
    pincode    = district_pincodes.get(district, '000000')
    ctype      = random.choices(['B2B','B2C'], weights=[0.70,0.30])[0]
    stage      = random.choices(STAGES, weights=STAGE_WEIGHTS)[0]
    clean_date = fake.date_between(
                    start_date=date(2018,1,1),
                    end_date=date(2024,12,31)
                 )

    customers.append({
        'customer_id'   : gen_id('CUST', i),
        'customer_name' : fake.company() if ctype == 'B2B' else fake.name(),
        'customer_type' : ctype,
        'customer_stage': stage,
        'industry'      : random.choice(INDUSTRIES) if ctype == 'B2B' else None,
        'street'        : fake.street_address(),
        'district'      : district,
        'state'         : dirty_state(state),
        'pincode'       : pincode,
        'email'         : fake.company_email() if ctype == 'B2B' else fake.email(),
        'phone'         : dirty_phone(),
        'created_date'  : dirty_date(clean_date),
        'status'        : random.choices(
                            ['Active','Inactive'],
                            weights=[0.90,0.10]
                          )[0]
    })

# ── Plant 2% duplicates ──────────────────────────────────────
n_dupes = int(len(customers) * 0.02)
log.info(f"Planting {n_dupes} duplicate customers...")
dupes = []
for i in range(n_dupes):
    original = random.choice(customers).copy()
    original['customer_id'] = gen_id('CUST', 2000 + i)
    original['email']       = None
    original['phone']       = dirty_phone()
    dupes.append(original)

all_customers = customers + dupes
df_customers  = pd.DataFrame(all_customers)
log.info(f"Total customers with dupes: {len(df_customers)}")
df_customers.to_sql('crm_customer', crm_engine, if_exists='append', index=False)
log.info(f"✅ {len(df_customers)} customers inserted into crm_db")

# ── Generate Vehicles ────────────────────────────────────────
log.info("Generating 800 vehicles...")
customer_ids = [c['customer_id'] for c in customers]
today        = date.today()
vehicles     = []

for i in range(1, 801):
    manufacture     = fake.date_between(
                        start_date=date(2019,1,1),
                        end_date=date(2023,12,31)
                      )
    factory_ship    = manufacture  + timedelta(days=random.randint(30,90))
    retail_ship     = factory_ship + timedelta(days=random.randint(15,60))
    dofu            = retail_ship  + timedelta(days=random.randint(1,30))
    warranty_start  = dofu
    warranty_months = random.choice([12,24,36])
    warranty_expiry = warranty_start + relativedelta(months=warranty_months)

    # ── Plant future date_of_first_use 2% of time ───────────
    if random.random() < 0.02:
        dofu = today + timedelta(days=random.randint(30,180))
        log.debug(f"Planted future DOFU for VIN{str(i).zfill(4)}: {dofu}")

    # ── Plant orphan customer_id 3% of time ─────────────────
    if random.random() < 0.03:
        cust_id = f"GHOST{random.randint(1000,9999)}"
    else:
        cust_id = random.choice(customer_ids)

    vehicles.append({
        'vehicle_id'              : gen_id('VIN', i),
        'model_number'            : random.choice(MODELS),
        'serial_number'           : ''.join(random.choices(
                                      string.ascii_uppercase + string.digits, k=12)),
        'engine_serial_number'    : ''.join(random.choices(
                                      string.ascii_uppercase + string.digits, k=16)),
        'capacity_kg'             : random.choice(CAPACITIES),
        'fuel_type'               : random.choice(FUELS),
        'manufacture_date'        : manufacture,
        'factory_shipped_date'    : factory_ship,
        'retail_shipment_date'    : retail_ship,
        'date_of_first_use'       : dofu,
        'warranty_type'           : random.choice(WARRANTY_TYPES),
        'warranty_start_date'     : warranty_start,
        'warranty_expiry_date'    : warranty_expiry,
        'last_hour_meter_reading' : random.randint(0,5000),
        'customer_id'             : cust_id,
        'dealer_id'               : dirty_dealer_id(),
        'status'                  : 'Active'
    })

df_vehicles = pd.DataFrame(vehicles)
df_vehicles.to_sql('crm_vehicle', crm_engine, if_exists='append', index=False)
log.info(f"✅ {len(df_vehicles)} vehicles inserted into crm_db")

log.info("crm_db populated successfully.")
log.info("─" * 50)
log.info("DATA QUALITY SUMMARY:")
log.info(f"  Customers total       : {len(df_customers)}")
log.info(f"  Duplicate customers   : {n_dupes}")
log.info(f"  Dirty state names     : ~{int(len(customers)*0.20)}")
log.info(f"  Mixed date formats    : ~{int(len(customers)*0.25)}")
log.info(f"  Missing phones        : ~{int(len(customers)*0.15)}")
log.info(f"  Vehicles total        : {len(df_vehicles)}")
log.info(f"  Invalid dealer_ids    : ~{int(800*0.05)}")
log.info(f"  Orphan customer_ids   : ~{int(800*0.03)}")
log.info(f"  Future DOFUs          : ~{int(800*0.02)}")
log.info("─" * 50)