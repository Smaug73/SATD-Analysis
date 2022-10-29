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
from numpy import size
import pandas as pd




#   Conta il numero di warning nella lista compresi tra le righe indicate
def count_warning(start_line , end_line):
    print()
    #   Ritorno il numero di warning



#   Per queste funzioni di count dei warning basta devono ritornare un dictionary all'interno del quale
#   abbiamo come chiave la riga e come value il numero di warning per riga (non sappiamo se possono esserci più
#   warning per riga)

#   Funzione per leggere il singolo file checkstyle e contare i warnings e la riga dove si trovano
def checkstyle_read(checkstyle_path):
    print()
    #   Ritorna una lista contenente per ogni warning la riga nella quale si trova(effetivamente serve anche solo la riga nella quale si trova)


#   Funzione per leggere il singolo file pmd e contare i warnings e la riga nel quale si trovano
def pmd_read(pmd_path):

    try:
        #   Leggiamo il csv di pmd
        pmd_data = pd.read_csv(pmd_path)

        #   Selezioniamo le righe presenti
        pmd_lines = pmd_data["Line"]
        
        lines_dict = {}

        for elem in pmd_lines :

            if lines_dict.has_key(elem):
                #   aggiorniamo il valore
                lines_dict
        #   Ritorna una lista nella quale per ogni warning abbiamo la riga nella quale si trova(serve anche solo la riga)

    except Exception:
        print("Errore lettura {}".format(pmd_path))
        print(Exception.__cause__)






if __name__ == "__main__":

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
