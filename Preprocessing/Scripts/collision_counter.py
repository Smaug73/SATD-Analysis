from pydriller import Repository
import argparse
import os
import pandas as pd



def count_collisions(directory):
    # Consider only the added and changed files
    accepted_changes = ['MODIFY', 'ADD']

    # Get the name of each project in the directory
    projects = next(os.walk(directory))[1]

    csv_files_with_collisions = pd.DataFrame(columns=['Project', 'Commit', 'File Name', 'Num of homonymous files']) 
    csv_project_percentages = pd.DataFrame(columns=['Project', 'Total Commits', 'Commits with Collisions', 'Percentage Commits with Collisions[%]', 
                                            'Total Modifications', 'Num of Homonymous Files', 'Percentage Homonymous Files[%]', 
                                            'Total Files Modified', 'Num Files to Exclude', 'Percentage Files to Exclude[%]'])
    csv_to_be_reanalysed = pd.DataFrame(columns=['Project', 'Commit', 'File', 'PMD', 'Checkstyle'])

    # Index for acessing rows in csv_files_with_collisions DataFrame
    i = 0

    # Index for acessing rows in csv_project_percentages DataFrame
    j = 0


    for project in projects:
        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + '/' + project))[1]

        print('\nProject: ' + project)
        print('Number of commits: ' + str(len(commits)))

        # Set of commits with at least two homonymous files 
        commits_with_collision_set = set()

        # Set of modified files in the project
        modified_files_set = set()

        # Set of modified homonimous files in the project
        homonymous_modified_files_set = set()

        # Counter of the number of collisions in the project
        collisions_in_project_count = 0

        # Counter of total java files modified (added or modified) in the project
        modified_java_files_project_count = 0

        # Counter of files that need to be re-analysed
        count_files_to_reanalyse = 0
        
        for commit in Repository(repository, only_commits=commits).traverse_commits():

            # Dictionary:
            # Key: Name of the file
            # Value: Number of homonymous files
            modifications_dict = {}

            # Dictionary:
            # Key: Name of the file
            # Value: Path of the file in the commit
            modifications_dict_paths = {}

            for modified_file in commit.modified_files:
                # Consider the file only if it's a java file that has been added or changed in the commit under analysis
                if (modified_file.filename.endswith('.java')) and (modified_file.change_type.name in accepted_changes):
                    modified_files_set.add(modified_file.new_path)
                    modified_java_files_project_count = modified_java_files_project_count + 1

                    # Check whether the file is already in the dictionary:
                    # if it is, increase the number of homonymous files (value in the dictionary),
                    # add the 2 homonimous files in the homonimous_modified_files_set set
                    # and add the commit in the commits_with_collision_set set:
                    # if not, add it in both the modifications_dict dictionary, with value = 1,
                    # and in the modifications_dict_paths dictionary
                    if modified_file.filename in modifications_dict:
                        commits_with_collision_set.add(commit.hash)
                        modifications_dict[modified_file.filename] = modifications_dict[modified_file.filename] + 1
                        homonymous_modified_files_set.add(modified_file.new_path)
                        homonymous_modified_files_set.add(modifications_dict_paths[modified_file.filename])
                    else:
                        modifications_dict[modified_file.filename] = 1
                        modifications_dict_paths[modified_file.filename] = modified_file.new_path
            
            for file_name in modifications_dict:
                if modifications_dict[file_name] > 1:
                    csv_files_with_collisions.loc[i] = [project, commit.hash, file_name, modifications_dict[file_name]]
                    collisions_in_project_count = collisions_in_project_count + modifications_dict[file_name]
                    i = i + 1
            
            count_files_to_reanalyse = count_files_to_reanalyse + count_files_reanalysis_needed(directory, project, 
                                        commit.hash, modifications_dict, homonymous_modified_files_set,  csv_to_be_reanalysed)


        percentage_commits = (len(commits_with_collision_set) / len(commits)) * 100
        percentage_homonymous_file = (collisions_in_project_count / modified_java_files_project_count) * 100
        percentage_exclude_file = (len(homonymous_modified_files_set) / len(modified_files_set)) * 100
        csv_project_percentages.loc[j] = [project, str(len(commits)), len(commits_with_collision_set), 
                                            percentage_commits, modified_java_files_project_count, collisions_in_project_count, 
                                            percentage_homonymous_file, str(len(modified_files_set)), str(len(homonymous_modified_files_set)), 
                                            percentage_exclude_file]
        j = j + 1
        print('Total modified java files: ' + str(modified_java_files_project_count))
        print('Total collisions: ' + str(collisions_in_project_count))
        print('Percentage: ' + str((collisions_in_project_count / modified_java_files_project_count) * 100))
        print('Files to be reanalysed: ' + str(count_files_to_reanalyse))
        
    
    csv_files_with_collisions.to_csv(directory + '/files_with_collisions.csv', index=False)
    csv_project_percentages.to_csv(directory + '/project_percentage.csv', index=False)
    csv_to_be_reanalysed.to_csv(directory + '/files_to_be_reanalysed.csv', index=False)


# Count and store into a csv the files that need to be re-analysed:
# TODO: PMD: check the package. If the same, both files need to be re-analysed; otherwise only one of the files should be analysed
# TODO: same thing for checkstyle
# TODO: code needs to be improved
def count_files_reanalysis_needed(directory, project, commit, modifications_dict, homonymous_set, csv_to_be_reanalysed):
    
    csv_static_analysis = pd.read_csv(directory + '/' + project + '/' + commit + '/pmd-' + commit + '.csv')
    
    to_exclude = []

    count = 0
    for i in range(0, len(csv_static_analysis) - 1):
        package = csv_static_analysis.at[i, 'Package'].replace('.', '/')
        filename = csv_static_analysis.at[i, 'File'].split('/')[-1]
        if not(filename in to_exclude) and (filename in modifications_dict) and (modifications_dict[filename] > 1):
            to_exclude.append(filename)
            subpath = package + '/' + filename

            homonymous_dict = {}
            homonymous_dict[subpath] = 0
            for homonymous_file in homonymous_set:
                if homonymous_file.endswith(subpath):
                    homonymous_dict[subpath] = homonymous_dict[subpath] + 1
                '''
                elif homonymous_file.endswith(filename):
                    #print('Other in commit ' + commit + ' :' + homonymous_file )
                    homonymous_dict[subpath] = 0
                '''
            print('Homonymous dict ' + commit + ' ' + str(homonymous_dict))
            if not(homonymous_dict[subpath] == 1):
                for homonymous_file in homonymous_set:
                    if homonymous_file.endswith(subpath):
                        csv_to_be_reanalysed.loc[len(csv_to_be_reanalysed)] = [project, commit, homonymous_file, 1, 1]
                        count = count + 1
                    '''
                    elif homonymous_file.endswith(filename):
                        csv_to_be_reanalysed.loc[len(csv_to_be_reanalysed)] = [project, commit, homonymous_file, 1, 1]
                        count = count + 1
                    '''
    return count
               





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

    
    count_collisions(pathProjects)