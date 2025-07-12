import os
import subprocess

def run_python_file(working_directory, file_path):

    if not os.path.abspath(os.path.join(working_directory, file_path)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(os.path.join(working_directory, file_path)):
        return f'Error: File "{file_path}" not found'

    if not file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file'

    try:
        result = subprocess.run(['python3', os.path.join(working_directory, file_path)], capture_output=True, text=True)
        if result.returncode == 0:
            if not result.stdout:
                return f'No output produced.\nSTDERR: \n{result.stderr}'
            return f'STDOUT: \n{result.stdout}\nSTDERR: \n{result.stderr}'
        else:
            return f'Process exited with code {result.returncode}'
    except Exception as e:
        return f'Error: executing Python file: {e}'