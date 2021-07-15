import single_covid_experiment
import create_datasets

n_his = 12
n_pred = 3
ATTR_type = ['delta', 'delta7', 'total']
ATTR_val = ['confirmed', 'deceased', 'recovered']
time_intvl = 1
stblock_num = 2
Kt = 3

exp_no = 1

for attr_type in ATTR_type:
    for attr_val in ATTR_val:
        create_datasets.get_all_data(ATTR_type, ATTR_val)
        
        print('Dataset written for {} and {} type'. format(attr_type, attr_val))
        
        scalar_point = attr_type +' | '+ attr_val
        
        
        single_covid_experiment.create_experiments(exp_no, n_his, n_pred, Kt,time_intvl, stblock_num ,scalar_point)
        
        exp_no+=1