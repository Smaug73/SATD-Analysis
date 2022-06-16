#!/usr/bin/env python3
#SBATCH --partition=mcs.default.q
#SBATCH --output=collision_%j.out

from pydriller import Repository
import argparse
import os
import pandas as pd
import string
import sys

sys.path.append(os.getcwd())
from pydriller_method_metrics import calc_metrics_file

#TODO vedi come devi prendere bene il body di una classe, perchè nei commenti ci può essere una { aperta
def trace(directory, projects):
    csv_trace = pd.DataFrame(columns=['Project', 'Commit', 'Old path', 'New path', 'Git_detected'])
    
    for project in projects:
        csv_pydriller_metrics = pd.DataFrame(columns=['Project', 'Commit', 'File', 'Method', 'Start', 'End', 'Parameters', 'Num_Parameters', 'NLOC', 'Complexity'])

        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + os.sep + project))[1]

        print('\nProject: ' + project + ' with ' + str(len(commits)) + ' commits')


        for commit in Repository(repository, only_commits=commits).traverse_commits():
        #for commit in Repository(repository, single='23e8edd9791b5a2ac025c321f97a9dd2329bbeaa').traverse_commits():    
            for modified_file in commit.modified_files:
                if modified_file.filename.endswith('.java') and not(modified_file.filename == 'package-info.java' or modified_file.filename == 'module-info.java'): 
                    if modified_file.change_type.name == 'RENAME':
                        #print('\nCommit: ' + commit.hash)
                        #print(modified_file.diff_parsed)
                        #print('File Renamed!')
                        #print('Old path: ' + modified_file.old_path)
                        #print('New path: ' + modified_file.new_path)
                        new_row = pd.DataFrame({'Project': [project], 'Commit': [commit.hash], 'Old path': [modified_file.old_path], 'New path': [modified_file.new_path], 'Git_detected':[1]})
                        csv_trace = pd.concat([csv_trace, new_row], ignore_index=True, sort=False)
                        csv_trace.to_csv(directory + os.sep + 'trace_files_' + project + '.csv', index=False)
                    elif modified_file.change_type.name == 'ADD' or modified_file.change_type.name == 'MODIFY': 
                        csv_pydriller_metrics = calc_metrics_file(directory, project, commit.hash, modified_file, csv_pydriller_metrics, modified_file.change_type.name)
                        csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_' + project + '.csv', index=False)




def isCodeEqual(sourceCode1, sourceCode2):
    #remove = string.whitespace
    sourceCode1 = sourceCode1.split('{', 1)[1]
    sourceCode2 = sourceCode2.split('{', 1)[1]
    #print('Comparing: \n\n' + sourceCode1.translate({ord(c): None for c in string.whitespace}) + '\n\nand\n\n' + sourceCode2)
    return sourceCode1.translate({ord(c): None for c in string.whitespace}) == sourceCode2.translate({ord(c): None for c in string.whitespace})



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for tracing renamed files')

    # Directory of projects being analysed
    parser.add_argument(
        'directory_projects',
        type=str,
        help='Projects directory',
    )

    parser.add_argument(
        '-p',
        '--projects_to_analyse',
        type=str,
        nargs='+',
        help='Projects to analyse',
        required=True
    )


    # Parsing the args
    args = parser.parse_args()

    # Projects Directory
    pathProjects = args.directory_projects

    projects = args.projects_to_analyse
    
    trace(pathProjects, projects)