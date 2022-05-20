from pydriller import Repository
import argparse
import os
import pandas as pd

def count_collisions(directory):
    accepted_changes = ['MODIFY', 'ADD']
    # Get the name of each project in the directory
    projects = next(os.walk(directory))[1]

    csv_files_with_collisions = pd.DataFrame(columns=['Project', 'Commit', 'File Name', 'Num of homonymous files']) 
    csv_project_percentages = pd.DataFrame(columns=['Project', 'Total Commits', 'Commits with Collisions', 'Percentage Commits with Collisions[%]', 
                                            'Total Java Files Modified', 'Files with Collisions', 'Percentage Files with Collisions[%]'])

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
        homonimous_modified_files_set = set()

        # Counter of the number of collisions in the project
        collisions_in_project_count = 0

        # Counter of total java files modified (added or modified) in the project
        modified_java_files_project_count = 0
        
        for commit in Repository(repository, only_commits=commits).traverse_commits():

            # Counter of total java files modified (added or modified) in the commit
            modified_java_files_commit_count = 0

            # Counter of homonymous java files modified (added or modified) in the commit
            files_with_collision_count = 0

            # Dictionary:
            # Key: Name of the file
            # Value: Number of homonymous files
            modifications_dict = {}

            modifications_dict_paths = {}

            for modified_file in commit.modified_files:
                # Consider the file only if it's a java file that has been added or changed in the commit under analysis
                if (modified_file.filename.endswith('.java')) and (modified_file.change_type.name in accepted_changes):
                    modified_files_set.add(modified_file.new_path)
                    modified_java_files_commit_count = modified_java_files_commit_count + 1

                    # Check whether the file is already in the dictionary:
                    # if it is, increase the number of homonymous files (value in the dictionary),
                    # increase the number of total collisions
                    # and add the commit in the commits_with_collision_set set:
                    # if not, add it in the dictionary, with value = 1
                    if modified_file.filename in modifications_dict:
                        commits_with_collision_set.add(commit.hash)
                        files_with_collision_count = files_with_collision_count + 1
                        modifications_dict[modified_file.filename] = modifications_dict[modified_file.filename] + 1
                        homonimous_modified_files_set.add(modified_file.new_path)
                        homonimous_modified_files_set.add(modifications_dict_paths[modified_file.filename])
                        # csv_files_with_collisions.loc[i] = [project, commit.hash, modified_file.filename]
                        # i = i + 1
                        #print('COLLISION!')
                        #print(modified_file.new_path)
                        #print(modifications_dict[modified_file.filename])
                    else:
                        modifications_dict[modified_file.filename] = 1
                        modifications_dict_paths[modified_file.filename] = modified_file.new_path

            collisions_commit = modified_java_files_commit_count - len(modifications_dict)
            collisions_in_project_count = collisions_in_project_count + collisions_commit
            modified_java_files_project_count = modified_java_files_project_count + modified_java_files_commit_count
            
            for collision in modifications_dict:
                if modifications_dict[collision] > 1:
                    csv_files_with_collisions.loc[i] = [project, commit.hash, collision, modifications_dict[collision]]
                    i = i + 1
            '''
            if collisions_commit > 0:
                print('There are ' + str(collisions_commit + 1) + ' modified java files with the same name but different package')
            else:
                print('No collisions found')
            '''
        
        percentage_commits = (len(commits_with_collision_set) / len(commits)) * 100
        percentage_file = (collisions_in_project_count / modified_java_files_project_count) * 100
        percentage_all_file = (len(homonimous_modified_files_set) / len(modified_files_set)) * 100
        csv_project_percentages.loc[j] = [project, str(len(commits)), len(commits_with_collision_set), percentage_commits, len(modified_files_set), len(homonimous_modified_files_set), percentage_all_file]
        j = j + 1
        print('Total modified java files: ' + str(modified_java_files_project_count))
        print('Total collisions: ' + str(collisions_in_project_count))
        print('Percentage: ' + str((collisions_in_project_count / modified_java_files_project_count) * 100))
        print('Files with collisions: ')
        for homonimoous_file in homonimous_modified_files_set:
            print(homonimoous_file)
    
    csv_files_with_collisions.to_csv(directory + '/files_with_collisions.csv', index=False)
    csv_project_percentages.to_csv(directory + '/project_percentage.csv', index=False)

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