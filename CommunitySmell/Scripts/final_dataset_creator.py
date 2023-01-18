import traceback
from numpy import size
import pandas as pd
import argparse
import os



dataset_folder = '/home/stefano/SATD-Analysis/CommunitySmell/dataset-finale/dataset-FINALI-communitysmells/'




columns = [
'missing_links',
'org_silo',
'radio_silence',
'Project',
'Commit',
'#Parameters',
'NLOC',
'Complexity',
'NLOC_slope',
'Params_slope',
'Complexity_slope',
'pmd_warnings_numbers',
'checkstyle_warnings_numbers',
'org_silo',
'missing_links',
'radio_silence',
'CommentType']

datas = []

for f in os.scandir(dataset_folder):
        
        if f.name.endswith('.csv') :
            
            print(f.name)

            df = pd.read_csv(dataset_folder+f.name, usecols = columns)

            datas.append(df)

print(datas)

result = pd.concat(datas,ignore_index=True)

result = result.fillna(0.0)

result.to_csv(dataset_folder+"totale-CS_dataset.csv")
