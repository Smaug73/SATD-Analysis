# Script for download mbox files of a specific apache project
import os
import requests





# function for mkdir for store the file
# parameter :   project  : string name of the project
def mkdir_for_mbox(project : str):
    
    print(f"Creating dir for Project : {str(project)} ")

    try:
    
        # directory for mbox file of projects
        dir_mbox = '..' + os.sep + 'mboxFile' 

        # create the directory for mbox if it does not exist, otherwise skip it
        if os.path.isdir(dir_mbox) is False:
            os.mkdir(dir_mbox)
            print(f"Dir mbox create! ")
        else:
            print("Already exists .. ")

        # path of mbox file of the proj
        dir_proj = dir_mbox + os.sep + project + os.sep
        
        # create the project directory if it does not exist, otherwise skip it
        if os.path.isdir(dir_proj) is False:
            os.mkdir(dir_proj)
            print(f"Dir "+dir_proj+" create! ")
        else:
            print("Already exists .. ")

        # return the dir path where to store the mbox files of the project
        return dir_proj
        
    except Exception as e:
        print(e)




# Function for download mbox file of a specific mounth for a specific apache project
# Mounth format : yeardaymounth   2016-05  2016(year)-05(mounth)
# Project name example: tinkertop  
def download_mbox_file_mounth(project : str, data: str):

    try:

        # uri
        #uri = 'https://mail-archives.apache.org/mod_mbox/'+project+'/'+data+'.mbox' NO old API
        uri = 'https://lists.apache.org/api/mbox.lua?list=dev@'+project+'.apache.org&d='+data

        # create the dir for store the file
        dirpath = mkdir_for_mbox(project)

        # download the file
        response = requests.get(uri)
        
        # for save the file check if the content of the response is greater than 0 byte
        # the api return a 0 byte response content there are no message for the data passed
        if response.content != 0 and not('Message Not Found!' in response.content.decode("utf-8") ):
            open(dirpath+project+'-'+data+".mbox", "wb").write(response.content)
            print('File downloaded: '+dirpath+project+'-'+data+".mbox")
        else:
            print('No data for this mounth')

    except Exception as e:
        print(e)




if __name__ == "__main__":


    # TEST ################################# 
    download_mbox_file_mounth('tinkerpop','2019-05')