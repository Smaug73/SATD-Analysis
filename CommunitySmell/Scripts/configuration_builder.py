'''

Script for the create the configuration file needed by the 
community smell script from kaiaulu.
Only the information necessary for community smell computing is 
insert in the file.

Information needed:
    
    apache project name
    git repository path
    git branch (only main/master branch is considered)
        *controllare se c'e' un master branch o il main branch*
    
    start commit
    end commit
    window size
    
    mbox file path
    
    jira issue comments path


'''



import yaml
import argparse
import subprocess as subprocess
import os








if __name__ == "__main__":
    
    # Args : directory of projects
    parser = argparse.ArgumentParser(
    description='Script for download mbox file for an apache project')

    # Apache roject name
    parser.add_argument(
        'project_name',
        type=str,
        help='Apache projects name',
    )