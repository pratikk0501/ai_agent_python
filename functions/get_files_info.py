import os
from functions.config import truncate_string, working_directory
from functions.run_python import run_python_file
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory. If not provided, returns appropriate error.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file in the given file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory. Returns appropriate error for incorrect file paths or non-Python files.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file, creating directories as needed, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory. If the file does not exist, it will be created. If the parent directory does not exist, it will be created as well.",
            ), "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory=None):

    if not os.path.abspath(os.path.join(working_directory,directory)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(os.path.join(working_directory,directory)):
        return f'Error: "{directory}" is not a directory'

    if directory == '.':
        val = 'current'
    else:
        val = f'\'{directory}\''

    message = f'Result for {val} directory:'

    for file in os.listdir(os.path.join(working_directory, directory)):
        file_size = f'\n- {file}: file_size={os.path.getsize(os.path.join(working_directory, directory, file))} bytes'
        is_dir = f', is_dir={os.path.isdir(os.path.join(working_directory, directory, file))}'
        message += file_size + is_dir

    return message

def get_file_content(working_directory, file_path):

    if not os.path.abspath(os.path.join(working_directory, file_path)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(os.path.join(working_directory, file_path)):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    content = truncate_string(os.path.join(working_directory, file_path))

    return content

def write_file(working_directory, file_path, content):
    
    if not os.path.abspath(os.path.join(working_directory, file_path)).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(os.path.dirname(os.path.join(working_directory, file_path))):
        os.makedirs(os.path.join(working_directory, file_path))

    with open(os.path.join(working_directory, file_path), 'w') as file:
        file.write(content)

    # print(os.path.dirname(os.path.join(working_directory, file_path)))

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = function_call_part.args

    args['working_directory'] = working_directory  # Injecting the working directory

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    result = function_map[function_name](**args)

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)
