import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL

# 1. Configuration
def get_connection():
    url = URL.create (
          drivername="postgresql+psycopg2",
          username ='postgres',
          password = "Arun1@Kas2",
          host ='localhost',
          port =5432,
          database ='aoem_warehouse'
    )
      
    return create_engine(url)
     
# 2. Extraction 
def extract_data(file_path):
    schema ={
         'district_code':str,
         'state_code': str,
         'pincode':str,
         'tier':str,
         'population':float,
         'area_sqkm':float,
         'density_per_sq_km':float
    }
    
    print(f"Reading {file_path}")
    return pd.read_csv(file_path ,dtype=schema)


# 3. Transform 
def transform_regions(df):
    zones=sorted(df['zone'].unique())
    print(f'Transforming Regions ')
    return pd.DataFrame({
        'region_id' : [f"R_{i+1:02}" for i in range(len(zones))],
        'region_name' : zones
    })

def transform_states(df,dim_region):
        states_unique=df[['zone','state','state_code']].drop_duplicates()
        states_map = states_unique.merge(dim_region,left_on='zone',right_on='region_name')
        states=states_map.sort_values('region_id').reset_index(drop=True)
        print("Generating dim_state")
        dim_state= states[['state_code','region_id','state']].rename(columns={
             'state':'state_name',
             'state_code':'state_id'
             })
        print(f'Transforming States ')
        return dim_state

def transform_district(df,dim_state):
    district_map = df.merge(dim_state,left_on='state',right_on='state_name')
    district_map=district_map.sort_values(['region_id','state_id']).reset_index(drop=True)
    district_map['district_id'] = [f"D_{i+1:02}" for i in range(len(district_map))]
    dim_district = district_map[['state_id','district_id','district_code','district',
                             'population','density_per_sq_km','headquarters',
                             'pincode','tier','area_sq_km']].rename(columns={
                                 'district':'district_name',
                                 'headquarters':'head_quarter' ,                            
                                 })
    print(f'Transforming Districts ')
    return dim_district


def load_to_postgres(table_name,dataframe):
    dataframe.to_sql(table_name,get_connection(),if_exists='append',index=False)
    print(f'{table_name} loaded successfully')

def run_pipeline():
    #  1.Extract
    raw_df = extract_data('data/dim_geo.csv')

    # 2. Transform
    df_region = transform_regions(raw_df)
    df_state = transform_states (raw_df,df_region)
    df_disrict = transform_district (raw_df,df_state)

    # 3 . Load
    load_to_postgres('dim_region',df_region)
    load_to_postgres('dim_state',df_state)
    load_to_postgres('dim_district',df_disrict)

    print('\n ETL Pipeline Completed Successfully')


if __name__ == "__main__":
     run_pipeline()
    