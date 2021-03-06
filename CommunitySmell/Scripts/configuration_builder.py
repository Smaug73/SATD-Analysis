'''

Script for the create the configuration file needed by the 
community smell script from kaiaulu.
Only the information necessary for community smell computing is 
insert in the file.

IMPORTANT:  The download of the jira issues are not included,
            check the directory where store it after download 
            in the configuration file created by the script

Information needed for the configuration file:
    
    apache project name
    git repository path
    git branch (only main/master branch is considered)
    
    start date
    end date
    window size
    
    conf file path
    
    jira issue comments path


'''

#TO DO :
#   UTILIZZARE PATH RELATIVI AL POSTO DI QUELLI ASSOLUTI !!
#   In questo modo i configuration file e tutto il dataset è portabile
#   I repository allora devono avere una precisa posizione all'interno del progetto per questioni di portabilità del dataset
# 
#   FIXARE IL PARAMETRO LIST-KEY per quanto riguarda le mail list, poichè è per la maggior parte solo dev (controllare come questo parametro viene utilizzato)
#   FARE ATTENZIONE: Controllare i file mbox troppo piccoli rispetto al periodo di sviluppo considerato, potrebbero utilizzare una mail list differente
#
#   mail list con problemi:  log4j  non si capisce quale mail list bisogna utilizzare, 
#                                   potrebbe essere meglio evitare evitare di utilizzare le mail in questo caso
#                                   poichè non si capisce quale 


import argparse
import subprocess as subprocess
import os
import git
from git import Repo
from numpy import size
from download_mbox_apacheproject import find_date_first_or_last_commit
from download_mbox_apacheproject import download_mbox_start_end



# function for mkdir for store the file
# parameter :   project  : string name of the project
def mkdir_for_confFile(kaiaulu_path : str):
    
    print(f"Creating conf dir in : {str(kaiaulu_path)} ")

    try:
    
        # directory for conf file of projects
        if kaiaulu_path.endswith(os.sep):
            dir_conf = kaiaulu_path + 'conf'
        else:
            dir_conf = kaiaulu_path + os.sep + 'conf' 

        # create the directory for conf if it does not exist, otherwise skip it
        if os.path.isdir(dir_conf) is False:
            os.mkdir(dir_conf)
            print(f"Dir conf create! ")
        else:
            print("Dir conf already exists .. ")

        # return the dir path where to store the conf files of the project
        return dir_conf
        
    except Exception as e:
        print(e)




# Function for create the configuration file for an apache project
def configuration_file_builder(kaiaulu_path : str , project_name : str, mbox_file_path : str , start_date : str, end_date : str, size_days : str , jira_path : str , git_repo_path : str):
    
    try:
        print(f"Creating conf file for : {str(project_name)} ...")

        start_date = start_date+ " 00:00:00"
        end_date = end_date+ " 00:00:00"

        # check witch is the default branch 
        repo = Repo(git_repo_path)
        head = repo.heads[0]
        main_branch_name = head.name


        configuration = str("project :\n"+
                        "  website : https://"+project_name+".apache.org\n"+
                        "  openhub : https://www.openhub.net/p/"+project_name+"\n"+
                        "version_control:\n"+
                        "  log: "+git_repo_path+"/.git\n"+
                        "  log_url: https://github.com/apache/"+project_name+"\n"+
                        "  branch:\n"+
                        "    - "+main_branch_name+"\n"+
                        "mailing_list:\n"+
                        "  mbox: "+mbox_file_path+"\n"+
                        "  domain: http://mail-archives.apache.org/mod_mbox\n"+
                        "  list_key:\n"+
                        "    - "+project_name+"-dev\n"+
                        "issue_tracker:\n"+
                        "  jira:\n"+    
                        "    domain: https://issues.apache.org/jira\n"+
                        "    project_key: "+str(project_name).upper()+"\n"+
                        "    issues: "+jira_path+project_name+"_issues-merged.json\n"+
                        "    issue_comments: "+jira_path+project_name+"_issues-merged.json\n"+
                        "  github:\n"+
                        "    owner: apache\n"+
                        "    repo: "+project_name+"\n"+
                        #"    replies: ../rawdata/git_repo/"+project_name+"/\n"+
                        "commit_message_id_regex:\n"
                        "    issue_id: \#[0-9]+\n"
                        #cve_id: ?

                        "filter:\n"
                        "  keep_filepaths_ending_with:\n"+
                        "    - cpp\n"+
                        "    - c\n"+
                        "    - h\n"+
                        "    - java\n"+
                        "    - js\n"+
                        "    - py\n"+
                        "    - cc\n"+
                        "  remove_filepaths_containing:\n"+
                        "    - test\n"+
                        "analysis:\n"+
                        "  window:\n"+
                        "    start_datetime: "+start_date+"\n"+
                        "    end_datetime: "+end_date+"\n"+
                        "    size_days: "+size_days+"\n"     
                        )

        
        

        if kaiaulu_path.endswith('/'):
            conf_file_path = kaiaulu_path + project_name + ".yml"
        else:
            conf_file_path = kaiaulu_path + os.sep + project_name + ".yml"

        with open(conf_file_path, 'w') as file:
        #with open(kaiaulu_path + os.sep + project_name + ".yml", 'w') as file:
            conf_file = file.write(configuration)

        print(f"Complete !")

    except Exception as e:
        print(e)
        print('ERRORE configuration file non creato!')






# Function for clone a repository
def clone_repo(project_name : str, git_repo_path : str):

    print("Cloning repository "+project_name+" ...")

    # clone only if the project doesn't exist, otherwise skip it
    if os.path.isdir(git_repo_path) is False:
        
        git.Repo.clone_from("https://github.com/apache/"+project_name, git_repo_path)
    
        print("Repository "+project_name+" cloned!")

    else:
        print("Repository "+project_name+" already exists ! ") 

    





if __name__ == "__main__":
    
    # Args : 
    #   project_name
    #   kaiaulu_path
    #   start_date
    #   end_date

    parser = argparse.ArgumentParser(
    description='Script for create kaiaulu configuration file for compute community smells for an Apache project.')

    # Kaiaulu path
    parser.add_argument(
        'kaiaulu_path',
        type=str,
        help='Kaiaulu path',
    )

    # Jira issues path
    parser.add_argument(
        'jira_path',
        type=str,
        help='Path to dir that containing all the jira issues for all project',
    )

    # Mail list name
    parser.add_argument(
        '-ml',
        '--mail_list_name',
        type=str,
        default= 'dev',
        required= False,
        help='Mail list name, default value : dev',
    )

    subparser = parser.add_subparsers()
    
    parser_from_date = subparser.add_parser('from_date' , description='Download a repo and using a starting date and an end date for conf')

    # Apache project name
    parser_from_date.add_argument(
        'project_name',
        type=str,
        help='Apache projects name',
    )

    # Start date
    parser_from_date.add_argument(
        'start_date',
        type=str,
        help='Start date of the consider period, formate:  YYYY-MM-DAY(year-mount-Day)',
    )

    # End date
    parser_from_date.add_argument(
        'end_date',
        type=str,
        help='End date of the consider period, formate : YYYY-MM-DAY(year-mount-Day)',
    )

    # For parse projects from a directory that contain all the projects
    parser_from_dir = subparser.add_parser('projects_dir')

    # Path of dir containing all projects
    parser_from_dir.add_argument(
        'dir_path',
        type=str,
        help='Path of dir containing all projects',
    )


    args = parser.parse_args()


    # Create dir for configuration file
    conf_path = mkdir_for_confFile(args.kaiaulu_path)

    # Clone the repo if the clone flag is True         ########################################
    if 'project_name' in vars(args) :
        
        # Repo path used is the preconfigured repo path used by kaiaulu
        repo_path = args.kaiaulu_path+"rawdata"+os.sep+"git_repo"+os.sep+args.project_name

        # Clone the repository of the project
        clone_repo(args.project_name, repo_path)

        # Start and End date
        start_date = find_date_first_or_last_commit(repo_path, True)
        end_date = find_date_first_or_last_commit(repo_path, False)

        # Download all the mail list
        mbox_path = download_mbox_start_end( args.project_name, start_date, end_date)

        # Create the configuration file
        configuration_file_builder(conf_path , args.project_name , mbox_path,
                                    start_date , end_date , str(90) , args.jira_path , repo_path)
    

    # If already have all the repositories in a dir #########################################
    if 'dir_path' in vars(args):

        # list of the names of the all projects
        list_repo_name = {}
        
        for rep in os.scandir(args.dir_path):
            
            if rep.is_dir():
                list_repo_name[rep.name] = rep
                #list_repo_name.append(rep)

        #list of the names of the project to skip and remove from the list
        for f in os.scandir(args.kaiaulu_path+'conf'):
            size = len(f.name)
            if f.name.endswith('.yml') and list_repo_name.get(f.name[:size-4]) != None:
                #list_repo_name.remove(f.name[:size-4])
                list_repo_name.pop(f.name[:size-4])
                print('Skip : '+f.name)

        # debug 
        print('Repositories : ')
        for rep in list_repo_name.keys():
            print(list_repo_name.get(rep))
        print()
        
        # Download the mbox file for all the repos
        for repK in list_repo_name.keys():

            rep = list_repo_name.get(repK)

            print("Download mbox files for : "+rep.name)
            
            # Start and End date
            start_date = find_date_first_or_last_commit(rep.path, True)
            end_date = find_date_first_or_last_commit(rep.path, False)

            # Download all the mail list
            mbox_path = download_mbox_start_end( rep.name , start_date, end_date , args.mail_list_name)
            
            # Create the configuration file
            configuration_file_builder(conf_path , rep.name , mbox_path,
                                    start_date , end_date , str(90) ,  args.jira_path , rep.path)

        