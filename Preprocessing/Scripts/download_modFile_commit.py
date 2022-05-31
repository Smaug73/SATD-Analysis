import os
from pdb import main
import re
from pydriller import Repository
from pydriller import ModifiedFile


# dir for store projects fix
dir_repo_fix = ".."+os.sep+".."+os.sep+"Repository-fix"+os.sep



# function for mkdir for store the file
def mkdir_for_fix(project,commit_id):
    

    try:
    
        # directory for the commit
        dir_commit = dir_repo_fix + project + os.sep + commit_id

        # create the fix projects directory if it does not exist, otherwise skip it
        if os.path.isdir(dir_repo_fix) is False:
            os.mkdir(dir_repo_fix)

        # create the project directory if it does not exist, otherwise skip it
        if os.path.isdir(dir_repo_fix + project) is False:
            print(f"\nCreating directory for project: {str(project)} ")
            os.mkdir(dir_repo_fix + project)

        # create the commitID directory if it does not exist, otherwise skip it
        if os.path.isdir(dir_commit) is False:
            print(f"\nCreating directory for commit: {str(commit_id)} in project: {str(project)} ")
            os.mkdir(dir_commit)
        # else:
        #     # print('No need to save files from commit: ' + commit_id)
        #     continue

        #return the path where store the files to fix for the commit of the project
        return dir_commit
        
    except Exception as e:
        print(e)






# Function for download specific file from a commit
def download_file_from_commit(project : str ,commit_id : str ,file_name : str):

    print('Download the file for the fix')
    
    try:
        repository = 'https://github.com/apache/' + project

        print('Commit:  '+ commit_id)

        # create the git rep object
        git_rep = Repository(repository, single=commit_id).traverse_commits()


        for commit in git_rep:

            # iterate over each modified file within the commit
            for m in commit.modified_files:
                
                if(m.filename == file_name):
                    download_Modifiedfile(m,project,commit)

    except Exception as e:
        print(e)




# Function for download file from ModifiedFile
def download_Modifiedfile(mod_file : ModifiedFile,project : str ,commit: str):
    
    print(f'Downloading file:  {mod_file.new_path} ...')

    try:
        # mkdir for store the file
        dir_commit = mkdir_for_fix(project,commit)

        # Check if the file were already downloaded
        if mod_file.filename in os.listdir(dir_commit):
            return

        #print('File found:  ', mod_file.new_path)
        # print(modified_file.source_code)

        # save the file
        if mod_file.source_code is not None:

            # Rename the file with the path because of the possible re-writing of file with same name 
            file = open(dir_commit + os.sep + mod_file.new_path.replace('/','#'), "w", encoding="utf-8")

            file.write(mod_file.source_code)
            file.close()

            #print(f'File:  {mod_file.filename}    Downloaded! ')
            print(f'{mod_file.new_path}  DOWNLOADED! ')
        
        else:
            print(f'{mod_file.new_path}    NOT DOWNLOADED! ')
    
    except Exception as e:
        print(e)



    


if __name__ == "__main__":


    # TEST download_Modifiedfile ################################# 
    
    commit_id = "0a1b46ce0d436002e8abf9ae74a7ba7324fe093e"
    project = "tinkerpop"


    repository = 'https://github.com/apache/' + project

    # create the git rep object
    git_rep = Repository(repository, single=commit_id).traverse_commits()

    for commit in git_rep:

        # iterate over each modified file within the commit
        for m in commit.modified_files:
            
            # test for all the file of the commit
            download_Modifiedfile(m,project,commit.hash)

    #################################