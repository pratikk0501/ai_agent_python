from functions.get_files_info import get_files_info, get_file_content, write_file
from functions.run_python import run_python_file

def main():

    print(run_python_file("calculator", "main.py"))
    
    print(run_python_file("calculator", "tests.py"))
    
    print(run_python_file("calculator", "../main.py"))

    print(run_python_file("calculator", "nonexistent.py"))

if __name__ == "__main__":
    main()