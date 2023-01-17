1. collision_detector.py -> detects, for each given project, homonymous files changed, added or renamed in the same commit. It requires 2 parameters in input:
   - path to the directory containing all the repositories;
   - list of the projects' names to be analysed.
   
   Es: python collision_detector.py /Users/user/Desktop/Repositories/ -p aries openjpa drill
   
   The output is a CSV file with the following columns: Project, Commit, File, Is PMD Needed. This last column is needed because in the PMD result CSVs the file's package is provided (instead, in the Checkstyle XMLs only the name of the file is provided). That means that reanalysis is necessary (of both files) only if the subpath of homonymous files is the same.
   
   **The result of this script is already present in the folder Results_dataset: homonymous_files.csv. This file was created by concatenating the CSVs of the single projects.**

2. pathConverter.py -> converts the local path of a file (in the column 'File' of the CSV in input) to its path inside the repository. It requires 3 parameters in input:
   - path to the directory containing the PMD results (or converted from XML to CSV Checkstyle results) of all projects;
   - tool used for static analysis ('pmd' or 'checkstyle');
   - list of the projects' names to be analysed.
   
   Es: python pathConverter.py /Users/user/Desktop/PMD_dataset/ -at pmd -p aries openjpa drill
   
   The output is a new CSV file in each commit of every given project, identical to the one in input except for the path of the files in the "File" column.
   
   **This script has already been run for all projects.**
   
3. xmlToCsvConverter.py -> converts the xml format files to csv files.It requires 1 parameter in input:
   - path to the directory containing the Checkstyle results (in XML format) of all projects.
   
   Es: python xmlToCsvConverter.py /Users/user/Desktop/Checkstyle_dataset/
   
   **This script hasn't been run for any project, because it was not actually needed in the following step: counting of the number of warnings per method.**
