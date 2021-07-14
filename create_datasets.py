import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests



code = 'MH' #State name
data = requests.get('https://api.covid19india.org/v4/min/timeseries-{}.min.json'.format(code)) #API
data = data.json()

city_list = list(data[code]['districts'].keys())

def get_data_by_district(district_name, SKIP_START=0, SKIP_END=0, TOTAL_LEN=444):
    #district_name = 'Akola'
    data_per_day = data[code]['districts'][district_name]['dates']   
    # node feature vector data for each day

    ATTR_LIST = ['confirmed', 'deceased', 'recovered', 'vaccinated1', 'vaccinated2']
    ALL_KEYS = ['delta', 'delta7', 'total']

    DISTRICT_INFO_DICT = {}

    ctr = 0
    for date in data_per_day:
        ctr+=1
        if ctr<=SKIP_START:
            continue
        if ctr >= TOTAL_LEN - SKIP_END:
            continue
        
        day_data = data_per_day[date]

        daily_info_dict = {}

        for key in ALL_KEYS:
            daily_info_dict[key] = []
            for attr in ATTR_LIST:
                daily_info_dict[key].append(day_data.get(key, {}).get(attr, 0))

        DISTRICT_INFO_DICT[date] = daily_info_dict
    
    return DISTRICT_INFO_DICT, min(DISTRICT_INFO_DICT.keys()), max(DISTRICT_INFO_DICT.keys())


#GET dataframe of cases for all cities
init_skip_val = 15
end_skip_val = 1

DISTRICT_NAMES = ['ahmednagar', 'akola', 'amravati', 'aurangabad', 'beed',
       'bhandara', 'buldhana', 'chandrapur', 'dhule', 'gadchiroli',
       'gondia', 'hingoli', 'jalgaon', 'jalna', 'kolhapur', 'latur',
       'mumbai', 'nagpur', 'nanded', 'nandurbar', 'nashik', 'osmanabad',
       'palghar', 'parbhani', 'pune', 'ratnagiri', 'sangli', 'satara',
       'sindhudurg', 'solapur', 'thane', 'wardha', 'washim', 'yavatmal']

SKIP_DISTRICTS = ['Gadchiroli', 'Wardha']

ALL_DISTRICT_DATA = dict()

ctr = 0
for NAME in DISTRICT_NAMES:
    NAME = NAME.title().strip()
    if NAME in SKIP_DISTRICTS:
        print("Skipping: ", NAME)
        continue
    
    ALL_DISTRICT_DATA[NAME], min_val, max_val = get_data_by_district(NAME, SKIP_START=init_skip_val, SKIP_END=end_skip_val)
    
    print(NAME, ": ", len(ALL_DISTRICT_DATA[NAME].keys()), " | ", min_val, max_val)
    print('---'*4)
    
print("--------------------------------")
print("All Districts: ", len(ALL_DISTRICT_DATA.keys()))



def transform_func(x, ATTR_type, i):
    if pd.isnull(x):
        return 0
    else:
        val = x[ATTR_type][i]
        return val
        

#Create single scalar dataframe for selected datatype
def create_TxN_df(dict_data, ATTR_type, ATTR_val):
    df = pd.DataFrame.from_dict(ALL_DISTRICT_DATA)
    
    if ATTR_val == 'confirmed':
        i = 0
        
    elif ATTR_val == 'deceased':
        i = 1
        
    elif ATTR_val == 'recovered':
        i = 2
        
    for col in df.columns:
        df[col] = df[col].apply(lambda x: transform_func(x, ATTR_type, i))
        
    return df

print(os.getcwd())
        
vector_df = create_TxN_df(ALL_DISTRICT_DATA, 'delta7', 'confirmed')
pd.DataFrame(vector_df.values).to_csv('data/train/road_traffic/covid/vel.csv', header =False, index = False) #Save file

#create Adjacency matrix
df_adj = pd.read_csv('adjacency_matrix.csv')
df_adj = df_adj[~df_adj['city1'].isin([x.lower() for x in SKIP_DISTRICTS])]
df_adj = df_adj[~df_adj['city2'].isin([x.lower() for x in SKIP_DISTRICTS])]
df_adj['distance'] = df_adj['distance']/ max(df_adj['distance'])
adj_finl_data = df_adj.pivot_table('distance', ['city1'], 'city2')

print(os.getcwd())

pd.DataFrame(adj_finl_data.values).to_csv('data/train/road_traffic/covid/adj_mat.csv', header = False, index = False) #Save file