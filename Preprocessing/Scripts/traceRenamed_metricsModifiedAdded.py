#!/usr/bin/env python3
#SBATCH --partition=mcs.default.q
#SBATCH --output=measure_%j.out

from pydriller import Repository
from git import Repo
import datetime
import argparse
import os
import pandas as pd

def trace_measure(directory, projects):
    
    for project in projects:
        csv_trace = pd.DataFrame(columns=['Project', 'Commit', 'Old path', 'New path'])
        csv_pydriller_metrics = pd.DataFrame(columns=['Project', 'Branches', 'Commit', 'Datetime', 'Timestamp', 'File', 'Method', 'Begin--End', 'Parameters', '#Parameters', 'NLOC', 'Complexity'])

        path_repo = directory + os.sep + project
        repo = Repo(path_repo)

        print('Project: ' + project)
        print('Repo: ' + directory + os.sep + project)

        #TODO: find a way to count all the commits, not just the master commits
        tot_commits = len(list(repo.iter_commits('HEAD')))

        count_commits = 1
        start_time = datetime.datetime.now()

        commits = Repository(path_repo, to=datetime.datetime(2020, 7, 20), only_no_merge=False).traverse_commits()
        #commits_to_convert = commits
        #commit_list = list(commits_to_convert)
        #tot_commits = len(commit_list)
        for commit in commits:
            print('Commit: ' + commit.hash + ' (' + str(count_commits) + '/' + str(tot_commits) + ')')
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

                        for m in modified_file.methods:
                            commit_timestamp = int(datetime.datetime.timestamp(commit.committer_date))
                            commit.branches
                            new_row = pd.DataFrame({'Project': [project], 'Branches': [commit.branches], 'Commit': [commit.hash], 'Datetime':[commit.committer_date], 'Timestamp':[commit_timestamp], 
                                    'File': [modified_file.new_path], 'Method': [m.long_name], 'Begin--End': [str(m.start_line) + '--' + str(m.end_line)],
                                    'Parameters': [m.parameters], '#Parameters': [len(m.parameters)], 'NLOC': [m.nloc], 'Complexity' : [m.complexity]})
                            csv_pydriller_metrics = pd.concat([csv_pydriller_metrics, new_row], ignore_index=True, sort=False)
                            #csv_pydriller_metrics = calc_metrics_file(project, commit.hash, commit.committer_date, modified_file, csv_pydriller_metrics)
                            csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_' + project + '.csv', index=False)
        print('Start: ' + datetime.date.strftime(start_time, "%m/%d/%Y, %H:%M:%S"))
        end_time = datetime.datetime.now()
        print('End: ' + datetime.date.strftime(end_time, "%m/%d/%Y, %H:%M:%S"))
        duration = end_time - start_time
        seconds_in_day = 24 * 60 * 60
        duration_tuple = divmod(duration.days * seconds_in_day + duration.seconds, 60)
        print('The measurement lasted: ' + str(duration_tuple[0]) + ' minutes and ' + str(duration_tuple[1]) + ' seconds')
        print('Number of commits: ' + str(count_commits))





if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for tracing renamed files and computing level-method metrics on changed and added files')

    # Path to repos of projects being analysed
    parser.add_argument(
        'directory_projects',
        type=str,
        help='Projects directory',
    )

    # Projects to be analysed
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

    # Repos Directory
    pathProjects = args.directory_projects

    projects = args.projects_to_analyse
    
    trace_measure(pathProjects, projects)