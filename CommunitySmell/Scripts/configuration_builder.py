'''

Script for the create the configuration file needed by the 
community smell script from kaiaulu.
Only the information necessary for community smell computing is 
insert in the file.

IMPORTANT:  The download of the jira issues are not included,
            check the directory where store it after download 
            in the configuration file created by the script

Information needed:
    
    apache project name
    git repository path
    git branch (only main/master branch is considered)
    
    start commit
    end commit
    window size
    
    conf file path
    
    jira issue comments path


'''

#TO DO :



import argparse
import subprocess as subprocess
import os
import git
from git import Repo
from download_mbox_apacheproject import download_mbox_start_end



# function for mkdir for store the file
# parameter :   project  : string name of the project
def mkdir_for_confFile(kaiaulu_path : str):
    
    print(f"Creating conf dir in : {str(kaiaulu_path)} ")

    try:
    
        # directory for conf file of projects
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
def configuration_file_builder(kaiaulu_path : str, project_name : str, mbox_file_path : str , start_date : str, end_date : str, size_days : str):
    
    try:
        print(f"Creating conf file for : {str(project_name)} ...")

        start_date = start_date+ " 00:00:00"
        end_date = end_date+ " 00:00:00"

        # check witch is the default branch 
        repo = Repo(args.kaiaulu_path+os.sep+"rawdata"+os.sep+"git_repo"+os.sep+project_name+os.sep)
        head = repo.heads[0]
        main_branch_name = head.name
        
        
        configuration = str("project :\n"+
                        "  website : https://"+project_name+".apache.org\n"+
                        "  openhub : https://www.openhub.net/p/"+project_name+"\n"+
                        "version_control:\n"+
                        "  log: ../rawdata/git_repo/"+project_name+"/.git\n"+
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
                        "    issues: ../rawdata/issue_tracker/"+project_name+"_issues-merged.json\n"+
                        "    issue_comments: ../rawdata/issue_tracker/"+project_name+"_issues-merged.json\n"+
                        "  github:\n"+
                        "    owner: apache\n"+
                        "    repo: "+project_name+"\n"+
                        #"    replies: ../rawdata/git_repo/"+project_name+"/\n"+
                        "commit_message_id_regex:"
                        "    issue_id: \#[0-9]+"
                        #cve_id: ?

                        "filter:"
                        "keep_filepaths_ending_with:\n"+
                        "    - cpp\n"+
                        "    - c\n"+
                        "    - h\n"+
                        "    - java\n"+
                        "    - js\n"+
                        "    - py\n"+
                        "    - cc\n"+
                        "remove_filepaths_containing:\n"+
                        "    - test\n"+
                        "analysis:\n"+
                        "  window:\n"+
                        "    start_datetime: "+start_date+"\n"+
                        "    end_datetime: "+end_date+"\n"+
                        "    size_days: "+size_days+"\n"     
                        )
                    

        with open(kaiaulu_path + os.sep + project_name + ".yml", 'w') as file:
            conf_file = file.write(configuration)

        print(f"Complete !")

    except Exception as e:
        print(e)






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

    # Apache project name
    parser.add_argument(
        'project_name',
        type=str,
        help='Apache projects name',
    )

    # Kaiaulu path
    parser.add_argument(
        'kaiaulu_path',
        type=str,
        help='Kaiaulu path',
    )

    # Start date
    parser.add_argument(
        'start_date',
        type=str,
        help='Start date of the consider period, formate:  YYYY-MM-DAY(year-mount-Day)',
    )

    # End date
    parser.add_argument(
        'end_date',
        type=str,
        help='End date of the consider period, formate : YYYY-MM-DAY(year-mount-Day)',
    )

    args = parser.parse_args()


    # Clone the repository of the project
    clone_repo(args.project_name, args.kaiaulu_path+"rawdata"+os.sep+"git_repo"+os.sep+args.project_name)

    # Download the mbox file
    mbox_path = download_mbox_start_end(args.project_name, args.start_date, args.end_date, args.kaiaulu_path+"rawdata"+os.sep+"mbox")

    # Create dir for configuration file
    conf_path = mkdir_for_confFile(args.kaiaulu_path)

    # Create the configuration file
    configuration_file_builder(args.kaiaulu_path+"conf"+os.sep , args.project_name , mbox_path,
                                args.start_date , args.end_date , str(90))