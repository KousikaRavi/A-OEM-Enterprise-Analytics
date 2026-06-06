DROP TABLE IF EXISTS crm_vehicle ;
DROP TABLE IF EXISTS crm_customer ;

CREATE TABLE crm_customer (
    customer_id       VARCHAR(10)  PRIMARY KEY,
    customer_name     VARCHAR(100) NOT NULL,
    customer_type     VARCHAR(5)   NOT NULL CHECK (customer_type IN ('B2B','B2C')),
    customer_stage    VARCHAR(15)  NOT NULL CHECK (customer_stage IN ('Prospect','Lead','Customer')),
    industry          VARCHAR(50),
    street            VARCHAR(100),
    district          VARCHAR(50)  NOT NULL,
    state             VARCHAR(50)  NOT NULL,
    pincode           VARCHAR(10),
    email             VARCHAR(100),
    phone             VARCHAR(15),
    created_date      DATE        NOT NULL,
    status            VARCHAR(10)  DEFAULT 'Active' CHECK (status IN ('Active','Inactive'))
);


CREATE TABLE crm_vehicle (
    vehicle_id               VARCHAR(25) PRIMARY KEY,
    model_number             VARCHAR(25) NOT NULL,
    serial_number            VARCHAR(50) NOT NULL UNIQUE,
    engine_serial_number     VARCHAR(64) NOT NULL UNIQUE,
    capacity_kg              INT,
    fuel_type                VARCHAR(15) CHECK (fuel_type IN ('Electric','LPG','Diesel','Petrol')),
    manufacture_date         DATE,
    factory_shipped_date     DATE,
    retail_shipment_date     DATE,
    date_of_first_use        DATE,
    warranty_type            VARCHAR(20),
    warranty_start_date      DATE,
    warranty_expiry_date     DATE,
    last_hour_meter_reading  INT         DEFAULT 0,
    customer_id              VARCHAR(10) REFERENCES crm_customer(customer_id),
    dealer_id                VARCHAR(20),
    status                   VARCHAR(10) DEFAULT 'Active'
);	

SELECT count(*) FROM crm_customer
UNION ALL
SELECT count(*) FROM crm_vehicle;



ALTER TABLE crm_customer
ALTER COLUMN created_date TYPE VARCHAR(20);

TRUNCATE TABLE crm_vehicle;
TRUNCATE TABLE crm_customer CASCADE;