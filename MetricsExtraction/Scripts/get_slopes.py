import numpy as np
import datetime
import pandas as pd
import argparse
import os
import subprocess 
from scipy import stats


def get_previous_commits(repos_directory, metrics_directory, projects, output_path):
    for project in projects:

        print('\nProject: ' + project)
        start_time = datetime.datetime.now()
        
        path_repo = repos_directory + os.sep + project
 
        commits_dataset= pd.read_csv(metrics_directory + os.sep + 'pydriller_metrics_' + project + '.csv')
        final_array = np.zeros((commits_dataset.shape[0], 3))

        commits = commits_dataset['Commit'].unique()

        print('\nCommits: ' + str(len(commits)))

        count_commits = 0

        x = np.arange(10)
        
        # For each commit create a dictionary (key: file; value: list of 10 most recent commits in which the file was modified);
        # For each file in the dictionary scn all its method and for each of them calculate the slope for the 3 metrics
        for commit in commits:

            count_commits = count_commits + 1
            print('\nCommit ' + commit + ' (' + str(count_commits) + '/' + str(len(commits)) + ')')
            runCmdList(['git', 'checkout', commit], path_repo)

            
            # Dictionary:
            # Key -> File
            # Value -> List of 10 most recent commits in which the file used as key was modified
            files_dict = {}
            subset_commit = commits_dataset[commits_dataset['Commit'] == commit]

            modified_files = subset_commit['File'].unique()

            for file in modified_files:
                files_dict[file] = []

                # Command that lists all the commits in which a given file was modified
                prev_commits = runCmdList(['git', 'log', '--oneline', '--full-history', '--pretty=format:\"%H\"', '--follow', file], path_repo)
                i = 0
                # Take only the 10 most recent commits
                for prev_commit in prev_commits:
                    files_dict[file].append(prev_commit.replace('\"',''))
                    i = i + 1
                    if i == 10:
                        break
            
            #print('Commit: ' + commit + '\n' + str(files_dict) + '\n\n')
            
            for file in files_dict:
                file_subset = subset_commit[subset_commit['File'] == file]

                methods = file_subset['Method']

                for method in methods:
                    index_current = ((commits_dataset[commits_dataset['Commit'] == commit])[commits_dataset['File'] == file])[commits_dataset['Method'] == method].index[0]
                    #print('CURRENT INDEX: ' + str(index_current))
                    if len(files_dict[file]) >= 10:
                        #print('METHOD: ' + method)
                        y_loc = np.zeros((10))
                        y_params = np.zeros((10))
                        y_complex = np.zeros((10))
                        try:
                            
                            filtered_dataset = getLastTenMeasures(commits_dataset,files_dict[file], file , method)

                            if len(filtered_dataset)==10:

                                for j in range(0, 10):
                                    y_loc[j] = filtered_dataset.iloc[j]['NLOC']
                                    y_params[j] = filtered_dataset.iloc[j]['#Parameters']
                                    y_complex[j] = filtered_dataset.iloc[j]['Complexity']
                                    
                                #print('\ny_loc:')
                                #print(y_loc)
                                #print('\ny_params:')
                                #print(y_params)
                                #print('\ny_complex:')
                                #print(y_complex)
                                
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

                                
                            else:
                                final_array[index_current, 0] = np.NaN
                                final_array[index_current, 1] = np.NaN
                                final_array[index_current, 2] = np.NaN

                        except:
                            final_array[index_current, 0] = np.NaN
                            final_array[index_current, 1] = np.NaN
                            final_array[index_current, 2] = np.NaN

                        


                    else:
                        #print('\nELSE\n')
                        #index_current = commits_dataset[commits_dataset['Commit'] == commit][commits_dataset['File'] == file][commits_dataset['Method'] == method].index[0]
                        final_array[index_current, 0] = np.NaN
                        final_array[index_current, 1] = np.NaN
                        final_array[index_current, 2] = np.NaN


        
            

        lst = final_array.tolist()

        slopes_dataframe = pd.DataFrame(lst, columns =['NLOC_slope', 'Params_slope', 'Complexity_slope'])
        result = pd.concat([commits_dataset, slopes_dataframe], axis=1)
        result.to_csv(output_path + os.sep + 'slopes_'+ project + '.csv', index=False)

        end_time = datetime.datetime.now()
        print('End: ' + datetime.date.strftime(end_time, "%m/%d/%Y, %H:%M:%S"))
        duration = end_time - start_time
        seconds_in_day = 24 * 60 * 60
        duration_tuple = divmod(duration.days * seconds_in_day + duration.seconds, 60)
        print('The measurement for project ' + project + ' lasted: ' + str(duration_tuple[0]) + ' minutes and ' + str(duration_tuple[1]) + ' seconds')                    
                              



# Run the specified command from command line in the specified directory
def runCmdList(commands, path_repo):
    try:
        x = subprocess.check_output(commands, cwd=path_repo)
        lines=str(x.decode("latin-1",errors='ignore')).splitlines()
        return lines
    except:
        return []



# Filter the dataset: return only the rows containing specified commit, file and method
def getLastTenMeasures(dataset,commits,file,method):
    filtered_dataset = dataset[dataset.Commit.isin(commits) & dataset.File.isin([file]) & dataset.Method.isin([method])]
    return filtered_dataset






if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for finding 10 previous commits where a file x was modified')

    # Path to repos of projects being analysed
    parser.add_argument(
        'directory_repos',
        type=str,
        help='Repos directory',
    )

    # Directory containing CSVs produced by calculate_metrics.py script
    parser.add_argument(
        '-md',
        '--metrics_directory',
        type=str,
        help='Path to the directory containing metrics CSVs of each project',
        required=True
    )

    # List of projects to be analysed, separated by a blank space
    parser.add_argument(
        '-p',
        '--projects_to_analyse',
        type=str,
        nargs='+',
        help='Projects to analyse',
        required=True
    )

    # List of projects to be analysed, separated by a blank space
    parser.add_argument(
        '-o',
        '--output_directory',
        type=str,
        help='Directory where to save the result',
        required=True
    )


    # Parsing the args
    args = parser.parse_args()

    # Repos Directory
    pathProjects = args.directory_repos

    # Directory containing CSVs produced by calculate_metrics.py script
    metricsDirectory = args.metrics_directory

    # Names of the projects to be analysed
    projects = args.projects_to_analyse

    # Output path
    output_path = args.output_directory
    
    get_previous_commits(pathProjects, metricsDirectory, projects, output_path)

