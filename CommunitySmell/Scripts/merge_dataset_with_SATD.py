import os
from shutil import ExecError
import traceback
from numpy import size
import pandas as pd
import argparse





#   Ci deve essere almeno un SATD per metodo per aggiungere la label SATD
#   Funzione per creare dataset aggiornato
def update_dataframe( pydriller_dataset, satd_dataset , satd_path, output_path, project_name):

    try:

        #   Prendere solo quelli che sono added dei SATD
        satd_dataset.query("TypeOfChange == 'ADDED'" , inplace = True)

        print("Inizio modifica dataset SATD")

        #   Ci deve essere una riga per ogni metodo, per ogni metodo dobbiamo vedere se c'e' almeno un SATD
        commits = satd_dataset['Commit'].unique()
        lenght = len(commits)

        # Nuovo dataset
        rows = []
        i=0

        for commit in commits:
            
            i=i+1
            #   Percentuale
            perc = i * 100 / lenght
            if perc % 5 == 0 :
                print("Percentuale commits: ",perc," %")

            #   New subset
            subset_commit = satd_dataset[satd_dataset['Commit'] == commit]

            #   Prendo i files commit corrente
            modified_files = subset_commit['File'].unique()

            for file in modified_files:
                
                file_subset = subset_commit[subset_commit['File'] == file]

                methods = file_subset['Signature'].unique()

                for method in methods:
                    
                    methods_subset = file_subset[file_subset['Signature'] == method]

                    if not methods_subset.empty : 
                        #print(methods_subset)
                        if 'SATD' in methods_subset['CommentType']:
                            #   Cerchiamo la prima riga con il SATD
                            old_row = methods_subset[methods_subset['CommentType'] == 'SATD']
                            #print(old_row)
                            #   Aggiungiamo la riga per questo metodo contente il SATD
                            rows.append(old_row.iloc[0])

                        else:
                            #print(methods_subset.iloc[0])
                            #   Aggiungiamo la riga, indica che non contiene il SATD in questo caso
                            rows.append(methods_subset.iloc[0])

        #   Salviamo dataset nuovo degli SATD, questo conterra' solo se c'e' oppure no SATD in un metodo
        new_satd_dataset = pd.DataFrame(rows, columns =  satd_dataset.columns)
        new_satd_dataset.to_csv( satd_path+'-NEW-only-one-method-only-added-SATD' + '.csv', index=False)

        print("SATD DATASET MODIFICATO")

        #   Aggiungere la colonna end a entrambi
        new_satd_dataset['end-method'] = new_satd_dataset.apply(lambda row: end_method(row), axis=1)
        pydriller_dataset['end-method']= pydriller_dataset.apply(lambda row: end_method(row), axis=1)

        #   fare il merge usando come chiave "Commit","File","End"
        new_data = pd.merge(new_satd_dataset,pydriller_dataset, on=["Commit","File","end-method"], how='left')
        print("MERG ESEGUITO")
        #new_data['checkstyle_warnings_numbers']=new_data['checkstyle_warnings_numbers'].fillna(0)
        #new_data['pmd_warnings_numbers']=new_data['pmd_warnings_numbers'].fillna(0)
        
        #new_data.to_csv('/home/stefano/SATD-Analysis/CommunitySmell/SATD_pydriller_warning_merge/SATD-pydriller-warnings-asterixdb.csv')
        new_data.to_csv(output_path+project_name+'-FINAL.csv')
        

    except Exception:

        print("Errore ...")
        traceback.print_exc()



# Restituisce la riga di terminazione del metodo
def end_method (str):
    return str['Begin--End'].split("--")[1]





def update_satd_dataset(satd_dataset, satd_path) :

    try:
        #   Ci deve essere una riga per ogni metodo, per ogni metodo dobbiamo vedere se c'e' almeno un SATD
        commits = satd_dataset['Commit'].unique()

        # Nuovo dataset
        rows = []

        for commit in commits:

            #   New subset
            subset_commit = satd_dataset[satd_dataset['Commit'] == commit]

            #   Prendo i files commit corrente
            modified_files = subset_commit['File'].unique()

            for file in modified_files:
                
                file_subset = subset_commit[subset_commit['File'] == file]

                methods = file_subset['Signature'].unique()

                for method in methods:

                    methods_subset = file_subset[file_subset['Signature'] == method]

                    if True in methods_subset['CommentType'].isin(['SATD']):
                        #   Cerchiamo la prima riga con il SATD
                        old_row = methods_subset[methods_subset['CommentType'] == 'SATD']
                        rows.append(old_row[0])

                    else:
                        rows.append(methods_subset[0])

        #   Salviamo dataset nuovo
        new_satd_dataset = pd.DataFrame(rows, columns =  satd_dataset.columns)
        new_satd_dataset.to_csv( satd_path+'-NEW' + '.csv', index=False)


    except Exception:

        print("Errore lettura CommunitySmell file...")
        traceback.print_exc()





if __name__ == "__main__":


    # Args : directory of projects
    parser = argparse.ArgumentParser(
                description='Script for merge SATD dataset with pydriller-slope-warning dataset')
    
    parser.add_argument(
        'project_name',
        type=str,
        help='Projects name',
    )

    parser.add_argument(
        'satd_dataset_path',
        type=str,
        help='SATD csv dataset path',
    )

    parser.add_argument(
        'pydriller_project_path',
        type=str,
        help='Pydriller csv dataset path',
    )

    parser.add_argument(
        'output_dir',
        type=str,
        help='Output path',
    )


    args = parser.parse_args()
    
    #   Load pydriller csv
    pydriller_dataset = pd.read_csv(args.pydriller_project_path)

    #   Load SATD csv
    satd_dataset = pd.read_csv(args.satd_dataset_path, sep=",")


    #   Update dataframe
    update_dataframe(pydriller_dataset, satd_dataset, args.satd_dataset_path , args.output_dir , args.project_name )

