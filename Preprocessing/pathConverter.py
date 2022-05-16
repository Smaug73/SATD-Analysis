from pydriller import Repository
import argparse
import os
import pandas as pd


def add_columns_and_convert_paths(directory, tool):

    # Get the name of each project in the directory
    projects = next(os.walk(directory))[1]

    # Traverse all the project directories
    for project in projects:

        # Create the url to the repository
        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + '/' + project))[1]

        print('\nProject: ' + project)

        # Traverse all the commit directories
        for commit in commits:
            print('Commit: ' + commit)

            # Read csv file and convert to a pandas DataFrame
            csv_violations = pd.read_csv(directory + '/' + project + '/' + commit + '/' + tool + '-' + commit + '.csv')

            # Check if there is any entry
            # Add the commit to commit_to_analyse list if there is at least one entry in the csv file
            # Add columns 'Project' and 'Commit' to each CSVs in the directory
            if csv_violations.size != 0:
                csv_violations['Project'] = project
                csv_violations['Commit'] = commit

                # Get the commit from remote repository
                for commit_to_analyse in Repository(repository, single=commit).traverse_commits():
                    print('\nCommit under analysis: ' + commit_to_analyse.hash)

                    # List of paths of the files modified in the current commit
                    modified_files_list= []

                    # Populate the list
                    for modified_file in commit_to_analyse.modified_files:
                        modified_files_list.append(modified_file.new_path)
                        
                    # List with files which path was already converted or that were not modified in the commit under analysis
                    to_exclude = []

                    # Index for accessing the rows of the CSVs
                    i = 0

                    # Iterate over all the files in the csv file
                    for violation_file in csv_violations['File']:

                        # Get the package of the file
                        package = csv_violations.at[i, 'Package']

                        # Replace the character '.' with '/' in order to create the path of the file
                        package = package.replace('.', '/')
                        i = i + 1

                        # Get the name of the file
                        violation_file_name = violation_file.split('/')[-1]

                        # Create the subpath of the file in the CSV
                        violation_file_subpath = package + '/' + violation_file_name

                        # Check whether the file was already searched
                        if not(violation_file_subpath in to_exclude):

                            # Add the file to the to_exclude array
                            to_exclude.append(violation_file_subpath)

                            # Flag: if the file was already found, exit the loop
                            found = False

                            # Look for the file with violations in the list of modified files
                            for modifed_file_path in modified_files_list:
                                if found:
                                    break

                                # Check if the modified file path ends with the violation file subpath
                                if modifed_file_path.endswith(violation_file_subpath):
                                    found = True
                                    # The method replace() updates data occurring multiple number of times
                                    csv_violations['File'] = csv_violations['File'].replace({violation_file: modifed_file_path})
                                    print(violation_file + ' -> ' + modifed_file_path)
                            
                            if not(found):
                                print('File ' + violation_file_name + ' was not modified in this commit')

                    # Save all the changes
                    csv_violations.to_csv(directory + '/' + project + '/' + commit + '/new-' + tool + '-' + commit + '.csv')
            else:
                csv_violations['Project'] = ''
                csv_violations['Commit'] = ''
                csv_violations.to_csv(directory + '/' + project + '/' + commit + '/new-' + tool + '-' + commit + '.csv')

        


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Program for converting file paths')

    # Directory of projects being analysed
    parser.add_argument(
        'directory_projects',
        type=str,
        help='Projects directory',
    )

    # Tool with which the violations were discovered
    # It is needed to build the file path of the CSV to be read/written
    parser.add_argument('-at',
                        '--analysis_tool',
                        type=str,
                        help='Tool that was used to analyse the commits',
                        required=True,
                        choices=['pmd', 'checkstyle']
                        )

    # Parsing the args
    args = parser.parse_args()

    # Projects Directory
    pathProjects = args.directory_projects

    # Analysis tool used
    tool = args.analysis_tool

    add_columns_and_convert_paths(pathProjects, tool)
