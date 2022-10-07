'''

Take all the conf file in a dir and fix the data.

'''
import os
import yaml


def fix_date_string(date):

    fixlist=date.split(" ")
    fixlist[0] = fixlist[0]+"-1"
    
    return fixlist[0]+" "+fixlist[1]



conf_dir="../kaiaulu/conf/"

# List all the conf file in the dir        
for rep in os.scandir(conf_dir):

    # Check if the file is a yml
    if rep.is_file and rep.name.endswith(".yml"):
        
        try:
            #Open the file and fix the data
            file=open(rep.path,'r')
                
            #print(file.read())
            
            conf_file= yaml.safe_load(file)
            #print(rep.path)
            
            start_date = conf_file["analysis"]["window"]["start_datetime"]
            end_date = conf_file["analysis"]["window"]["end_datetime"]
            print("1")
            conf_file["analysis"]["window"]["start_datetime"] = fix_date_string(start_date)
            conf_file["analysis"]["window"]["end_datetime"] = fix_date_string(end_date)
            print("2")
            print(conf_file)

            file.close()
            
            if(conf_file)
            # save file
            subs_file = open(rep.path,'w')
            #yaml.dump(conf_file,rep.path)
            print("3")

        except Exception as e:
            print("Oops!", e.__class__, "occurred for  ", rep.path,"  .")
            print("Next entry.")
            print()

            exit()
