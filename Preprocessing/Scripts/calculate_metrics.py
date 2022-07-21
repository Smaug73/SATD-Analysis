from pydriller import Repository
from git import Repo
import datetime
import pandas as pd
import argparse
import os


def traverse_commits(directory, projects):
    for project in projects:

        path_repo = directory + os.sep + project

        repo = Repo(path_repo)
        main = repo.heads[0]

        print('\nProject: ' + project)
        print('Main branch: ' + main.name + '\n')

        commits = set()
        branches = []
        remote_refs = repo.remote().refs

        #print('\nTutti:')
        #for ref in repo.references:
        #    print(ref.name)

        print('\nBranches:')
        for ref in remote_refs:
        #for ref in repo.references:
            #branches.append(ref.name.lstrip('origin/'))
            if ref.name != 'origin/HEAD':
                if ref.name.split('/')[-1] == main.name:
                    main = ref
                else:
                    branches.append(ref.name)
                print(ref.name)
            for comm in repo.iter_commits(rev=ref.name):
                commits.add(comm)
        tot_commits = len(commits)

        start_time = datetime.datetime.now()

        commits_analysed = set()
        rows = []

        print('\nBranch: ' + main.name)
        rm = Repository(path_repo, only_no_merge=False, only_in_branch=main)

        measure(rm, commits_analysed, tot_commits, rows)



        for br in branches:
            print('\nBranch: ' + br)
            rm = Repository(path_repo, only_no_merge=False, only_in_branch=br)
            
            measure(rm, commits_analysed, tot_commits, rows)

                
        csv_pydriller_metrics = pd.DataFrame(rows, columns=['Project', 'Commit', 'File', 'Method', 'Begin--End', 'Parameters', '#Parameters', 'NLOC', 'Complexity'])
        csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_'+ project + '.csv', index=False)


        print('\nProject: ' + project)
        print('Main branch: ' + main.name)
        print('Other branches: ' + str(branches))
        print('Start: ' + datetime.date.strftime(start_time, "%m/%d/%Y, %H:%M:%S"))
        end_time = datetime.datetime.now()
        print('End: ' + datetime.date.strftime(end_time, "%m/%d/%Y, %H:%M:%S"))
        duration = end_time - start_time
        seconds_in_day = 24 * 60 * 60
        duration_tuple = divmod(duration.days * seconds_in_day + duration.seconds, 60)
        print('The measurement for project ' + project + ' lasted: ' + str(duration_tuple[0]) + ' minutes and ' + str(duration_tuple[1]) + ' seconds')
        #print('Number of commits: ' + str(count_commits))



def measure(repository, commits_analysed, tot_commits, rows):

    for commit in repository.traverse_commits():
        if commit.hash in commits_analysed:
            continue

        commits_analysed.add(commit.hash)
        print('Commit: ' + commit.hash + ' (' + str(len(commits_analysed)) + '/' + str(tot_commits) + ')')
        #print('Branches: ' + str(commit.branches))

        for f in commit.modified_files:
            #print("File: ",f.filename)
            if f.filename.endswith('.java') and (f.change_type.name == 'ADD' or f.change_type.name == 'MODIFY'):
                for m in f.methods:
                    new_row = [commit.project_name, commit.hash, f.new_path, m.long_name, str(m.start_line) + '--' + str(m.end_line), m.parameters, len(m.parameters), m.nloc, m.complexity]
                    rows.append(new_row)







if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for computing level-method metrics on changed and added files')

    # Path to repos of projects being analysed
    parser.add_argument(
        'directory_repos',
        type=str,
        help='Repos directory',
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

    projects = args.projects_to_analyse
    
    traverse_commits(pathProjects, projects)