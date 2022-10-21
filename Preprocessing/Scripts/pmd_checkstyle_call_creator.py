# Example and alpha version of script for process checkstyle and pmd analysis
# TO DO: check the configuration file of checkstyle in felipe repository



from genericpath import isdir
import os
import subprocess as subprocess



# directory of the PMD output
dir_pmd = '../pmd-bin-6.50.0/'
# directory of the CheckStyle output
dir_checkstyle = '../checkstyle/'





# Launch Checkstyle
def checkstyle_call(file_path,output_path):

    # java -jar checkstyle-8.36-all.jar -c checkstyle-all-checks_v8.36.xml -f xml -o

    #   FIX DA FARE : il file di configurazione va indicato in quale cartella si trova
    checkstyle = 'java -jar '+dir_checkstyle+'checkstyle-10.2-all.jar -c '+dir_checkstyle+'google_checkstyle_configuration.xml -f xml -o '

    output_path = output_path.replace('java', '') + 'xml'

    call = checkstyle + output_path + ' ' + file_path

    # lanch checkstyle for the specific file
    try:
        print()
        print('Launch Checkstyle: '+call)
        command= call
        p=subprocess.Popen(command.split(),stdout=subprocess.PIPE)
        p.wait()
        print('Done.. ')
    except Exception:
        print("Errore lancio {}".format(command))
        print(Exception)






# Launch PMD
def pmd_call(file_path,output_path):

    output_path = output_path.replace('java', '') + 'csv'

    #call = dir_pmd+'pmd-bin-6.45.0/bin/run.sh pmd -d '+ folder + ' -R rulesets/java/quickstart.xml -f csv --no-cache > ' + output
    call = dir_pmd+'pmd-bin-6.50.0/bin/run.sh pmd -d '+ file_path + ' -R rulesets/java/quickstart.xml -f csv --no-cache ' 

    # lanch PMD for the specific file
    try:
        print()
        print('Launch PMD: '+call)
        command= call
        #p=subprocess.Popen(command.split(),stdout=subprocess.PIPE)
        p=subprocess.Popen(command.split(),stdout=open(output_path,'w'))
        p.wait()
        print('Done.. ')
    except Exception:
        print("Errore lancio {}".format(command))
        print(Exception)





#   Funzione per scorrere tutti i file da analizzare
def read_rep(reps_path):

    #   ogni repository ha una cartella il cui nome è il commit_id di riferimento

    
    #   Creiamo cartelle di output per le analisi di checkstyle e pmd   ############
    
    dir_pmd_rep = dir_pmd+'repository'

    # create the project directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_pmd_rep) is False:
        os.mkdir(dir_pmd_rep)
    
    dir_checkstyle_rep = dir_checkstyle+'repository'+os.sep
    # create the project directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_checkstyle_rep) is False:
        os.mkdir(dir_checkstyle_rep)

    ################################################################################


    #   scorriamo tutti i repository
    for repo in os.listdir(reps_path):
    
        if os.path.isdir(reps_path+repo):
            # per ogni repository creiamo cartella di output dei risultati
            dir_pmd_output= dir_pmd_rep+ os.sep + repo
            
            #   create the project directory if it does not exist, otherwise skit it
            if os.path.isdir(dir_pmd_output) is False:
                os.mkdir(dir_pmd_output)


            dir_checkstyle_output= dir_checkstyle_rep + os.sep + repo

            #   create the project directory if it does not exist, otherwise skit it
            if os.path.isdir(dir_checkstyle_output) is False:
                os.mkdir(dir_checkstyle_output)

            

            #   per ogni commit di una repo creiamo output dir
            for commit in os.listdir(reps_path+repo):
                
                if os.path.isdir(reps_path+repo+os.sep+commit):

                    commit_checkstyle_output = dir_checkstyle_output + os.sep + commit

                    #   create the project directory if it does not exist, otherwise skit it
                    if os.path.isdir(commit_checkstyle_output) is False:
                        os.mkdir(commit_checkstyle_output)

                    commit_pmd_output = dir_pmd_output + os.sep + commit
                    
                    #   create the project directory if it does not exist, otherwise skit it
                    if os.path.isdir(commit_pmd_output) is False:
                        os.mkdir(commit_pmd_output)


                    # per ogni file nel commit eseguiamo analisi pmd e checkstyle
                    for file in os.listdir(reps_path+repo+os.sep+commit):

                        file_path = reps_path+repo+os.sep+commit+os.sep+file
                        
                        if(os.path.isfile(file_path) and '.java' in file) :
                            
                            print('Analysis for : '+file_path)

                            #launch pmd 
                            #pmd_call(file_path , commit_pmd_output+os.sep+file)
                            
                            #launch checkstyle
                            #checkstyle_call(file_path , commit_pmd_output+os.sep+file)

                            print()




if __name__ == "__main__":


    read_rep('../Repository-fix/')
    #checkstyle_call()
    #pmd_call()