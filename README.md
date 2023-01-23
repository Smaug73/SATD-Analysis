# SATD-Analysis

Technical debt is a metaphor to describe the situation where long-term code quality is traded for short-term goals. The presence of this “not quiet-right code yet" is often self-admitted by developers through comments in order to keep track of it and manage it in the future. The TD, therefore, has to do with source code quality, which can be quantified through different indicators such as source code metrics or static analysis warnings.
In this study we investigate to what extent the introduction of self-admitted technical debt is correlated with the presence of static analysis warnings, with source code metrics or with their trends.


In the repo there are 4 directories:
- Preprocessing: contains scripts that fix the already existing PMD and Checkstyle datasets. Specifically, the scripts were used to convert the local path of each analysed file into its repository path, to identify the homonymous files that were changed in the same commit and to redo the static analysis on these files. The result of the homonymous files identification is already present in the Results_dataset folder. 
  In the Preprocessing directory there are also the two tools used for static analysis (PMD and Checkstyle) as well as a subset of the initial dataset, used for testing the scripts described above (Subset_for_tests).
- SATDExtraction: contains the scripts that extract methods and comments in each changed (modified or added) file in every commit of a project, maps the right comments on the right methods and labels each comment as "SATD" or "Not SATD". The jar that does this labeling is already present in the directory. *N.B.: in order to use these scripts, you must download srcML first: https://www.srcml.org.* 
  The output is a CSV file with the following columns: Commit, File, TypeOfChange (indicates whether the comment was added or removed), Signature, Begin--End (the first and the last line of the method), Comment, CommentType ("SATD" or "Not SATD").
- MetricsExtraction: contains scripts that extract, for each method in each modified or added file of each commit in the given projects, 3 source code metrics as well as their trends: NLOC, Number of Parameters, Cyclomatic Complexity.
- CommunitySmell:
