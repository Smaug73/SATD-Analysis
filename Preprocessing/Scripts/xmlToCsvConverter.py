from genericpath import isdir
from xml.dom import minidom
import pandas as pd
import argparse
import os

# Function for explore dataset
def convert_all_files(directory):
     # Get the name of each project in the directory
    projects = next(os.walk(directory))[1]

    for project in projects:

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + os.sep + project))[1]

        for commit in commits:
            print('Commit: ' + commit)
            checkstyle_csv = pd.DataFrame(columns=['File', 'Line', 'Severity', 'Message', 'Source'])
            filepath_csv = directory + os.sep + project + os.sep + commit + os.sep + 'checkstyle-' + commit + '.csv'

            filepaths = []
            filepath = directory + os.sep + project + os.sep + commit + os.sep + 'checkstyle-' + commit + '.xml'
            if os.path.isfile(filepath):
                filepaths.append(filepath)
            else:
                classes = next(os.walk(directory + os.sep + project + os.sep + commit))[2]
                for cl in classes:
                    if cl.endswith('.xml'):
                        filepaths.append(directory + os.sep + project + os.sep + commit + os.sep + cl)
            
            convert_file(filepaths, checkstyle_csv, filepath_csv)    


# Function for convert xml to csv
def convert_file(filepaths, checkstyle_csv, filepath_csv):
    
    for filepath in filepaths:
        # Parse an xml file by name
        file_xml = minidom.parse(filepath)

        # Parse all file elements
        files = file_xml.getElementsByTagName('file')

        for file in files:
            print("\nFile name: " + file.getAttribute('name'))

            # Parse the errors of a file
            errors = file.getElementsByTagName('error')
            
            # Create a new row and append it to the DataFrame
            for error in errors:
                new_row = pd.DataFrame({'File': [file.getAttribute('name')], 'Line': [error.getAttribute('line')], 
                                        'Severity':[error.getAttribute('severity')], 'Message': [error.getAttribute('message')], 
                                        'Source': [error.getAttribute('source')]})
                checkstyle_csv = pd.concat([checkstyle_csv, new_row], ignore_index=True, sort=False)
                checkstyle_csv.to_csv(filepath_csv, index=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for converting xml file from checkstyle analysis to csv')

    # Directory of projects being analysed
    parser.add_argument(
        'directory_projects',
        type=str,
        help='Projects directory',
    )

    # Parsing the args
    args = parser.parse_args()

    # Projects Directory
    pathProjects = args.directory_projects
    
    convert_all_files(pathProjects)
    
    

