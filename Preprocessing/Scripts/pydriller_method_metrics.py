from pydriller import Repository
import pandas as pd
import argparse
import os


# Computes, on each modified file in each commit, method level metrics provided by pydriller:
# parameters, nloc, complexity.
# Fan in and fan out are not computed correctly by pydriller.
def calc_metrics(directory, projects):
    for project in projects:
        csv_pydriller_metrics = pd.DataFrame(columns=['Project', 'Commit', 'File', 'Method', 'Start', 'End', 'Parameters', 'Num_Parameters', 'NLOC', 'Complexity', 'Change_type'])
        
        repository = 'https://github.com/apache/' + project

        # Get the hash of each commit in the project directory
        commits = next(os.walk(directory + os.sep + project))[1]

        print('\nProject: ' + project)
        print('Number of commits: ' + str(len(commits)))

        num_commits = str(len(commits))
        commit_count = 1

        for commit in Repository(repository, only_commits=commits).traverse_commits():
            print('Commit: ' + commit.hash + ' ' + str(commit_count) + '/' + num_commits)
            commit_count = commit_count + 1
            for f in commit.modified_files:
                if f.filename.endswith('.java'):
                    
                    for m in f.methods:
                        new_row = pd.DataFrame({'Project': [project], 'Commit': [commit.hash], 'File': [f.new_path], 
                                                'Method': [m.long_name], 'Start': [m.start_line], 'End': [m.end_line],
                                                'Parameters': [m.parameters], 'Num_Parameters': [len(m.parameters)],
                                                'NLOC': [m.nloc], 'Complexity' : [m.complexity], 'Change_type': [f.change_type.name]})
                        csv_pydriller_metrics = pd.concat([csv_pydriller_metrics, new_row], ignore_index=True, sort=False)
                        csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_' + project + '.csv', index=False)


def calc_metrics_file(directory, project, commit_hash, file, csv_pydriller_metrics, change_type):            
    for m in file.methods:
        new_row = pd.DataFrame({'Project': [project], 'Commit': [commit_hash], 'File': [file.new_path], 
                                'Method': [m.long_name], 'Start': [m.start_line], 'End': [m.end_line],
                                'Parameters': [m.parameters], 'Num_Parameters': [len(m.parameters)], 'NLOC': [m.nloc], 'Complexity' : [m.complexity],
                                'Change_type': [change_type]})
        csv_pydriller_metrics = pd.concat([csv_pydriller_metrics, new_row], ignore_index=True, sort=False)
        #csv_pydriller_metrics.to_csv(directory + os.sep + 'pydriller_metrics_' + project + '.csv', index=False)
        return pd.DataFrame(csv_pydriller_metrics)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
    description='Program for compute pydriller metrics on method level in modified files: nloc, complexity, parameters')

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
    
    calc_metrics(pathProjects, projects)