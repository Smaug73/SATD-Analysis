# Script for download mbox files of a specific apache project
from enum import Flag
import os
from re import sub
import requests
import datetime
import argparse
import subprocess as subprocess
import git
import time
from datetime import datetime as dateTime

#   TO DO:
#   - La data di inizio da considerare deve essere rintracciata dal primo commit del progetto 



# function for mkdir for store the file
# parameter :   project  : string name of the project
def mkdir_for_mbox(project : str , dir_mbox = '..' + os.sep + 'mboxFile'):
    
    print(f"Creating dir for Project : {str(project)} ")

    try:
    
        # directory for mbox file of projects
        # dir_mbox = '..' + os.sep + 'mboxFile' 

        # create the directory for mbox if it does not exist, otherwise skip it
        if os.path.isdir(dir_mbox) is False:
            os.mkdir(dir_mbox)
            print(f"Dir mbox create! ")
        else:
            print("Dir mbox already exists .. ")
        
        return dir_mbox
        '''
        # path of mbox file of the proj
        dir_proj = dir_mbox + os.sep + project + os.sep
        
        # create the project directory if it does not exist, otherwise skip it
        
        if os.path.isdir(dir_proj) is False:
            os.mkdir(dir_proj)
            print(f"Dir "+dir_proj+" create! ")
        else:
            print(f"Dir "+dir_proj+" already exists .. ")
        '''
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





# Function for download all email and attach in one mbox file from a specific project
# from a start date to an end date.
# Mounth format : yeardaymounth   2016-05  2016(year)-05(mounth)
# Project name example: tinkertop
def download_mbox_start_end(project : str, start_date_str: str, end_date_str:str , mail_list : str , output_dir = '..' + os.sep + 'mboxFile' ):
    
    try:

        # split the data and convert the value in integer 
        start_date_split = start_date_str.split('-')
        start_date = datetime.date(int(start_date_split[0]), int(start_date_split[1]), 1)

        end_date_split = end_date_str.split('-')
        end_date = datetime.date(int(end_date_split[0]), int(end_date_split[1]), 1)

        temp_date = datetime.date(int(start_date_split[0]), int(start_date_split[1]), 1)

        # create the dir for store the file
        dirpath = mkdir_for_mbox(project, output_dir)


        # check if the mbox file already exist
        print(dirpath)
        list_mbox_file = []
        for mbox in os.scandir(dirpath):
            list_mbox_file.append(mbox.name)
        print("Mbox files:")
        print(list_mbox_file)

        print('Locking for : '+project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox")
        print()
        if str(project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox") in list_mbox_file:
            print("Mbox file already exist! Skipped")
        else:    
            while end_date >= temp_date :
                
                # request the mbox
                #uri = 'https://mail-archives.apache.org/mod_mbox/'+project+'/'+data+'.mbox' NO old API
                uri = 'https://lists.apache.org/api/mbox.lua?list='+mail_list+'@'+project+'.apache.org&d='+str(temp_date.year)+'-'+str(temp_date.month)
                print(uri)
                

                # download the file
                response = requests.get(uri)
        
                # for save the file check if the content of the response is greater than 0 byte
                # the api return a 0 byte response content there are no message for the data passed
                if response.content != b'' and not('Message Not Found!' in response.content.decode("utf-8") ):
                    
                    # open the file and append to the end the content of the response
                    open(dirpath+os.sep+project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox", "a").write(response.content.decode("utf-8"))
                    print('File downloaded and appended: '+dirpath+os.sep+project+".mbox")

                else:
                    print("No data for this mounth: "+str(temp_date.year)+"-"+str(temp_date.month))

                # increment temp_date
                if temp_date.month >= 12:
                    # increment year
                    temp_date = datetime.date( temp_date.year+1, 1, 1)
                else :
                    # increment mounth
                    temp_date = datetime.date(temp_date.year, temp_date.month + 1, 1)
        
        #return dirpath+os.sep+project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox"
        #return os.path.realpath(open(dirpath+os.sep+project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox", "a").name)
        #FIX FOR RELATIVE PATH RETURN
        if not str(output_dir).endswith('/'):
            return output_dir+os.sep+project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox"
        else:
            return output_dir+project+"-from-"+start_date.isoformat()+"-to-"+end_date.isoformat()+".mbox"

    except Exception as e:
        print(e)
        



# Function for find the date of the first commit (not good parameters but ...)
def find_date_first_or_last_commit(repo_path : str , first_or_last : bool):

    try:

        #Repository
        repo = git.Repo(repo_path)

        gitR = repo.git

        if first_or_last:
            # Get the gitlog from the first commit and split
            log_list = str(gitR.log('--reverse')).split('\n')
        else :
            # Get the gitlog from the last commit and split
            log_list = str(gitR.log()).split('\n')


        # Find the date string, this is a more generic solution
        date_s = ''
        i = 0
        while 'Date' not in date_s:
            date_s = log_list[i]
            i = i+1

        # Get the date of the first commit as datetime object
        datetime_object = dateTime.strptime(' '.join(date_s[8:].split(' ')[:-1]), '%a %b %d %H:%M:%S %Y') 

        # String of the date of the first commit
        date_string = str(datetime_object.year) + '-' + str(datetime_object.month) + '-' + str(datetime_object.day)

        return date_string

    except Exception as e:
        print(e)




if __name__ == "__main__":

    # Args : directory of projects
    parser = argparse.ArgumentParser(
    description='Script for download mbox file for an apache project')

    # Apache project name
    parser.add_argument(
        'project_name',
        type=str,
        help='Apache projects name',
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
    parser_a = subparser.add_parser('from_date')
    
    # Start date
    parser_a.add_argument(
        'start_date',
        type=str,
        help='Start date, formate:  YYYY-MM(year-mount)',
    )

    # End date
    parser_a.add_argument(
        'end_date',
        type=str,
        help='End date, formate:  YYYY-MM(year-mount)',
    )


    parser_b = subparser.add_parser('from_git')

    # Local path of the git project
    parser_b.add_argument(
        'path',
        type=str,
        help='Local path of the git project',
    )



    # Parsing the args
    args = parser.parse_args()
    print(args)
    if 'start_date' in vars(args) :
        download_mbox_start_end(args.project_name, args.start_date, args.end_date , args.mail_list_name)
    
    if 'path' in vars(args) :
        download_mbox_start_end( args.project_name, find_date_first_or_last_commit(args.path, True), find_date_first_or_last_commit(args.path, False) , args.mail_list_name)
        #print(find_date_first_or_last_commit(args.path, True))
        #print(find_date_first_or_last_commit(args.path, False))



    # TEST ################################# 
    #download_mbox_file_mounth('tinkerpop','2019-05')
    #download_mbox_start_end('activemq','2010-01','2020-12')
    