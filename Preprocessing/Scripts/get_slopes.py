import numpy as np
import datetime
import pandas as pd
import argparse
import os
import subprocess 
from scipy import stats


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
        final_array = np.zeros((commits_dataset.shape[0], 3))

        commits = commits_dataset['Commit'].unique()

        print('\nCommits: ' + str(len(commits)))

        count_commits = 0
        #rows = []

        x = np.arange(10)
        
        
        for commit in commits:
            start_time_commit = datetime.datetime.now()

            count_commits = count_commits + 1
            print('\nCommit ' + commit + ' (' + str(count_commits) + '/' + str(len(commits)) + ')')
            runCmdList(['git', 'checkout', commit], path_repo)

            
            
            files_dict = {}
            
            modified_files = commits_dataset[commits_dataset['Commit'] == commit]['File'].unique()

            start_time_ten_files = datetime.datetime.now()
            for file in modified_files:
                start_time_single_file = datetime.datetime.now()
                files_dict[file] = []
                prev_commits = runCmdList(['git', 'log', '--oneline', '--full-history', '--pretty=format:\"%H\"', '--follow', file], path_repo)
                i = 0
                for prev_commit in prev_commits:
                    files_dict[file].append(prev_commit.replace('\"',''))
                    i = i + 1
                    if i == 10:
                        end_time_single_file = datetime.datetime.now()
                        duration_single_file = end_time_single_file - start_time_single_file
                        seconds_in_day = 24 * 60 * 60
                        duration_tuple_single_file = divmod(duration_single_file.days * seconds_in_day + duration_single_file.seconds, 60)
                        print('The extraction of 10 previous commits for the file ' + file + ' lasted: ' + str(duration_tuple_single_file[0]) + ' minutes and ' + str(duration_tuple_single_file[1]) + ' seconds')                    
        
                        break
            end_time_ten_files = datetime.datetime.now()
            duration_ten_files = end_time_ten_files - start_time_ten_files
            seconds_in_day = 24 * 60 * 60
            duration_tuple_ten_files = divmod(duration_ten_files.days * seconds_in_day + duration_ten_files.seconds, 60)
            print('The extraction of 10 previous commits for all the modified files in the commit ' + commit + ' lasted: ' + str(duration_tuple_ten_files[0]) + ' minutes and ' + str(duration_tuple_ten_files[1]) + ' seconds')                    
        

            #print('Commit: ' + commit + '\n' + str(files_dict) + '\n\n')
            start_time_get_all_slopes = datetime.datetime.now()
            for file in files_dict:
                start_time_slopes_single_file = datetime.datetime.now()
                methods = commits_dataset[commits_dataset['Commit'] == commit][commits_dataset['File'] == file]['Method']
                for method in methods:
                    #print('METHOD: ' + method)
                    index_current = ((commits_dataset[commits_dataset['Commit'] == commit])[commits_dataset['File'] == file])[commits_dataset['Method'] == method].index[0]
                    #print('CURRENT INDEX: ' + str(index_current))
                    if len(files_dict[file]) >= 10:
                        #print('METHOD: ' + method)
                        y_loc = np.zeros((10))
                        y_params = np.zeros((10))
                        y_complex = np.zeros((10))
                        try:
                            for j in range(0, 10):
                                other_commit = files_dict[file][j]
                                #print('OTHER COMMIT: ' + other_commit)
                                index = commits_dataset[commits_dataset['Commit'] == other_commit][commits_dataset['File'] == file][commits_dataset['Method'] == method].index[0]
                                y_loc[9 - j] = commits_dataset.iloc[index]['NLOC']
                                y_params[9 - j] = commits_dataset.iloc[index]['#Parameters']
                                y_complex[9 - j] = commits_dataset.iloc[index]['Complexity']
                                
                            #print('\ny_loc:')
                            #print(y_loc)
                            #print('\ny_params:')
                            #print(y_params)
                            #print('\ny_complex:')
                            #print(y_complex)
                            start_time_linregr = datetime.datetime.now()
                            try:
                                slope_loc, intercept, r, p, std_err = stats.linregress(x, y_loc)
                            except Exception as e:
                                print(e)
                            final_array[index_current, 0] = slope_loc
                            #print('slope loc final array: ' + str(final_array[index_current, 0]))

                            try:
                                slope_params, intercept, r, p, std_err = stats.linregress(x, y_params)
                            except Exception as e:
                                print(e)
                            final_array[index_current, 1] = slope_params

                            try:
                                slope_complex, intercept, r, p, std_err = stats.linregress(x, y_complex)
                            except Exception as e:
                                print(e)
                            final_array[index_current, 2] = slope_complex

                            end_time_linregr = datetime.datetime.now()
                            duration_linregr  = end_time_linregr  - start_time_linregr
                            seconds_in_day = 24 * 60 * 60
                            duration_tuple_linregr  = divmod(duration_linregr.days * seconds_in_day + duration_linregr.seconds, 60)
                            print('The linear regression calculation for method ' + method + ' in file ' + file + ' lasted: ' + str(duration_tuple_linregr[0]) + ' minutes and ' + str(duration_tuple_linregr[1]) + ' seconds')
        
                        except:
                            final_array[index_current, 0] = np.NaN
                            final_array[index_current, 1] = np.NaN
                            final_array[index_current, 2] = np.NaN

                    #print('IF ' + file + ' ' + str(len(files_dict[file])) + '\n' + str(files_dict[file]))
                    #new_row = [commit, file, files_dict[file][1], files_dict[file][2], files_dict[file][3], files_dict[file][4], files_dict[file][5],
                    #        files_dict[file][6], files_dict[file][7], files_dict[file][8], files_dict[file][9]]
                    #rows.append(new_row)

                    else:
                        #print('\nELSE\n')
                        #index_current = commits_dataset[commits_dataset['Commit'] == commit][commits_dataset['File'] == file][commits_dataset['Method'] == method].index[0]
                        final_array[index_current, 0] = np.NaN
                        final_array[index_current, 1] = np.NaN
                        final_array[index_current, 2] = np.NaN


                end_time_slopes_single_file = datetime.datetime.now()
                duration_slopes_single_file  = end_time_slopes_single_file  - start_time_slopes_single_file 
                seconds_in_day = 24 * 60 * 60
                duration_tuple_slopes_single_file  = divmod(duration_slopes_single_file.days * seconds_in_day + duration_slopes_single_file.seconds, 60)
                #print(x)
                print('The slope extraction for all methods in file ' + file + ' lasted: ' + str(duration_tuple_slopes_single_file[0]) + ' minutes and ' + str(duration_tuple_slopes_single_file[1]) + ' seconds')
        
            
            
            end_time_get_all_slopes = datetime.datetime.now()
            duration_get_all_slopes  = end_time_get_all_slopes  - start_time_get_all_slopes 
            seconds_in_day = 24 * 60 * 60
            duration_tuple_get_all_slopes  = divmod(duration_get_all_slopes.days * seconds_in_day + duration_get_all_slopes.seconds, 60)
            #print(x)
            print('The slope extraction for method ' + method + ' in file ' + file + ' lasted: ' + str(duration_tuple_get_all_slopes[0]) + ' minutes and ' + str(duration_tuple_get_all_slopes[1]) + ' seconds')
        

            end_time_commit = datetime.datetime.now()
            duration_commit = end_time_commit - start_time_commit
            seconds_in_day = 24 * 60 * 60
            duration_tuple_commit = divmod(duration_commit.days * seconds_in_day + duration_commit.seconds, 60)
            #print(x)
            print('The measurement for commit ' + commit + ' lasted: ' + str(duration_tuple_commit[0]) + ' minutes and ' + str(duration_tuple_commit[1]) + ' seconds')
        

        #csv_previous_commits = pd.DataFrame(rows, columns=['Commit', 'File', 'Commit-1', 'Commit-2', 'Commit-3', 'Commit-4', 'Commit-5', 'Commit-6', 'Commit-7', 'Commit-8', 'Commit-9'])
        #csv_previous_commits.to_csv('previous_commits_'+ project + '.csv', index=False)
        lst = final_array.tolist()
        #print(final_array)
        #print(lst)
        slopes_dataframe = pd.DataFrame(lst, columns =['NLOC_slope', 'Params_slope', 'Complexity_slope'])
        slopes_dataframe.to_csv('slopes_'+ project + '.csv', index=False)

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

