# Example and alpha version of script for process checkstyle and pmd analysis
# TO DO: check the configuration file of checkstyle in felipe repository



import os
import subprocess as subprocess


# Launch Checkstyle
def checkstyle_call():
    # directory of the CheckStyle output
    dir_checkstyle = '/home/stefano/TesiMagistrale/ProvePydriller/Checkstyle/'

    commit_id = "0a1b46ce0d436002e8abf9ae74a7ba7324fe093e"

    project = "tinkerpop"

    # the local dir where the java files are located
    dir_local_path = "/home/stefano/TesiMagistrale/ProvePydriller/"+project+"/"


    #### MakeDir for the analysis in the CheckStyle directory #######
    #### ...SATD_Analysis/Checkstyle/repository/*allrepository/*allcommits

    dir_checkstyle_rep = dir_checkstyle+'repository'
    # create the project directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_checkstyle_rep) is False:
        os.mkdir(dir_checkstyle_rep)

    dir_project_output= dir_checkstyle+'repository'+ os.sep +project

    # create the project directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_project_output) is False:
        os.mkdir(dir_project_output)

    dir_project_commit_output= dir_project_output+ '/'+commit_id

    # create the commitID directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_project_commit_output) is False:
        os.mkdir(dir_project_commit_output)

    #######################



    print('Started creating call for ' + project)

    # java -jar checkstyle-8.36-all.jar -c checkstyle-all-checks_v8.36.xml -f xml -o

    #   FIX DA FARE : il file di configurazione va indicato in quale cartella si trova
    checkstyle = 'java -jar '+dir_checkstyle+'checkstyle-10.2-all.jar -c google_checkstyle_configuration.xml -f xml -o '

    
    # iterate over the project comments and save call string
    for root, dirs, files in os.walk(dir_local_path, topdown=False):

        # iterate over the files of the commit
        for file in files:

            # just proceed if it is a Java file
            if '.java' in file:

                path = dir_local_path

                output = dir_project_commit_output + os.sep +'checkstyle-' + file.replace('java', '') + 'xml'

                folder = path + commit_id + os.sep + file

                call = checkstyle + output + ' ' + folder
            
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

    print('\nDone with project ' + project)





# Launch PMD
def pmd_call():

    # directory of the CheckStyle output
    dir_pmd = '/home/stefano/TesiMagistrale/ProvePydriller/PMD/'

    commit_id = "0a1b46ce0d436002e8abf9ae74a7ba7324fe093e"

    project = "tinkerpop"

    # the local dir where the java files are located
    dir_local_path = "/home/stefano/TesiMagistrale/ProvePydriller/"+project+"/"


    #### MakeDir for the analysis in the PMD directory #######
    #### ...SATD_Analysis/PMD/repository/*allrepository/*allcommits

    dir_pmd_rep = dir_pmd+'repository'
    # create the project directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_pmd_rep) is False:
        os.mkdir(dir_pmd_rep)

    dir_project_output= dir_pmd_rep+ os.sep +project

    # create the project directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_project_output) is False:
        os.mkdir(dir_project_output)

    dir_project_commit_output= dir_project_output+ '/'+commit_id

    # create the commitID directory if it does not exist, otherwise skit it
    if os.path.isdir(dir_project_commit_output) is False:
        os.mkdir(dir_project_commit_output)

    #######################

    # iterate over the project comments and save call string
    for root, dirs, files in os.walk(dir_local_path, topdown=False):

        # iterate over the files of the commit
        for file in files:

             # just proceed if it is a Java file
            if '.java' in file:

                path = dir_local_path

                output = dir_project_commit_output + os.sep +'pmd-' + file.replace('java', '') + 'csv'

                folder = path + commit_id + os.sep + file

                #call = dir_pmd+'pmd-bin-6.45.0/bin/run.sh pmd -d '+ folder + ' -R rulesets/java/quickstart.xml -f csv --no-cache > ' + output
                call = dir_pmd+'pmd-bin-6.50.0/bin/run.sh pmd -d '+ folder + ' -R rulesets/java/quickstart.xml -f csv --no-cache'


                # lanch PMD for the specific file
                try:
                    print()
                    print('Launch PMD: '+call)
                    command= call
                    #p=subprocess.Popen(command.split(),stdout=subprocess.PIPE)
                    p=subprocess.Popen(command.split(),stdout=open(output,'w'))
                    p.wait()
                    print('Done.. ')
                except Exception:
                    print("Errore lancio {}".format(command))
                    print(Exception)





if __name__ == "__main__":

    #checkstyle_call()
    pmd_call()