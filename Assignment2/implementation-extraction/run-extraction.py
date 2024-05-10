# starting point of the extraction - run implementations based on selected choice
import sys
import re
import json
import regexWier


def extract_with_algorithm_a():
    regexWier.extract_with_regex()
    input("Press enter to exit")

def extract_with_algorithm_b():
    return "Data extracted with Algorithm B"


def extract_with_algorithm_c():
    return "Data extracted with Algorithm C"


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