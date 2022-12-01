#   Script for create dataset with number of SATD added in each period of dataset of CommunitySmells

import os
from shutil import ExecError
import traceback
from numpy import size
import pandas as pd
import git
import argparse


#   Function for read community smells csv dataset and create the 
def community_smell_read(cs_path, satd_path , repo_name, repos_dir, output_dir):
    
    try:
        #   Lettura csv
        print("Lettura community_smell_dataset: "+cs_path)
        community_smell_dataset = pd.read_csv(cs_path)

        #   eliminiamo righe con valori di commit interval vuoti
        #community_smell_dataset = community_smell_dataset.drop(community_smell_dataset[community_smell_dataset.commit_interval == 'NA'].index)
        community_smell_dataset = community_smell_dataset.dropna(axis=0, subset=['commit_interval'])

        print("Lettura satd_path: "+satd_path)
        satd_dataset = pd.read_csv(satd_path)

        #   rimuoviamo i SATD rimossi perche' vogliamo considerare solo quelli introdotti


        repo_path = repos_dir+repo_name+os.sep
        print(repo_path)
        repo = git.Repo(repo_path)

        #   lista numero di satd per periodo
        satd_added_count_column = []
        satd_removed_count_column = []

        #   Numero di righe del dataframe
        lenght = len(community_smell_dataset.index)
        print("Numero di righe del csv: ",lenght)

        #  Leggiamo riga per riga
        for i in range(0,lenght):

            row = community_smell_dataset.iloc[i]
            #print(row)

            #   Potrebbero esserci righe alle quali non e' associato nessun commit
            if str(row['commit_interval']) != 'NA'  :

                #   Start and End Commit
                start_end_commits = str(row['commit_interval']).split('-')

                #   Lista commit da start commit ad end commit
                commits = repo.git.rev_list('--ancestry-path',start_end_commits[0]+'..'+start_end_commits[1])
                
                #   Creiamo lista dei commits
                commitsList = commits.split('\n')

                #   aggiungiamo i commit start ed end
                commitsList.append(start_end_commits[0])
                commitsList.append(start_end_commits[1])

                #   calcoliamo i satd all'interno di questo insieme di commit
                satd_added_count, satd_removed_count= count_satd(satd_dataset,commitsList)
                
                #   Aggiungiamo numero satd alla lista
                satd_added_count_column.append(satd_added_count)
                satd_removed_count_column.append(satd_removed_count) 


        #   Aggiungiamo la nuova colonna
        community_smell_dataset['SATD_added_num'] = satd_added_count_column
        community_smell_dataset['SATD_removed_num'] = satd_removed_count_column

        #   Salviamo il nuovo dataset
        community_smell_dataset.to_csv(output_dir+repo_name+"-communitysmell_satdnum_dataset.csv")

        print("File "+output_dir+repo_name+"-communitysmell_satdnum_dataset SAVED!")

    except Exception:

        print("Errore lettura CommunitySmell file...")
        traceback.print_exc()




#   Function for count the number of satd for the commit list
def count_satd(satd_dataset,commits_list):

    try:
        
        satd_added_count = 0
        satd_removed_count = 0

        for commit in commits_list:
            
            #   filtro per trovare tutte le righe del commit 
            subset_commit = satd_dataset[(satd_dataset['Commit'] == commit) & (satd_dataset['CommentType'] == 'SATD')]
            
            #   controllo che il subset non e' vuoto
            if not subset_commit.empty:

                #   conto numero satd aggiunti e rimossi
                count_changes = subset_commit['TypeOfChange'].value_counts()
                
                if not count_changes.empty :
                    
                    if 'ADDED' in count_changes:
                        count_a  = count_changes['ADDED']
                    else:
                        count_a = 0

                    if 'REMOVED' in count_changes:
                        count_r  = count_changes['REMOVED']
                    else:
                        count_r = 0

                    #  aggiorno numero satd 
                    satd_added_count += count_a
                    satd_removed_count += count_r


        return satd_added_count, satd_removed_count

    except Exception:

        print("Errore ...")
        traceback.print_exc()




if __name__ == "__main__":

    # Args : directory of projects
    parser = argparse.ArgumentParser(
                description='Script for create dataset with number of SATD added and removed in each period of dataset of CommunitySmells')
    
    parser.add_argument(
        'project_name',
        type=str,
        help='Projects name',
    )

    parser.add_argument(
        'community_smell_path',
        type=str,
        help='Community Smells csv dataset path',
    )

    parser.add_argument(
        'satd_path',
        type=str,
        help='Pydriller csv dataset path',
    )

    parser.add_argument(
        'git_repos_dir',
        type=str,
        help='Git repositories directory',
    )

    parser.add_argument(
        'output_dir',
        type=str,
        help='Output path',
    )


    args = parser.parse_args()

    community_smell_read(args.community_smell_path, args.satd_path, args.project_name , args.git_repos_dir, args.output_dir)