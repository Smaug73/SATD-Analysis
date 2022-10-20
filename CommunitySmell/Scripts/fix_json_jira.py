from asyncore import write
import os

file = open('/home/stefano/SATD-Analysis/CommunitySmell/kaiaulu/jiraIssues/solr_issues-merged.json','r')
n_file = open('/home/stefano/SATD-Analysis/CommunitySmell/kaiaulu/jiraIssues/FIXED-solr_issues-merged.json','a')
lines = file.readlines()

for l in lines:
    n_file.write(l)
    n_file.write(',\n')

file.close()
n_file.close()

print('End !')

'''
#   leggiamo carattere per carattere fino ad incontrare } 
#   inseriamo una , successivamente se non c'e' gia'
while 1:
    char = file.read(1)
    
    if not char:
        break
    
    if char == '}' :
        # controlliamo il prossimo carattere per verificare se non sia una virgola
        n_char = file.read(1)
        
        if n_char != ',' and n_char != ']':
            # inseriamo la virgola
            file.seek()
'''