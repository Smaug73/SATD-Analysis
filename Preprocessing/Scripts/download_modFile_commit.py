import os
from pdb import main
import re
from pydriller import Repository


# dir for store projects fix
dir_repo_fix = '../../Repository-fix/'



# function for mkdir for store the file
def mkdir_for_fix(project,commit_id):

    print(f"Creating dir for Project : {str(project)}    Commit: {str(commit_id)}")

    # directory for the commit
    dir_commit = dir_repo_fix + project + os.sep + commit_id

    # create the fix projects directory if it does not exist, otherwise skip it
    if os.path.isdir(dir_repo_fix) is False:
        os.mkdir(dir_repo_fix)

    # create the project directory if it does not exist, otherwise skip it
    if os.path.isdir(dir_repo_fix + project) is False:
        os.mkdir(dir_repo_fix + project)

    # create the commitID directory if it does not exist, otherwise skip it
    if os.path.isdir(dir_commit) is False:
        os.mkdir(dir_commit)
    # else:
    #     # print('No need to save files from commit: ' + commit_id)
    #     continue

    #return the path where store the files to fix for the commit of the project
    return dir_commit






# Function for download specific file from a commit
def download_file_from_commit(project,commit_id,file_name):

    print('Download the file for the fix')

    repository = 'https://github.com/apache/' + project

    print('Commit:  '+ commit_id)

    '''
    # directory for the commit
    dir_commit = dir_repo_fix + project + os.sep + commit_id

    # create the project directory if it does not exist, otherwise skip it
    if os.path.isdir(dir_repo_fix + project) is False:
        os.mkdir(dir_repo_fix + project)

    # create the commitID directory if it does not exist, otherwise skip it
    if os.path.isdir(dir_commit) is False:
        os.mkdir(dir_commit)
    # else:
    #     # print('No need to save files from commit: ' + commit_id)
    #     continue

    

    dir_commit = mkdir_for_fix(project,commit_id)

    # Check if the file were already downloaded
    if file_name in os.listdir(dir_commit):
        return
    
    '''

    # create the git rep object
    git_rep = Repository(repository, single=commit_id).traverse_commits()


    for commit in git_rep:

        # iterate over each modified file within the commit
        for m in commit.modified_files:
            
            if(m.filename == file_name):
                download_Modifiedfile(m,project,commit)

            '''
            # only proceed with it is a Java file with the searched name
            # TO DO : DIFFERENT CASE OF MATCH FOR PMD AND CHECKSTYLE
            #if re.search('\\.java$', m.filename, re.IGNORECASE):
            if re.search('\\'+file_name+'.java$', m.filename, re.IGNORECASE):

                print('File found:  ',m.filename)
                # print(modified_file.source_code)

                # save the file
                if m.source_code is not None:

                    file = open(dir_commit + '/' + m.filename, "w", encoding="utf-8")
                    file.write(m.source_code)
                    file.close()
            '''




# Function for download file from ModifiedFile
def download_Modifiedfile(mod_file,project,commit):
    
    print(f'Downloading file:  {mod_file.filename} ...')

    try:
        # mkdir for store the file
        dir_commit = mkdir_for_fix(project,commit)

        # Check if the file were already downloaded
        if mod_file.filename in os.listdir(dir_commit):
            return

        print('File found:  ',mod_file.filename)
        # print(modified_file.source_code)

        # save the file
        if mod_file.source_code is not None:

            # Rename the file with the path because of the possible re-writing of file with same name 
            file = open(dir_commit + '/' + m.new_path.replace('/','#'), "w", encoding="utf-8")

            file.write(mod_file.source_code)
            file.close()

            print(f'File:  {mod_file.filename}    Downloaded! ')
            print(f'FilePath:  {dir_commit + os.sep() + mod_file.filename}    Downloaded! ')
        
        else:
            print(f'File:  {mod_file.filename}    NOT DOWNLOADED! ')
    
    except Exception as e:
        print(e)



    


if __name__ == "__main__":


    # TEST ################################# 
    
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