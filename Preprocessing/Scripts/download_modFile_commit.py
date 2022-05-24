# Example and alpha version of script for download the modified file of
# a specific commit for a Repository


import os
from pdb import main
import re

from pydriller import Repository






commit_id = "0a1b46ce0d436002e8abf9ae74a7ba7324fe093e"
project = "tinkerpop"

repository = 'https://github.com/apache/' + project

# create the git rep object
git_rep = Repository(repository, single=commit_id).traverse_commits()

print('Commit:', commit_id)

# directory for the commit
dir_commits = "/home/stefano/TesiMagistrale/ProvePydriller/"

# directory for the commit
dir_commit = dir_commits + project + '/' + commit_id

# create the project directory if it does not exist, otherwise skit it
if os.path.isdir(dir_commits + project) is False:
    os.mkdir(dir_commits + project)

# create the commitID directory if it does not exist, otherwise skit it
if os.path.isdir(dir_commit) is False:
    os.mkdir(dir_commit)
# else:
#     # print('No need to save files from commit: ' + commit_id)
#     continue

for commit in git_rep:

    # iterate over each modified file within the commit
    for m in commit.modified_files:

        # only proceed with it is a Java file
        if re.search('\\.java$', m.filename, re.IGNORECASE):

            # print(modified_file.filename)
            # print(modified_file.source_code)

            # save the file
            if m.source_code is not None:

                file = open(dir_commit + '/' + m.filename, "w", encoding="utf-8")
                file.write(m.source_code)
                file.close()

print('Files saved from commit: ' + commit_id)

print('Done downloading files from project:', project)
