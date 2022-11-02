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
from xml.dom import minidom
#   Forziamo utilizzo garbage collection per diminuire memoria utilizzata
import gc



pmd_path = ""
checkstyle_path = ""
fixed_repos_path = ""
output_dir = "../DatasetUpdate/"
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
        checkstyle_xml = minidom.parse(checkstyle_path)

        #   Estraiamo tutti gli errori segnalati da checkstyle
        errors = checkstyle_xml.getElementsByTagName('error')
        
        #   Per ogni errore lo inseriamo all'interno di un dizionario
        lines_dict = {}


        for elem in errors :
            
            #   se la riga considerata è già nel dizionario
            if elem.attributes['line'].value in lines_dict.keys():
                #   aggiorniamo il valore
                lines_dict[ elem.attributes['line'].value ] = lines_dict[elem.attributes['line'].value] + 1
            else:
                lines_dict[ elem.attributes['line'].value ] = 1

        #   Garbage Collector call
        del errors
        del checkstyle_xml 
        gc.collect()    

        return lines_dict

    except Exception:
        print("Errore lettura {}".format(checkstyle_path))
        traceback.print_exc()




#   Funzione per leggere il singolo file pmd e contare i warnings e la riga nel quale si trovano
#   ATTENZIONE, i pmd prodotti inizialmente sono in base al commit quindi possiedono tutti i valori 
#   dei file modificati in quel commit, quindi bisogna modificare l'algoritmo in modo da cacciarsi i valori per i singoli file
def pmd_read(pmd_path, file_path = "", old_v = False):

    try:
        #   Leggiamo il csv di pmd
        pmd_data = pd.read_csv(pmd_path)

        #   Per la vecchia versione dobbiamo filtrare le righe del file che ci interessa
        if old_v :
            #   Il campo File deve contenere il path del file che stiamo analizzando
            pmd_data = pmd_data[file_path in str(pmd_data['File'])]
            
            print(pmd_data)


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

        #   Garbage Collector call
        del pmd_data
        del pmd_lines 
        gc.collect()

        #   Ritorna dizionario per ogni riga abbiamo numero di warning
        return lines_dict

    except Exception:
        print("Errore lettura {}".format(pmd_path))
        traceback.print_exc()





#   Funzione per la creazione dei nuovi dataset con i dati di pmd e checkstyle
def update_dataframe(pydriller_dateset_path, project_name, homonymous_data):

    try:
        print("Pydriller file: "+pydriller_dateset_path)
        pydriller_data = pd.read_csv(pydriller_dateset_path)

        
        #   Numero di righe del dataframe
        lenght = len(pydriller_data.index)
        print("Numero di righe: ",lenght)

        #   Liste nelle quali inserire warning pmd e checkstyle
        #   Come aggiungere una colonna http://pytolearn.csd.auth.gr/b4-pandas/40/moddfcols.html 
        pmd_warnings = []
        checkstyle_warnings = []

        #  Leggiamo riga per riga
        for i in range(0,lenght+1):

            row = pydriller_data.iloc[i]

            print(row['Project'])
            print(row['Commit'])
            print(row['File'])

            #   Per avere prima riga e ultima riga del metodo
            print(str(row['Begin--End']).split('--'))
            
            

            #   Controlliamo se non fa parte degli omonimi
            homonymous = homonymous_data.loc[(homonymous_data['Commit'] == row['Commit']) and (homonymous_data['File'] == row['File'])]
            
            #   Controlliamo che homonymous abbia almeno 1 row
            if len(homonymous) == 1:

                #   I dati devono essere letti dal repository fixed
                #   Cambiamo / in #
                file_name = str(row['File']).replace("/","#")
                
                #   Checkstyle
                checkstyle_file_path = fixed_repos_path+row['Project']+os.sep+row['Commit']+os.sep+file_name+".xml"
                print("checkstyle_file_path: "+checkstyle_file_path)

                checkstyle_dict =  checkstyle_read(checkstyle_file_path)
                cs_count = count_warning(checkstyle_dict)
                checkstyle_warnings.append(cs_count)

                #   PMD
                pmd_file_path = fixed_repos_path+row['Project']+os.sep+row['Commit']+os.sep+file_name+".csv"
                print("pmd_file_path: "+pmd_file_path)
                
                pmd_dict = pmd_read(pmd_file_path)
                pmd_cuont = count_warning(pmd_dict)
                pmd_warnings.append(pmd_cuont)


            else:
                #   Caso non omonimo
                
                #   Checkstyle
                #   Estrapoliamo solo il nome del file che ci serve
                list_s = str(row['Commit']).split("/")
                file_name = list_s[len(list_s)-1]
                checkstyle_file_path = checkstyle_path+row['Project']+os.sep+row['Commit']+os.sep+"checkstyle-"+file_name
                print("checkstyle_file_path: "+checkstyle_file_path)
                
                checkstyle_dict =  checkstyle_read(checkstyle_file_path)
                cs_count = count_warning(checkstyle_dict)
                checkstyle_warnings.append(cs_count)

                #   PMD 
                pmd_file_path = pmd_path+row['Project']+os.sep+row['Commit']+os.sep+"pmd-"+row['Commit']+".csv"
                print("pmd_file_path: "+pmd_file_path)

                pmd_dict = pmd_read(pmd_file_path , str(row['File']), True)
                pmd_cuont = count_warning(pmd_dict)
                pmd_warnings.append(pmd_cuont)


        
        #   Aggiungere le due colonne al dataframe
        pydriller_data['pmd_warnings_numbers'] = pmd_warnings
        
        pydriller_data['checkstyle_warnings_numbers'] = checkstyle_warnings

        #   Creiamo la cartella dove inserire gli output
        if os.path.isdir(output_dir) is False:
                os.mkdir(output_dir)
                print(f"Dir conf create! ")

        #   Salviamo il dataset
        pydriller_data.to_csv(output_dir+"pydriller_checkstyle_pmd_metrics_commons-"+project_name+".csv")

        print(f"File "+output_dir+"pydriller_checkstyle_pmd_metrics_commons-"+project_name+".csv SAVED!")

        #   Garbage Collector call
        del pydriller_data
        del pmd_dict
        del pmd_warnings 
        del checkstyle_dict
        del checkstyle_warnings
        gc.collect()

    except Exception:
        print("Errore in update_dataframe ...")
        traceback.print_exc()





if __name__ == "__main__":

    '''
    # TEST
    path_xml = "/home/stefano/SATD-Analysis/Preprocessing/1ace3061217340e4d5dae67d75532ec48efe32fb/tests#timing-tests#src#test##org#apache#activemq#artemis#tests#timing#core#server#impl#QueueImplTest.xml"
    path_csv = "/home/stefano/SATD-Analysis/Preprocessing/1ace3061217340e4d5dae67d75532ec48efe32fb/tests#unit-tests#src#test##org#apache#activemq#artemis#tests#unit#core#server#impl#QueueImplTest.csv"

    pmd_warnings_dict = pmd_read(path_csv)
    print(pmd_warnings_dict)
    print()


    checkstyle_warnings_dict = checkstyle_read(path_xml)
    print(checkstyle_warnings_dict)
    print()

    print("Numero warnings pmd: ",count_warning('0','2000',pmd_warnings_dict))
    print()
    print("Numero warnings checkstyle: ",count_warning('0','2000',checkstyle_warnings_dict))

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
            #print(pydriller_data.head())

            #   Creiamo un nuovo dataset dove inserire i nuovi dati
            #   Leggiamo riga per riga
            break

            
    