#!/usr/bin/env python3
#SBATCH --partition=mcs.default.q
#SBATCH --output=clone_%j.out

from git import Repo
import argparse
import os

def clone(directory, output_dir):
    projects = next(os.walk(directory))[1]
    
    tot_projects = 50
    count_projects = 1

    for project in projects:
        print('\nCloning project ' + project + ' (' + str(count_projects) + '/' + str(tot_projects) +  ') ...')
        count_projects = count_projects + 1

        git_url = 'https://github.com/apache/' + project + '.git'
        repo_dir = output_dir + os.sep + project

        if(os.path.isdir(repo_dir) is False):
            Repo.clone_from(git_url, repo_dir)
            print(project + ' cloned succefully!')
        else:
            print(project + ' already cloned')




if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for tracing renamed files and computing level-method metrics on changed and added files')

    # Path to projects
    parser.add_argument(
        'directory_projects',
        type=str,
        help='Projects directory',
    )

    parser.add_argument(
        '-o',
        '--repo_dir',
        type=str,
        help='Path to the directory with all the repos',
        required=True
    )

    # Parsing the args
    args = parser.parse_args()

    # Repos Directory
    pathProjects = args.directory_projects

    output_dir= args.repo_dir
    
    clone(pathProjects, output_dir)