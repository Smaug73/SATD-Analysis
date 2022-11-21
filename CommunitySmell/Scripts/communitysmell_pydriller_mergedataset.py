#   Script for the join of community smell csv and pydriller csv





import os
from shutil import ExecError
import traceback
from numpy import size
import pandas as pd
import git
#   Forziamo utilizzo garbage collection per diminuire memoria utilizzata
import gc



#   Path utili
pydriller_project_path = "/home/stefano/SATD-Analysis/CommunitySmell/dataset-finale/cayenne_dataset.csv"
community_smell_path = "/home/stefano/SATD-Analysis/CommunitySmell/kaiaulu/rawdata/smell_data/cayenne_community_smells.csv"
repos_dir = "/home/stefano/SATD-Analysis/CommunitySmell/Repo/"
output_dir = "/home/stefano/SATD-Analysis/CommunitySmell/dataset-finale/"



#   Funzione per la lettura dei file riguardante i Community Smell
def community_smell_read( cs_path , repo_name):
    
    try:

        print("Lettura : "+cs_path)
        community_smell_dataset = pd.read_csv(cs_path)

        repo_path = repos_dir+repo_name+os.sep
        print(repo_path)
        repo = git.Repo(repo_path)

        #   Associo ad ogni commit la riga del file corrispondente
        commit_row_dict = {}

        #   Numero di righe del dataframe
        lenght = len(community_smell_dataset.index)
        print("Numero di righe del csv: ",lenght)

        #  Leggiamo riga per riga
        for i in range(0,lenght):

            print("Analisi riga: ",i)

            row = community_smell_dataset.iloc[i]

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
                
                #   Aggiungiamo ogni commit al dictionary
                for commit in commitsList:
                    commit_row_dict[commit] = row

        #   Ritorniamo il dizionario
        return commit_row_dict


    except Exception:

        print("Errore lettura CommunitySmell file...")
        traceback.print_exc()






#   Funzione per creare dataset aggiornato
def update_dataframe( pydriller_path, commits_dict , project_name):

    try:

        print("Pydriller file: "+pydriller_path)
        pydriller_data = pd.read_csv(pydriller_path)

        
        #   Numero di righe del dataframe
        lenght = len(pydriller_data.index)
        print("Numero di righe del csv: ",lenght)                      

        # Nuove colonne
        org_silo = []
        missing_links = []
        radio_silence = []
        st_congruence = []
        num_tz = []
        code_only_devs = []
        code_files = []
        ml_only_devs = []
        ml_threads = []
        code_ml_both_devs = []

        #  Leggiamo riga per riga
        for i in range(0,lenght):
            
            row = pydriller_data.iloc[i]

            #   Controlliamo che cs_row non sia vuoto 
            if row['Commit'] in commits_dict.keys():

                #   Per ogni commit cerchiamo nel dizionario e aggiorniamo le nuove colonne
                cs_row = commits_dict[row['Commit']]

                #   Aggiungiamo valori alle colonne
                org_silo.append(cs_row['org_silo'])
                missing_links.append(cs_row['missing_links'])
                radio_silence.append(cs_row['radio_silence'])
                st_congruence.append(cs_row['st_congruence'])
                num_tz.append(cs_row['num_tz'])
                code_only_devs.append(cs_row['code_only_devs'])
                code_files.append(cs_row['code_files'])
                ml_only_devs.append(cs_row['ml_only_devs'])
                ml_threads.append(cs_row['ml_threads'])
                code_ml_both_devs.append(cs_row['code_ml_both_devs'])
            
            else:
                #   Se non e' presente il commit preso in considerazione aggiungiamo tutti valori vuoti
                org_silo.append(None)
                missing_links.append(None)
                radio_silence.append(None)
                st_congruence.append(None)
                num_tz.append(None)
                code_only_devs.append(None)
                code_files.append(None)
                ml_only_devs.append(None)
                ml_threads.append(None)
                code_ml_both_devs.append(None)


        #   Aggiungere le due colonne al dataframe
        pydriller_data['org_silo'] = org_silo
        pydriller_data['missing_links'] = missing_links
        pydriller_data['radio_silence'] = radio_silence
        pydriller_data['st_congruence'] = st_congruence
        pydriller_data['num_tz'] = num_tz
        pydriller_data['code_only_devs'] = code_only_devs
        pydriller_data['code_files'] = code_files
        pydriller_data['ml_only_devs'] = ml_only_devs
        pydriller_data['ml_threads'] = ml_threads
        pydriller_data['code_ml_both_devs'] = code_ml_both_devs

        #   Creiamo la cartella dove inserire gli output
        if os.path.isdir(output_dir) is False:
                os.mkdir(output_dir)
                print(f"Dir conf create! ")

        #   Salviamo il dataset
        pydriller_data.to_csv(output_dir+project_name+"-CS_dataset"+".csv")

        print("File "+output_dir+project_name+"-CS_dataset SAVED!")
        


            


    except Exception:

        print("Errore lettura update_dataframe ...")
        traceback.print_exc()

    finally:
    #   Garbage Collector call
        del pydriller_data
        gc.collect()







if __name__ == "__main__":

    '''
    #   Dobbiamo leggere uno per uno tutti i dataset
    for repo_analysis in os.listdir(pydriller_project_dir):

        pydriller_dateset_path = pydriller_project_dir+os.sep+repo_analysis

        #   Controlliamo che il file sia corretto
        if os.path.isfile(pydriller_dateset_path) and "pydriller" in repo_analysis and ".csv" in repo_analysis:
            
            #   Nome del repository
            repo_name = repo_analysis[18:]
            repo_name = repo_name[:-4]
            
            #   Path community smell csv
            cs_path = community_smell_dir+repo_name+'_community_smells.csv'
            
            #   Creiamo dizionario commit   
            commits_dict =  community_smell_read( cs_path , repo_name)

            #   Creiamo nuovo dataset
            update_dataframe (pydriller_dateset_path, commits_dict, repo_name)

            #   Cancelliamo il dizionario dei commit
            del commits_dict
            gc.collect()
    
    '''

    commits_dict =  community_smell_read( community_smell_path , 'cayenne')
    print(commits_dict)

    update_dataframe (pydriller_project_path, commits_dict, 'cayenne')
