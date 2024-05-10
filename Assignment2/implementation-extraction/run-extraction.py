# starting point of the extraction - run implementations based on selected choice
import sys
import re
import json
import regexWier
import xpath
import roadrunner


def extract_with_algorithm_a():
    regexWier.extract_with_regex()
    input("Press enter to exit")

def extract_with_algorithm_b():
    xpath.extract_with_xpath()
    input("Press enter to exit")


def extract_with_algorithm_c():
    roadrunner.wrapper_with_roadrunner()
    input("Press enter to exit")


def main():

    if len(sys.argv) != 2:
        print("Usage: python run-extraction.py <algorithm>")
        sys.exit(1)
    
    algorithm = sys.argv[1]

    if algorithm == 'A':
        result = extract_with_algorithm_a()
    elif algorithm == 'B':
        result = extract_with_algorithm_b()
    elif algorithm == 'C':
        result = extract_with_algorithm_c()
    else:
        print("Invalid algorithm. Use A, B, or C.")
        sys.exit(1)
    
    print(result)

    input("Press Enter to close...") 


if __name__ == "__main__":
    main()