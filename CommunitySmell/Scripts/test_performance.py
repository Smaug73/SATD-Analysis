import os
import pandas as pd
from xml.dom import minidom
import time



#   Test pandas speed
def test_pandas(file_path):
    t = time.process_time()
    #do some stuff
    pmd_data = pd.read_csv(file_path)

    elapsed_time = time.process_time() - t
    print("Tempo di esecuzione : ",elapsed_time)
    
    return pmd_data


def test_pandas_search(data):
    t = time.process_time()
    #do some stuff
    #   Selezioniamo le righe presenti
    pmd_lines = data["Line"]
    
    lines_dict = {}

    for elem in pmd_lines :
        #   se la riga considerata è già nel dizionario
        if elem in lines_dict.keys():
            #   aggiorniamo il valore
            lines_dict[str(elem)] = lines_dict[str(elem)] + 1
        else:
            lines_dict[str(elem)] = 1


    elapsed_time = time.process_time() - t
    print("Tempo di esecuzione: ",elapsed_time)




def test_xml_dom(file_path):
    t = time.process_time()
    #do some stuff
    checkstyle_xml = minidom.parse(file_path)
    elapsed_time = time.process_time() - t
    print("Tempo di esecuzione: ",elapsed_time)

    return checkstyle_xml



def xml_dom_search(data):
    t = time.process_time()
    
    #do some stuff
    #   Estraiamo tutti gli errori segnalati da checkstyle
    errors = data.getElementsByTagName('error')
    
    #   Per ogni errore lo inseriamo all'interno di un dizionario
    lines_dict = {}

    for elem in errors :
        
        #   se la riga considerata è già nel dizionario
        if elem.attributes['line'].value in lines_dict.keys():
            #   aggiorniamo il valore
            lines_dict[ elem.attributes['line'].value ] = lines_dict[elem.attributes['line'].value] + 1
        else:
            lines_dict[ elem.attributes['line'].value ] = 1


    elapsed_time = time.process_time() - t
    print("Tempo di esecuzione: ",elapsed_time)
    print("Numero warning: ",len(errors))
    print(lines_dict.keys())
    print(lines_dict.values())




def test_xml_etree(file_path):
    
    import xml.etree.ElementTree as ET
    
    t = time.process_time()
    #do some stuff
    checkstyle_xml = ET.parse(file_path)

    elapsed_time = time.process_time() - t
    print("Tempo di esecuzione: ",elapsed_time)

    return checkstyle_xml




def xml_tree_search(data):
    print(data)

    t = time.process_time()
    
    #do some stuff
    #   Estraiamo tutti gli errori segnalati da checkstyle
    root = data.getroot()
    root = root.find('file')
    print(root.attrib)
    errors = root.findall('error')
    #print(errors)
    #   Per ogni errore lo inseriamo all'interno di un dizionario
    lines_dict = {}

    for elem in errors :
        
        #   se la riga considerata è già nel dizionario
        if elem.get('line') in lines_dict.keys():
            #   aggiorniamo il valore
            lines_dict[ elem.get('line') ] = lines_dict[elem.get('line')] + 1
        else:
            lines_dict[ elem.get('line') ] = 1


    elapsed_time = time.process_time() - t
    print("Tempo di esecuzione: ",elapsed_time)
    print("Numero warning: ",len(errors))
    print(lines_dict.keys())
    print(lines_dict.values())






if __name__ == "__main__":

    #   Pandas
    print("Caricamento documento pandas")
    pmd_data =test_pandas("/media/stefano/LinuxDiskLock/pmd-dataset/pmd-apache-projects-commits/activemq-artemis/0a47e1bc6fee2474e45acd8b8a7ca366e4e724bf/pmd-0a47e1bc6fee2474e45acd8b8a7ca366e4e724bf.csv")

    print("\nRicerca in dataframe:")
    test_pandas_search(pmd_data)

    print("\nCaricamento xml_dom:")
    checkstyle_xml = test_xml_dom("/media/stefano/LinuxDiskLock/checkstyle-apache-projects-commits/activemq-artemis/0a2e143de50ec6506b6bcce6fe9427cd2fbf9f4c/checkstyle-JMXAccessControlList.xml")
    
    print("\nRicerca xml_dom:")
    xml_dom_search(checkstyle_xml)

    print("\nCaricamento xml_tree:")
    checkstyle_xml = test_xml_etree("/media/stefano/LinuxDiskLock/checkstyle-apache-projects-commits/activemq-artemis/0a2e143de50ec6506b6bcce6fe9427cd2fbf9f4c/checkstyle-JMXAccessControlList.xml")
    
    print("\nRicerca xml_tree:")
    xml_tree_search(checkstyle_xml)