from pydriller import Repository
import argparse
import os
import pandas as pd

# The method adds columns "Project" and "Commit" to each CSV
# and converts the paths in the column "File" from local path to repository path.
# In order to do that, the name of the file taken from the local path is compared with
# modified files (added, changed or renamed) in the current commit. When there's a match, 
# the absolute local path is overwritten with the repository path.
# For checkstyle only the name of the file is used.
# For PMD the package of the file is used too, in order to create a subpath of the file.
# This is possible because in PMD results there is a reference to the package of the file analysed,
# whereas in checkstyle results the only given information is the name of the file.
# If there are 2 or more homonimous files, it is impossible to say to which file the checkstyle results
# (or PMD if the subpath is also the same) are referring to.
def add_columns_and_convert_paths(directory, tool):

    # Get the name of each project in the directory
    projects = next(os.walk(directory))[1]

    for project in projects:
        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + '/' + project))[1]

        print('\nProject: ' + project)

        commit_count = 1

        for commit in commits:
            print('\nCommit: ' + commit + ' ' + str(commit_count) + '/' + str(len(commits)))
            commit_count = commit_count + 1

            csv_violations = pd.read_csv(directory + '/' + project + '/' + commit + '/' + tool + '-' + commit + '.csv')

            # Check if there is any entry
            # If there is at least one entry in the CSV, use PyDriller to get the original path of each file in the CSV
            # Add columns 'Project' and 'Commit' to each CSVs in the directory
            if csv_violations.size != 0:
                csv_violations['Project'] = project
                csv_violations['Commit'] = commit

                for commit_to_analyse in Repository(repository, single=commit).traverse_commits():
                    modified_files_list= []

                    # Only added or modified files are taken into account 
                    # (renamed too, not because they're needed but because in the CSV there are
                    # files which were renamed in the commit)
                    accepted_changes = ['MODIFY', 'ADD', 'RENAME']

                    for modified_file in commit_to_analyse.modified_files:
                        if(modified_file.change_type.name in accepted_changes):
                            modified_files_list.append(modified_file.new_path)
                        
                    # List with files which path was already converted or that were not modified in the commit under analysis
                    to_exclude = []

                    # Index for accessing the rows of the CSVs
                    i = 0

                    for violation_file in csv_violations['File']:

                        # Get the name of the file
                        violation_file_name = violation_file.split('/')[-1]

                        # If there is a column "Package" in the CSV, use it to create the subpath of the file.
                        # If there's no column "Package" or if the field is empty, use just the name of the file
                        try:
                            package = csv_violations.at[i, 'Package']
                            i = i + 1
                            
                            # Create the subpath of the file in the CSV
                            package = package.replace('.', '/')
                            violation_file_subpath = package + '/' + violation_file_name
                        except:
                            violation_file_subpath = violation_file_name

                        if not(violation_file_subpath in to_exclude):
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
                                
            else:
                csv_violations['Project'] = ''
                csv_violations['Commit'] = ''

            csv_violations.to_csv(directory + '/' + project + '/' + commit + '/new-' + tool + '-' + commit + '.csv', index=False)
        

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
