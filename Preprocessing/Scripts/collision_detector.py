from pydriller import Repository
import argparse
import sys
import os
import pandas as pd
from download_modFile_commit import download_Modifiedfile


def count_collisions(directory, projects):

    print('Projects analysed in this process: ' + str(projects))
    
    csv_files_with_collisions = pd.DataFrame(columns=['Project', 'Commit', 'File', 'Is PMD Needed'])
    csv_collision_counter = pd.DataFrame(columns=['Project', 'Total Modifications', 'Num of Homonymous Files', 'Total Commits', 'Num of Commits with Homonymous Files'])

    # Index for acessing rows in csv_files_with_collisions DataFrame
    i = 0

    # Index for acessing rows in csv_collision_counter DataFrame
    j = 0

    # Consider only the added and changed files
    accepted_changes = ['MODIFY', 'ADD']

    # Get the name of each project in the directory
    # projects = next(os.walk(directory))[1]

    string_projects_analysed = ''
    for project in projects:
       string_projects_analysed = string_projects_analysed + '_' + project 

    for project in projects:
        
        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + '/' + project))[1]

        print('\nProject: ' + project)
        print('Number of commits: ' + str(len(commits)))

        # Counter of the number of homonimous files in the project
        homonymous_files_in_project_count = 0

        # Counter of total java files modified (added or modified) in the project
        modified_java_files_project_count = 0

        # Counter of files that need to be re-analysed
        files_to_reanalyse_count = 0

        # Set of commits with homonymous files
        commits_with_collision_set = set()
        
        for commit in Repository(repository, only_commits=commits).traverse_commits():

            # Dictionary:
            # Key: Name of the file
            # Value: Number of homonymous files
            modifications_dict_count = {}

            # Dictionary:
            # Key: Name of the file
            # Value: Object Modified_file
            modifications_dict_paths = {}

            homonymous_modified_files_set = set()

            for modified_file in commit.modified_files:
                # Consider the file only if it's a java file that has been added or changed in the commit under analysis
                if (modified_file.filename.endswith('.java')) and (modified_file.change_type.name in accepted_changes):
                    modified_java_files_project_count = modified_java_files_project_count + 1

                    # Check whether the file is already in the dictionary:
                    # if it is, increase the number of homonymous files (value in the dictionary),
                    # add the 2 homonimous files in the homonimous_modified_files_set set
                    # and add the commit in the commits_with_collision_set set:
                    # if not, add it in both the modifications_dict dictionary, with value = 1,
                    # and in the modifications_dict_paths dictionary
                    if modified_file.filename in modifications_dict_count:
                        modifications_dict_count[modified_file.filename] = modifications_dict_count[modified_file.filename] + 1
                        homonymous_modified_files_set.add(modified_file)
                        homonymous_modified_files_set.add(modifications_dict_paths[modified_file.filename])
                        commits_with_collision_set.add(commit.hash)
                    else:
                        modifications_dict_count[modified_file.filename] = 1
                        modifications_dict_paths[modified_file.filename] = modified_file
            

            for file_name in modifications_dict_count:
                if modifications_dict_count[file_name] > 1:
                    homonymous_files_in_project_count = homonymous_files_in_project_count + modifications_dict_count[file_name]

            homonymous_filepaths_set = set()
            for mod_file in homonymous_modified_files_set:
                homonymous_filepaths_set.add(mod_file.new_path)

            files_to_reanalyse_count_commit, to_reanalyse_pmd = count_files_reanalysis_needed_pmd(directory, project, 
                                        commit.hash, homonymous_filepaths_set, modifications_dict_count)

            files_to_reanalyse_count = files_to_reanalyse_count + files_to_reanalyse_count_commit

            files_downloaded_count = 0
            for mod_file in homonymous_modified_files_set:
                if mod_file.new_path in to_reanalyse_pmd:
                    csv_files_with_collisions.loc[i] = [project, commit.hash, mod_file.new_path, 1]
                else:
                    csv_files_with_collisions.loc[i] = [project, commit.hash, mod_file.new_path, 0]
                csv_files_with_collisions.to_csv(directory + '/files_with_collisions' + string_projects_analysed + '.csv', index=False)
                i = i + 1
                download_Modifiedfile(mod_file, project, commit.hash)
                files_downloaded_count = files_downloaded_count + 1
                #print('\nFiles downloaded in project ' + project + ': ' + str(files_downloaded_count) + '/' + str(len(homonymous_modified_files_set)))

        csv_collision_counter.loc[j] = [project, modified_java_files_project_count, homonymous_files_in_project_count, len(commits), len(commits_with_collision_set)]
        csv_collision_counter.to_csv(directory + '/project_collisions_count' + string_projects_analysed + '.csv', index=False)
        j = j + 1
        print('Total modified java files: ' + str(modified_java_files_project_count))
        print('Total homonymous files: ' + str(homonymous_files_in_project_count))
        print('Files to be reanalysed with PMD: ' + str(files_to_reanalyse_count))
        print('Commits with homonymous files: ' + str(len(commits_with_collision_set)))


# Count and store into a csv the files that need to be re-analysed with PMD. That happens in 3 cases:
# 1: There are more than one file with the same subpath (obtained through Package column in the csv). 
#    All the files with the same subpath should be re-analysed
# 2: There are two or more files with the same name but different subpaths. 
#    Only the files that have a different subpath from the one obtained using the package of the file should be reanalysed
# 3: None of the homonymous files have a row in the pmd results csv. 
#    That means that no violation was discovered during the analysis, but we don't know on which file the said analysis was conducted
def count_files_reanalysis_needed_pmd(directory, project, commit, homonymous_set, modifications_dict):
    try:
        csv_static_analysis = pd.read_csv(directory + '/' + project + '/' + commit + '/pmd-' + commit + '.csv')
    except:
        print('File: ' + directory + '/' + project + '/' + commit + '/pmd-' + commit + '.csv is empty')
        return len(homonymous_set), homonymous_set
    # Dictionary:
    # Key: subpath obtained concatenating package and filename
    # Value: repository path ending with the key subpath
    homonymous_subpath_dict = {}

    # Set of files needing pmd re-analysis
    to_reanalyse_set = set()

    # Files that ends with one of the subpaths obtained from csv rows
    travesed_homonymous_files = set()

    # The same file can have multiple rows in the csv if more than one violation was detected. 
    # Need to exclude files already read and checked
    to_exclude = []

    # For each file in the csv:
    # Create the subpath concatenating package and filename;
    # Check if the file wasn't already examinated and if it has homonyms;
    # If it does:
    # Search the repository path among the set of all the homonymous files of the commit;
    # Check if there's already an entry in the homonymous_subpath_dict dictionary with key == subpath:
    # True => add to the to_reanalyse_set set both the file under analysis and the one in the dictionary (case 1)
    # False => add an entry into homonymous_subpath_dict dictionary: key = subpath, value = repository path
    for i in range(0, len(csv_static_analysis)):
        try:
            package = csv_static_analysis.at[i, 'Package'].replace('.', '/')
        except Exception:
            #print(e)
            #print('Exception for package: ' +  str(csv_static_analysis.at[i, 'Package']) + ' at line ' + str(i) + ' for commit ' + commit)
            package = ''
        filename = csv_static_analysis.at[i, 'File'].split('/')[-1]
        subpath = package + '/' + filename
        if not(subpath in to_exclude) and (filename in modifications_dict) and (modifications_dict[filename] > 1):
            to_exclude.append(subpath)
            
            for homonymous_file in homonymous_set:
                if homonymous_file.endswith(subpath):
                    travesed_homonymous_files.add(homonymous_file)
                    if subpath in homonymous_subpath_dict:
                        to_reanalyse_set.add(homonymous_file)
                        to_reanalyse_set.add(homonymous_subpath_dict[subpath])
                    else:
                        homonymous_subpath_dict[subpath] = homonymous_file
        
    # If the homonymous file was not traversed, reanalysis is needed (cases 2 and 3)
    for homonymous_file in homonymous_set:
        if not(homonymous_file in travesed_homonymous_files):
            to_reanalyse_set.add(homonymous_file)


    return len(to_reanalyse_set), to_reanalyse_set
               




if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for converting xml file from checkstyle analysis to csv')

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
    
    count_collisions(pathProjects, projects)
