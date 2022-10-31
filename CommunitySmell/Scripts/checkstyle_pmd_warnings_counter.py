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



#   Conta il numero di warning nella lista compresi tra le righe indicate
def count_warning(start_line , end_line, lines_dict):
    
    try:
        
        #   Counter dei warnings
        count = 0
        
        #    Per ogni riga che di trova tra start ed end cerchiamo nel dizionario
        for line in range(int(start_line),int(end_line)+1):
            
            if line in lines_dict.keys():
                #   Sommiamo a count il valore associato alla chiave line, che è un stringa
                count += lines_dict[str(line)]

        return count

    except Exception:
        print("Errore count warnings")
        print(Exception.__cause__)
    


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
            if elem.attributes('line').value in lines_dict.keys():
                #   aggiorniamo il valore
                lines_dict[elem] = lines_dict[elem] + 1
            else:
                lines_dict[elem] = 1
            

        return lines_dict

    except Exception:
        print("Errore lettura {}".format(checkstyle_path))
        traceback.print_exc()




#   Funzione per leggere il singolo file pmd e contare i warnings e la riga nel quale si trovano
def pmd_read(pmd_path):

    try:
        #   Leggiamo il csv di pmd
        pmd_data = pd.read_csv(pmd_path)

        #   Selezioniamo le righe presenti
        pmd_lines = pmd_data["Line"]
        
        lines_dict = {}

        for elem in pmd_lines :
            #   se la riga considerata è già nel dizionario
            if elem in lines_dict.keys():
                #   aggiorniamo il valore
                lines_dict[elem] = lines_dict[elem] + 1
            else:
                lines_dict[elem] = 1

        #   Ritorna dizionario per ogni riga abbiamo numero di warning
        return lines_dict

    except Exception:
        print("Errore lettura {}".format(pmd_path))
        traceback.print_exc()






if __name__ == "__main__":


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

    #   Path alla cartella contenente tutte le analisi eseguite con pydriller
    pydriller_project_dir = "../../Preprocessing/MetricsDataset"

    #   Dobbiamo leggere uno per uno tutti i dataset
    for repo_analysis in os.listdir(pydriller_project_dir):

        pydriller_dateset_path = pydriller_project_dir+os.sep+repo_analysis

        #   Controlliamo che il file sia corretto
        if os.path.isfile(pydriller_dateset_path) and "pydriller" in repo_analysis and ".csv" in repo_analysis:
            
            print("Pydriller file: "+repo_analysis)
            pydriller_data = pd.read_csv(pydriller_dateset_path)
            print(pydriller_data.head())

            #   Creiamo un nuovo dataset dove inserire i nuovi dati
            #   Leggiamo riga per riga


            break
    
    '''