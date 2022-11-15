import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
import pandas as pd
import argparse
import os
import subprocess 
import git


def get_previous_commits(repos_directory, metrics_directory, projects):
    for project in projects:

        print('\nProject: ' + project)
        start_time = datetime.datetime.now()
        
        path_repo = repos_directory + os.sep + project
        #repo = git.Repo(path_repo)
        

        '''
        commits = repo.traverse_commits()

        for commit in commits:
        '''           
        commits_dataset= pd.read_csv(metrics_directory + os.sep + 'pydriller_metrics_' + project + '.csv')

        commits = commits_dataset['Commit'].unique()

        print('\nCommits: ' + str(len(commits)))

        count_commits = 0
        rows = []

        
        for commit in commits:
            start_time_commit = datetime.datetime.now()

            count_commits = count_commits + 1
            print('\nCommit ' + commit + ' (' + str(count_commits) + '/' + str(len(commits)) + ')')
            runCmdList(['git', 'checkout', commit], path_repo)

            
            
            files_dict = {}
            
            modified_files = commits_dataset[commits_dataset['Commit'] == commit]['File'].unique()

            for file in modified_files:
                files_dict[file] = []
                prev_commits = runCmdList(['git', 'log', '--oneline', '--full-history', '--pretty=format:"%H"' '--follow', file], path_repo)
                i = 0
                for prev_commit in prev_commits:
                    files_dict[file].append(prev_commit)
                    i = i + 1
                    if i == 8:
                        break
            
            #print('Commit: ' + commit + '\n' + str(files_dict) + '\n\n')
            for file in files_dict:
                if len(files_dict[file]) >= 9:
                    new_row = [commit, file, files_dict[file][0], files_dict[file][1], files_dict[file][2], files_dict[file][3], files_dict[file][4],
                            files_dict[file][5], files_dict[file][6], files_dict[file][7], files_dict[file][8]]
                    print(new_row + '\n ')
                    rows.append('NEW ROW: ' + new_row)
                else:
                    print('ELSE\n' + str(files_dict[file]))
            '''
            for other_commit in commits:
                if (other_commit != commit):
                    other_modified_files = commits_dataset[commits_dataset['Commit'] == other_commit]['File'].unique()
                    if any(x in modified_files for x in other_modified_files):
                        range = other_commit + '..' + commit
                        lines = runCmdList(['git', 'rev-list', '--ancestry-path', range, '--count'], path_repo)
                        hops = int(lines[0])

                        #hops = len(repo.git.rev_list('--ancestry-path',range))
                        if hops != 0:
                            #print('\n' + "Current commit: " + commit + "   Ancestor: " +  other_commit + "   Hops:" + str(hops))
                            for file in modified_files:
                                
                                if file in other_modified_files:
                                    if file not in files_dict:
                                        files_dict[file] = {}
                                    if hops not in files_dict[file]:
                                        files_dict[file][hops] = set()
                                    files_dict[file][hops].add(other_commit)

            #print('Commit: ' + commit + '\n' + str(files_dict) + '\n\n')
            for file in files_dict:
                if len(files_dict[file]) >= 9:
                    print('\nCommit: ' + commit + ' file: ' + file + '\n' + str(files_dict[file]) + '\n\n')
                    prev_commits_dict = {}
                    i = 1
                    for k in sorted((files_dict[file])):
                        if i < 10:
                            prev_commits_dict[i] = files_dict[file][k]
                            print('\n' + str(i) + ' :' + str(files_dict[file][k]) + ' hops: ' + str(k) + '\n')
                            i = i + 1
                        else:
                            break

                    new_row = [commit, file, prev_commits_dict[1], prev_commits_dict[2], prev_commits_dict[3], prev_commits_dict[4], prev_commits_dict[5],
                        prev_commits_dict[6], prev_commits_dict[7], prev_commits_dict[8], prev_commits_dict[9]]
                    rows.append(new_row)
            '''
            end_time_commit = datetime.datetime.now()
            duration_commit = end_time_commit - start_time_commit
            seconds_in_day = 24 * 60 * 60
            duration_tuple_commit = divmod(duration_commit.days * seconds_in_day + duration_commit.seconds, 60)
            print('The measurement for commit ' + commit + ' lasted: ' + str(duration_tuple_commit[0]) + ' minutes and ' + str(duration_tuple_commit[1]) + ' seconds')
        
        csv_previous_commits = pd.DataFrame(rows, columns=['Commit', 'File', 'Commit-1', 'Commit-2', 'Commit-3', 'Commit-4', 'Commit-5', 'Commit-6', 'Commit-7', 'Commit-8', 'Commit-9'])
        csv_previous_commits.to_csv('previous_commits_'+ project + '.csv', index=False)
        end_time = datetime.datetime.now()
        print('End: ' + datetime.date.strftime(end_time, "%m/%d/%Y, %H:%M:%S"))
        duration = end_time - start_time
        seconds_in_day = 24 * 60 * 60
        duration_tuple = divmod(duration.days * seconds_in_day + duration.seconds, 60)
        print('The measurement for project ' + project + ' lasted: ' + str(duration_tuple[0]) + ' minutes and ' + str(duration_tuple[1]) + ' seconds')                    
                              

            
        '''
        if commit == 'c58670cbdbb227df34b67ff8855e3d4beca0a4e1':
            for c in other_commits:
                print('\n' + c)
        '''


def runCmdList(commands, path_repo):
    try:
        x = subprocess.check_output(commands, cwd=path_repo)
        lines=str(x.decode("latin-1",errors='ignore')).splitlines()
        return lines
    except:
        return []





if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for finding 10 previous commits where a file x was modified')

    # Path to repos of projects being analysed
    parser.add_argument(
        'directory_repos',
        type=str,
        help='Repos directory',
    )

    parser.add_argument(
        '-md',
        '--metrics_directory',
        type=str,
        help='Path to the directory containing metrics CSVs of each project',
        required=True
    )

    # Repos to be analysed
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
    pathProjects = args.directory_repos

    metricsDirectory = args.metrics_directory

    projects = args.projects_to_analyse
    
    get_previous_commits(pathProjects, metricsDirectory, projects)

