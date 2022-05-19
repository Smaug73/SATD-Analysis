from pydriller import Repository
import argparse
import os
import pandas as pd

def count_collisions(directory):
    accepted_changes = ['MODIFY', 'ADD']
    # Get the name of each project in the directory
    projects = next(os.walk(directory))[1]

    csv_files_with_collisions = pd.DataFrame(columns=['Project', 'Commit', 'File Name']) 
    csv_project_percentages = pd.DataFrame(columns=['Projectß', 'Total Commits', 'Commits with Collisions', 'Percentage Commits with Collisions[%]', 
                                            'Total Java Files Modified', 'Files with Collisions', 'Percentage Files with Collisions[%]'])

    # Index for acessing rows in csv_files_with_collisions DataFrame
    i = 0

    # Index for acessing rows in csv_project_percentages DataFrame
    j = 0

    for project in projects:
        collisions_project = 0
        modified_java_files_project_count = 0
        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + '/' + project))[1]

        print('\nProject: ' + project)

        commits_with_collision_set = set()
        commits_count = 0
        
        for commit in Repository(repository, only_commits=commits).traverse_commits():
            commits_count = commits_count + 1
            modified_java_files_commit_count = 0
            modifications_dict = {}
            files_with_collision_count = 0
            for modified_file in commit.modified_files:
                #print('Change type: ' + modified_file.change_type.name)
                if (modified_file.filename.endswith('.java')) and (modified_file.change_type.name in accepted_changes):
                    modified_java_files_commit_count = modified_java_files_commit_count + 1
                    if modified_file.filename in modifications_dict:
                        commits_with_collision_set.add(commit.hash)
                        files_with_collision_count = files_with_collision_count + 1
                        csv_files_with_collisions.loc[i] = [project, commit.hash, modified_file.filename]
                        i = i + 1
                        #print('COLLISION!')
                        #print(modified_file.new_path)
                        #print(modifications_dict[modified_file.filename])
                    else:
                        modifications_dict[modified_file.filename] = modified_file.new_path

            collisions_commit = modified_java_files_commit_count - len(modifications_dict)
            collisions_project = collisions_project + collisions_commit
            modified_java_files_project_count = modified_java_files_project_count + modified_java_files_commit_count
            '''
            if collisions_commit > 0:
                print('There are ' + str(collisions_commit + 1) + ' modified java files with the same name but different package')
            else:
                print('No collisions found')
            '''
        
        percentage_commits = (len(commits_with_collision_set) / commits_count) * 100
        percentage_file = (collisions_project / modified_java_files_project_count) * 100
        csv_project_percentages.loc[j] = [project, commits_count, len(commits_with_collision_set), percentage_commits, len(commit.modified_files), collisions_project, percentage_file]
        j = j + 1
        print('Total modified java files: ' + str(modified_java_files_project_count))
        print('Total collisions: ' + str(collisions_project))
        print('Percentage: ' + str((collisions_project / modified_java_files_project_count) * 100))
    
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