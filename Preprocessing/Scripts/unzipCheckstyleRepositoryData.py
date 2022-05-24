# Script for unzip only a group of repository data from zipped checkstyle dataset
# Used for cluster memory issue 
# Use this script like a module for the other script

import re
import zipfile
import shutil


# control that repository name is a directory name and fix
def controlDirName(repository_name):
    if not str(repository_name).endswith('/'):
        return str(repository_name)+'/'
    else:
        return str(repository_name)


# function for unzip all the file of a specific repository
# repository_name is name of the directory of the repository. Example :  arie/ 
def unzipRepo(zipped_file,repository_name,path_to_extract):
    
    zip_ref= zipfile.ZipFile(zipped_file, 'r') 
    
    repository_name = controlDirName(repository_name)

    #print table of content of the zip file
    for member in zip_ref.filelist:
        # only unzip filename with repository dir file name
        if(repository_name in member.filename):
            print("Unzipping:  "+member.filename)
            with zipfile.ZipFile(zipped_file, 'r') as zip_ref:
                zip_ref.extract(member.filename,path_to_extract)





# Function for remove all data of specific repository
def removeRepoData(repository_data_path):

    print("Removing repository checkstyle data of :   "+repository_data_path)
    
    #remove the dir and all sub-dir and file 
    shutil.rmtree(repository_data_path, ignore_errors=True)
    
    print("Deleted '%s' directory successfully" % repository_data_path)


# Function for gzip files of our processing
#   TO DO!!!!

# TEST
if __name__ == "__main__":

    #Unzip only the repository data we need
    zipped_file= '/media/stefano/1a583e86-0a0c-43b2-946f-ea87c552565a/dataset_tesi_magistrale/[dataset]SATD-Repair/Android_Projects/pmd-apache-projects-commits.zip'
    repository_name = 'aries'
    path_to_extract = '/media/stefano/1a583e86-0a0c-43b2-946f-ea87c552565a/dataset_tesi_magistrale/[dataset]SATD-Repair/Android_Projects/'


    #unzipRepo(zipped_file,repository_name,path_to_extract)
    removeRepoData(path_to_extract+repository_name)




