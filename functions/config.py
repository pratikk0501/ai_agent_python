def truncate_string(file_path, MAX_CHARS=10000):

    with open(file_path, 'r') as file:
        content = file.read()

    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    
    return content

working_directory = './calculator'  # Default working directory