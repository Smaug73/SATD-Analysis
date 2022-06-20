#!/usr/bin/env python3
#SBATCH --partition=mcs.default.q
#SBATCH --output=measure_%j.out

from pydriller import Repository
from datetime import datetime
import argparse
import os
import pandas as pd
import sys

sys.path.append(os.getcwd())
from pydriller_method_metrics import calc_metrics_file

def trace_measure(directory, projects):
    csv_trace = pd.DataFrame(columns=['Project', 'Commit', 'Old path', 'New path'])
    
    for project in projects:
        csv_pydriller_metrics = pd.DataFrame(columns=['Project', 'Commit', 'Timestamp', 'File', 'Method', 'Start', 'End', 'Parameters', 'Num_Parameters', 'NLOC', 'Complexity'])

        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + os.sep + project))[1]
        num_commits = len(commits)

        print('\nProject: ' + project + ' with ' + str(len(commits)) + ' commits')

        count_commits = 1
        for commit in Repository(repository, only_commits=commits).traverse_commits():
            print('Commit: ' + commit.hash + ' (' + str(count_commits) + '/' + str(num_commits) + ')')
            count_commits = count_commits + 1
        #for commit in Repository(repository, single='23e8edd9791b5a2ac025c321f97a9dd2329bbeaa').traverse_commits():    
            for modified_file in commit.modified_files:
                if modified_file.filename.endswith('.java') and not(modified_file.filename == 'package-info.java' or modified_file.filename == 'module-info.java'): 
                    if modified_file.change_type.name == 'RENAME':
                        new_row = pd.DataFrame({'Project': [project], 'Commit': [commit.hash], 'Old path': [modified_file.old_path], 'New path': [modified_file.new_path]})
                        csv_trace = pd.concat([csv_trace, new_row], ignore_index=True, sort=False)
                        csv_trace.to_csv(directory + os.sep + 'trace_files_' + project + '.csv', index=False)
                    elif modified_file.change_type.name == 'ADD' or modified_file.change_type.name == 'MODIFY': 
                        commit_timestamp = int(datetime.timestamp(commit.committer_date))
                        #print(str(commit.committer_date) + ' -> ' + str(commit_timestamp))
                        #print('Committer: ' + commit.committer.name + ' ' + commit.committer.email)
                        #print('Timezone: ' + str(commit.committer_timezone) + '\n')
                        csv_pydriller_metrics = calc_metrics_file(project, commit.hash, str(commit_timestamp), modified_file, csv_pydriller_metrics)
                        csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_' + project + '.csv', index=False)





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
    
    trace_measure(pathProjects, projects)