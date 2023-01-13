Run the script analyzeComments.pl to create SATD CSVs.
The script needs 6 parameters in input:
- path to the repo to analyze
- path to the working directory (the one containing the other 2 scripts extractSignatures.pl and extractComments.pl)
- path to srcML's bin directory (es: usr/bin/srcML/bin)
- complete path to the extractSignatures.pl script
- complete path to the extractComments.pl script
- path to the SATDDetector jar

Before running the script, it's important to create a directory in the working directory called "temporary".
In the "temporary" directory create 2 other empty directories: "current" and "previous".

When running the analyzeComments.pl script, don't forget to specify the name of the output file.

Es:
perl analyzeComments.pl 
/Users/user/Desktop/Repositories/pdfbox/ 
/Users/user/Desktop/SATD-Analysis/SATDExtraction/Scripts/ 
/usr/local/bin 
/Users/user/Desktop/SATD-Analysis/SATDExtraction/Scripts/extractSignatures.pl 
/Users/user/Desktop/SATD-Analysis/SATDExtraction/Scripts/extractComments.pl 
/Users/user/Desktop/SATD-Analysis/SATDExtraction/Scripts/satd_detector.core-1.0.0-jar-with-dependencies.jar >> pdfboxComments.csv 

If you don't want to use SATDDetector to identify the SATD comments, run the script analyzeComments-NO-JAR.pl: it will label as "SATD" only the comments
containing the key words "TODO", "FIXME" and "XXX".
