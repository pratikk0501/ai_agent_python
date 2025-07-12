import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import (
    schema_get_files_info, schema_get_file_content, 
    schema_run_python_file, schema_write_file, call_function,
    )

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    user_prompt = sys.argv[1]
    messages = [types.Content(role="user",
                parts=[types.Part(text=user_prompt)]),
                ]
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    for _ in range(20):

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools = [available_functions],
                system_instruction=system_prompt,
                ),
            )

        if not response.candidates or not response.candidates[0].content.parts:
            raise Exception("No response generated, exiting.")

        if not response.candidates[0].content.parts[0].text:
            break

        print(response.candidates[0].content.parts[0].text)

        for candidate in response.candidates:
            if candidate.content.parts[0].function_call:
                function_call_part = candidate.content.parts[0].function_call
                result = call_function(function_call_part, verbose=True)
                if not result.parts or not result.parts[0].function_response:
                    raise Exception("Empty function call result")
                messages.append(
                    types.Content(
                        role="tool",
                        parts=result.parts[0].function_response.response,
                    )
                )

        messages.append(
            types.Content(
                role="tool",
                parts=response.candidates[0].content.parts,
            )
        )

    # function_call_part = types.FunctionCall(
    #     name=response.candidates[0].content.parts[0].function_call.name,
    #     args=response.candidates[0].content.parts[0].function_call.args,
    #     )

    # if len(sys.argv) > 2 and sys.argv[2] == '--verbose':
    #     result = call_function(function_call_part, verbose=True)
    #     if (
    #         not result.parts
    #         or not result.parts[0].function_response
    #     ):
    #         raise Exception("empty function call result")
    #     print(f"-> {result.parts[0].function_response.response}")
        
    #     if not result:
    #         raise Exception("no function responses generated, exiting.")

if __name__ == "__main__":
    main()