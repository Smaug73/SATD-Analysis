#!/usr/bin/env python3
#SBATCH --partition=mcs.default.q
#SBATCH --output=measure_%j.out

from pydriller import Repository
import datetime
import argparse
import os
import pandas as pd
import sys

sys.path.append(os.getcwd())
from pydriller_method_metrics import calc_metrics_file

def trace_measure(directory, projects):
    csv_trace = pd.DataFrame(columns=['Project', 'Commit', 'Old path', 'New path'])
    
    for project in projects:
        csv_pydriller_metrics = pd.DataFrame(columns=['Project', 'Branch', 'Commit', 'Datetime', 'Timestamp', 'File', 'Method', 'Begin--End', 'Parameters', '#Parameters', 'NLOC', 'Complexity'])

        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        print ('Project: ' + project)
        #commits = next(os.walk(directory + os.sep + project))[1]
        #num_commits = len(commits)

        #print('\nProject: ' + project + ' with ' + str(len(commits)) + ' commits')

        count_commits = 1
        start_time = datetime.datetime.now()
        print('Start: ' + datetime.date.strftime(start_time, "%m/%d/%Y, %H:%M:%S"))

        commits = Repository(repository, to=datetime.datetime(2020, 7, 20), only_no_merge=False).traverse_commits()
        #commits_to_convert = commits
        #commit_list = list(commits_to_convert)
        #tot_commits = len(commit_list)
        for commit in commits:
            print('Commit: ' + commit.hash + ' (' + str(count_commits) + ')')
            count_commits = count_commits + 1
            #commit_timestamp = int(datetime.timestamp(commit.committer_date))
            #print(str(commit.committer_date) + ' -> ' + str(commit_timestamp) + '\n')
        #for commit in Repository(repository, single='23e8edd9791b5a2ac025c321f97a9dd2329bbeaa').traverse_commits(): 
            for modified_file in commit.modified_files:
                if modified_file.filename.endswith('.java') and not(modified_file.filename == 'package-info.java' or modified_file.filename == 'module-info.java'): 
                    if modified_file.change_type.name == 'RENAME':
                        new_row = pd.DataFrame({'Project': [project], 'Commit': [commit.hash], 'Old path': [modified_file.old_path], 'New path': [modified_file.new_path]})
                        csv_trace = pd.concat([csv_trace, new_row], ignore_index=True, sort=False)
                        csv_trace.to_csv(directory + os.sep + 'renamed_files_' + project + '.csv', index=False)
                    elif modified_file.change_type.name == 'ADD' or modified_file.change_type.name == 'MODIFY':  
                        #print('Committer: ' + commit.committer.name + ' ' + commit.committer.email)
                        #print('Timezone: ' + str(commit.committer_timezone) + '\n')
                        csv_pydriller_metrics = calc_metrics_file(project, commit.hash, commit.committer_date, modified_file, csv_pydriller_metrics)
                        csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_' + project + '.csv', index=False)
        end_time = datetime.datetime.now()
        print('End: ' + datetime.date.strftime(end_time, "%m/%d/%Y, %H:%M:%S"))
        duration = end_time - start_time
        seconds_in_day = 24 * 60 * 60
        duration_tuple = divmod(duration.days * seconds_in_day + duration.seconds, 60)
        print('The measurement lasted: ' + str(duration_tuple[0]) + ' minutes and ' + str(duration_tuple[1]) + ' seconds')
        print('Number of commits: ' + str(count_commits))





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