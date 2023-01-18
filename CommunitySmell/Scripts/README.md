There are the list of all the script used for the thesis.

NOTE:  Read or launch the scripts for know what is the input and output.




COMMUNITY SMELLS ANALYSIS:

1- To create all the configuration files needed by kaiaulu with this script:

    configuration_builder.py :                      Script for the create the configuration file needed by the 
                                                    community smell script from kaiaulu.

2- To download the mbox files:

    download_mbox_apacheproject.py :                Script for download mbox files of a specific apache project


3- Launch, for all the project selected, the script for the CommunitySmells analysis:

    fixFromKaiaulu/automate_community_smell_calculate.R

    NOTE:   This script is the final version with several fix for the analysis, in particular for the read of mbox 
            and jira json files used. Often the single analysis need a particular tooning of the script.




WARNING COUNTING:

    checkstyle_pmd_warnings_counter.py  :           Counts the numbers of pmd and checkstyle warning
                                                    at methode level for all the files modified in a 
                                                    commit. Return a single dataset for a project. 




DATASET MERGE AND DATA AGGREGATION:

    communitysmell_pydriller_mergedataset.py :      Script for merge CommunitySmells dataset with 
                                                    pydriller-slope-warning dataset

    merge_dataset_with_SATD.py :                    Script for merge SATD dataset with pydriller-slope-warning 
                                                    dataset

    satd_num_communitysmells_dataset.py :           Script for create dataset with number of SATD added in each 
                                                    period of dataset of CommunitySmells
    
    communitysmells_satd_analysis.py :              Script for the creation of the descriptive analysis
                                                    of the CommunitySmells-SATD dataset