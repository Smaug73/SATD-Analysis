'''

Script for the create the configuration file needed by the 
community smell script from kaiaulu.
Only the information necessary for community smell computing is 
insert in the file.

Information needed:
    
    apache project name
    git repository path
    git branch (only main/master branch is considered)
        *controllare se c'e' un master branch o il main branch*
    
    start commit
    end commit
    window size
    
    conf file path
    
    jira issue comments path


'''



import yaml
import argparse
import subprocess as subprocess
import os
import git




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
def configuration_file_builder(kaiaulu_path : str, project_name : str):
    
    try:

        # check witch is the default branch 

        dict_file = str("project :\n"+
                        "  website : https://"+project_name+".apache.org\n"+
                        "  openhub : https://www.openhub.net/p/"+project_name+"\n"+
                        "version_control:\n"+
                        "  log: ../rawdata/git_repo/"+project_name+"/.git\n"+
                        "  log_url: https://github.com/apache/"+project_name+"\n"+
                        "  branch:\n"+
                        "    ")
                    

        with open(kaiaulu_path + os.sep + project_name, 'w') as file:
            conf_file = yaml.dump(dict_file, file)


    except Exception as e:
        print(e)



# Function for clone a repository
def clone_repo(project_name : str, git_repo_path : str):
    git.Repo.clone_from("https://github.com/apache/"+project_name, git_repo_path)






if __name__ == "__main__":
    
    # Args : 
    #   project_name
    #   kaiaulu_path
    #   
    parser = argparse.ArgumentParser(
    description='Script for create kaiaulu configuration file for an apache project')

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

    args = parser.parse_args()


    # Clone the repository of the project
    clone_repo(args.project_name, args.kaiaulu_path)


    # Create dir for configuration file
    conf_path=mkdir_for_confFile(args.kaiaulu_path)


    # Create the configuration file
    