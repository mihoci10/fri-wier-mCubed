# Project Description
This project contains our implemented approaches for data extraction from Assignment 2. 
- _implementation-extraction_ folder contains all of our implemented algorithms for data extraction. _regexWier.py_ contains implementation of algorithm which uses regular expressions, _xpath.py_ contains implementation of algorithm which uses xpath queries, _roadrunner.py_ contains implementation of a roadrunner algorithm. _run-extraction.py_ file is the main entrypoint and runs all of above described algorithms when executed.
- _input-extraction_ folder contains all of our websites data - rtvslo.si, overstock.com and avto.net.

# Run Data Extraction Algorithms
1. Install Python
2. In the _Assignment2_ folder, run command `pip install -r requirements.txt` to install required libraries
3. Go to _implementation-extraction_ folder and run command `python run_extraction.py A` for running RegEx implementation, `python run_extraction.py B` for running XPath implementation or `python run_extraction.py C` for running Roadrunner implementation.
