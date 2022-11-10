#   Script per il conteggio dei warning all'interno di checkstyle e generazione di csv
#   Il conteggio va fatto a livello di metodo, per capire se un warning si trova all'interno di un metodo
#   va visto l'informazione sulle line dal dataset costruito con pydriller e la line del warning dal xml di checkstyle

#   Nei file costruiti con pydriler c'e' una label Begin--End che ci dice inizio e fine di un metodo
#   Abbiamo una riga per ogni metodo di una classe per ogni commit, e di conseguenza dove inizia e finisce il metodo
#   Per quanto riguarda il csv di pmd abbiamo il nome della label File scritta allo stesso modo di quello di pydriller

#   Per ogni metodo presente nei dataset di pydriller dobbiamo aggiungere il numero di warning checkstyle

#   Cose di cui tenere conto:   File omonimi, cercare di capire come aggiungere i Community Smell all'interno del dataset


#   Step:
#   1   Leggere csv pydriller di un certo progetto e il csv contenente gli omonimi

#   2   Leggere commit per commit:
#           2.1 Per ogni file del commit preso in considerazione:
    #           3.1 Controllare che non abbia omonimi
    #           3.2 Leggere file pmd e checkstyle

    #           3.3 Per ogni medoto all'interno di quel file:
    #                   4.1 cercare il file pmd e checkstyle usando il commit per orientarci tra le cartelle
    #                   4.2 contare warning checkstyle e pmd per quel metodo controllando la riga nella quale di trova
    #                   4.3 aggiungere l'informazione all'interno del csv di pydriller


import os
from shutil import ExecError
import traceback
from numpy import size
import pandas as pd
import xml.etree.ElementTree as ET
import argparse
#   Forziamo utilizzo garbage collection per diminuire memoria utilizzata
import gc



pmd_path = ""
checkstyle_path = ""
fixed_repos_path = ""
output_dir = "../pmd_checkstyle_dataset_update/"
homonymous_file_csv =  ""
#   Path alla cartella contenente tutte le analisi eseguite con pydriller
pydriller_project_dir = "../../Preprocessing/MetricsDataset"


#   Conta il numero di warning nella lista compresi tra le righe indicate
def count_warning(start_line , end_line, lines_dict):
    
    try:
        #   Counter dei warnings
        count = 0
    
        #    Per ogni riga che di trova tra start ed end cerchiamo nel dizionario
        for line in range(int(start_line),int(end_line)+1):
            
            if str(line) in lines_dict.keys():
                #   Sommiamo a count il valore associato alla chiave line, che è un stringa
                count += lines_dict[str(line)]

        return count

    except Exception:
        print("Errore count warnings")
        traceback.print_exc()
    





#   Per queste funzioni di count dei warning basta ritornare un dictionary all'interno del quale
#   abbiamo come chiave la riga e come value il numero di warning per riga (non sappiamo se possono esserci più
#   warning per riga)

#   Funzione per leggere il singolo file checkstyle e contare i warnings e la riga dove si trovano
def checkstyle_read(checkstyle_path):

    try:
        #   Leggiamo il file xml dell'analisi di checkstyle
        checkstyle_xml = ET.parse(checkstyle_path)

        #   Estraiamo tutti gli errori segnalati da checkstyle
        root = checkstyle_xml.getroot()
        root = root.find('file')
        errors = root.findall('error')
        
        #   Per ogni errore lo inseriamo all'interno di un dizionario
        lines_dict = {}

        for elem in errors :
            
            #   se la riga considerata è già nel dizionario
            if elem.get('line') in lines_dict.keys():
            #   aggiorniamo il valore
                lines_dict[ elem.get('line') ] = lines_dict[elem.get('line')] + 1
            else:
                lines_dict[ elem.get('line') ] = 1

      
        return lines_dict

    except Exception:
        print("Errore checkstyle_read {}".format(checkstyle_path))
        traceback.print_exc()

    finally:
    #   Garbage Collector call
        del errors
        del checkstyle_xml 
        gc.collect()




#   Funzione per leggere il singolo file pmd e contare i warnings e la riga nel quale si trovano
#   ATTENZIONE, i pmd prodotti inizialmente sono in base al commit quindi possiedono tutti i valori 
#   dei file modificati in quel commit, quindi bisogna modificare l'algoritmo in modo da cacciarsi i valori per i singoli file
def pmd_read(pmd_path, file_path = "", old_v = False):

    try:
        #   Leggiamo il csv di pmd
        pmd_data = pd.read_csv(pmd_path)

        #   Per la vecchia versione dobbiamo filtrare le righe del file che ci interessa
        if old_v :
            #   Il campo File deve contenere il nome del file che stiamo analizzando
            split_path = str(file_path).split("/")
            file_name = split_path[len(split_path)-1]
            #   Selezioniamo solo le righe che contengono il nome del file da analizzare
            pmd_data = pmd_data[pmd_data['File'].str.contains(file_name)]
            

        #   Selezioniamo le righe presenti
        pmd_lines = pmd_data["Line"]
        
        lines_dict = {}

        for elem in pmd_lines :
            #   se la riga considerata è già nel dizionario
            if elem in lines_dict.keys():
                #   aggiorniamo il valore
                lines_dict[str(elem)] = lines_dict[str(elem)] + 1
            else:
                lines_dict[str(elem)] = 1

        #   Ritorna dizionario per ogni riga abbiamo numero di warning
        return lines_dict

    except Exception:
        print("Errore pmd_read: {}".format(pmd_path))
        traceback.print_exc()
    
    finally:
        #   Garbage Collector call
        del pmd_data
        del pmd_lines 
        gc.collect()







#   Funzione per la creazione dei nuovi dataset con i dati di pmd e checkstyle
def update_dataframe(pydriller_dateset_path, project_name, homonymous_data):

    try:
        print("Pydriller file: "+pydriller_dateset_path)
        pydriller_data = pd.read_csv(pydriller_dateset_path)

        
        #   Numero di righe del dataframe
        lenght = len(pydriller_data.index)
        print("Numero di righe del csv: ",lenght)

        #   Liste nelle quali inserire warning pmd e checkstyle
        #   Come aggiungere una colonna http://pytolearn.csd.auth.gr/b4-pandas/40/moddfcols.html 
        pmd_warnings = []
        checkstyle_warnings = []


        #  Leggiamo riga per riga
        for i in range(0,lenght):
            
            #   Percentuale
            perc = i * 100 / lenght
            if perc % 5 == 0 :
                print("Percentuale righe: ",perc," %")

            row = pydriller_data.iloc[i]
            
            #   Inizio e fine metodo
            start_end_method_index = str(row['Begin--End']).split('--')
            

            #   Controlliamo se non fa parte degli omonimi
            homonymous = homonymous_data.loc[(homonymous_data['Commit'] == row['Commit']) & (homonymous_data['File'] == row['File'])]
            
            #   Controlliamo che homonymous abbia almeno 1 row
            if len(homonymous) == 1:
                
                print("Il file è presenete nella lista degli OMONIMI")
                #   I dati devono essere letti dal repository fixed
                #   Cambiamo / in #
                file_name = str(row['File']).replace("/","#")

                file_name_checkstyle = file_name[:-4]+"xml"
                file_name_pmd = file_name[:-4]+"csv"

                try:
                    #   Checkstyle
                    checkstyle_file_path = fixed_repos_path+row['Project']+os.sep+row['Commit']+os.sep+file_name_checkstyle
                    #print("checkstyle_file_path: "+checkstyle_file_path)

                    checkstyle_dict =  checkstyle_read(checkstyle_file_path)
                    cs_count = count_warning(start_end_method_index[0], start_end_method_index[1],checkstyle_dict)
                
                except Exception:
                    print("Errore lettura file Checkstyle..."+checkstyle_file_path)
                    traceback.print_exc()
                    #   Per mantenere la consistenza all'interno del file count lo assegnamo a None in modo
                    cs_count = None
                    print("\nPercentuale righe: ",perc," % \n")

                #   Aggiorniamo lista Checkstyle
                checkstyle_warnings.append(cs_count)

                #   PMD
                try:
                    pmd_file_path = fixed_repos_path+row['Project']+os.sep+row['Commit']+os.sep+file_name_pmd
                    print("pmd_file_path: "+pmd_file_path)

                    pmd_dict = pmd_read(pmd_file_path)
                    pmd_count = count_warning(start_end_method_index[0], start_end_method_index[1],pmd_dict)

                except Exception:
                    print("Errore lettura file PMD..."+pmd_file_path)
                    traceback.print_exc()
                    #   Per mantenere la consistenza all'interno del file count lo assegnamo a None 
                    pmd_count = None
                    print("\nPercentuale righe: ",perc," % \n")

                #   Aggiorniamo lista PMD
                pmd_warnings.append(pmd_count)



            else:
                #   Caso non omonimo
                #print("Il file NON HA OMONIMI")

                try:
                    #   Checkstyle
                    #   Estrapoliamo solo il nome del file che ci serve
                    list_s = str(row['File']).split("/")
                    file_name = list_s[len(list_s)-1]
                    file_name = file_name[:-4]+"xml"

                    checkstyle_file_path = checkstyle_path+row['Project']+os.sep+row['Commit']+os.sep+"checkstyle-"+file_name
                    #print("checkstyle_file_path: "+checkstyle_file_path)
                    
                    checkstyle_dict =  checkstyle_read(checkstyle_file_path)
                    cs_count = count_warning(start_end_method_index[0], start_end_method_index[1], checkstyle_dict)
                
                except Exception:
                    print("Errore lettura file Checkstyle..."+checkstyle_file_path)
                    traceback.print_exc()
                    #   Per mantenere la consistenza all'interno del file count lo assegnamo a None 
                    cs_count = None
                    print("\nPercentuale righe: ",perc," % \n")
                
                #   Aggiorniamo lista warning checkstyle
                checkstyle_warnings.append(cs_count)


                try:
                    #   PMD 
                    pmd_file_path = pmd_path+row['Project']+os.sep+row['Commit']+os.sep+"pmd-"+row['Commit']+".csv"
                    #print("pmd_file_path: "+pmd_file_path)

                    pmd_dict = pmd_read(pmd_file_path , str(row['File']), True)
                    pmd_count = count_warning(start_end_method_index[0], start_end_method_index[1], pmd_dict)

                except Exception:
                    print("Errore lettura file PMD..."+pmd_file_path)
                    traceback.print_exc()
                    #   Per mantenere la consistenza all'interno del file count lo assegnamo a None
                    pmd_count = None
                    print("\nPercentuale righe: ",perc," % \n")

                #   Aggiorniamo lista warning pmd
                pmd_warnings.append(pmd_count)


        
        #   Aggiungere le due colonne al dataframe
        pydriller_data['pmd_warnings_numbers'] = pmd_warnings
        
        pydriller_data['checkstyle_warnings_numbers'] = checkstyle_warnings

        #   Creiamo la cartella dove inserire gli output
        if os.path.isdir(output_dir) is False:
                os.mkdir(output_dir)
                print(f"Dir conf create! ")

        #   Salviamo il dataset
        pydriller_data.to_csv(output_dir+"pydriller_checkstyle_pmd_metrics_commons-"+project_name)

        print("File "+output_dir+"pydriller_checkstyle_pmd_metrics_commons-"+project_name+" SAVED!")


    except Exception:
        print("Errore in update_dataframe ...")
        traceback.print_exc()

    finally:
    #   Garbage Collector call
        del pydriller_data
        del pmd_dict
        del pmd_warnings 
        del checkstyle_dict
        del checkstyle_warnings
        gc.collect()








if __name__ == "__main__":

    # Args : directory of projects
    parser = argparse.ArgumentParser(
                description='Script for download mbox file for an apache project')

    # Apache project name
    parser.add_argument(
        'project_name',
        type=str,
        help='Apache projects name',
    )

    # Apache projects directory
    parser.add_argument(
        'git_repos_dir',
        type=str,
        help='Git repositories directory',
    )

    # pydriller_project_dir file
    parser.add_argument(
        'pydriller_project_dir',
        type=str,
        help='Pydriller repositories',
    )

    # Pmd directory
    parser.add_argument(
        'pmd_path',
        type=str,
        help='PMD repository directory',
    )

    # Checkstyle repository
    parser.add_argument(
        'checkstyle_path',
        type=str,
        help='Checkstyle repository directory',
    )

    # homonymous_file_csv file
    parser.add_argument(
        'homonymous_file_csv',
        type=str,
        help='Homonymous csv file',
    )

    # fixed_repos_path file
    parser.add_argument(
        'fixed_repos_path',
        type=str,
        help='Fixed repositories of homonimous files',
    )


    # output directory
    parser.add_argument(
        'output_dir',
        type=str,
        help='Output directory',
    )

    args = parser.parse_args()


    #   Carichiamo gli omonimi
    homonymous_data = pd.read_csv(args.homonymous_file_csv)
    output_dir = args.output_dir
    checkstyle_path = args.checkstyle_path
    pmd_path = args.pmd_path
    git_repos_dir = args.git_repos_dir
    fixed_repos_path = args.fixed_repos_path
    pydriller_project_dir = args.pydriller_project_dir


    #   Avviamo l'analisi
    pydriller_dateset_path = args.pydriller_project_dir + "pydriller_metrics_" + args.project_name + ".csv"

    if os.path.isfile(pydriller_dateset_path) :
            update_dataframe(pydriller_dateset_path, args.project_name, homonymous_data)

    '''
    #   Carico dataset file omonimi 
    print("Loading homonymous file dataset: "+homonymous_file_csv)
    homonymous_data = pd.read_csv(homonymous_file_csv)

    #   Dobbiamo leggere uno per uno tutti i dataset
    for repo_analysis in os.listdir(pydriller_project_dir):

        pydriller_dateset_path = pydriller_project_dir+os.sep+repo_analysis

        #   Controlliamo che il file sia corretto
        if os.path.isfile(pydriller_dateset_path) and "pydriller" in repo_analysis and ".csv" in repo_analysis:


            update_dataframe(pydriller_dateset_path, repo_analysis, homonymous_data)
     '''      
            
    