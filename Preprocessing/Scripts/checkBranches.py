from pydriller import Repository
import os
import argparse
import pandas as pd

# Create a csv with 3 columns:
# Project
# Branch
# Number of commits in that branch
def check_branches(directory):

    projects = next(os.walk(directory))[1]

    csv_branches = pd.DataFrame(columns=['Project', 'Branch', 'Commits Count'])
    
    i = 0
    for project in projects:
        repository = 'https://github.com/apache/' + project

        commits = next(os.walk(directory + os.sep + project))[1]

        print('Project: ' + project)
        
        # Traverse only the commits in the directory
        commits_repo = Repository(repository, only_commits=commits).traverse_commits()

        # Dictionary:
        # Key: branch
        # Value: number of commits in the branch
        branches_dict = {}
        for commit in commits_repo:
            for branch in commit.branches:
                if branch in branches_dict:
                    branches_dict[branch] = branches_dict[branch] + 1
                else:
                    branches_dict[branch] = 1
        
        for br in branches_dict: 
            csv_branches.loc[i] = [project, br, branches_dict[br]]
            i = i + 1
    
    # Save the csv file in the repository directory          
    csv_branches.to_csv(directory + os.sep + 'csv_branches.csv')





if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for check the branches of all commits in the directory')

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

    
    check_branches(pathProjects)