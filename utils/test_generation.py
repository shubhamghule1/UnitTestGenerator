import ast
from openai import OpenAI
import os

# Ensure that environment variables are loaded
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)

def extract_functions_from_file(file_path: str):
    """Extracts all function names from a Python file."""
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return functions


def extract_functions_from_repo(repo_dir: str):
    """Extracts functions from all Python files in a repository."""
    functions_dict = {}
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                functions = extract_functions_from_file(file_path)
                if functions:
                    functions_dict[file_path] = functions
    return functions_dict


def generate_unit_test(function_name: str, code_snippet: str) -> str:
    """Generates unit test code for a given function."""
    prompt = f"Generate a unit test for the following Python function:\n\n{code_snippet}\n\n# Unit test for {function_name} using unittest."
    system_prompt = (
        "You are a helpful assistant that writes unit tests using the unittest library.\n"
        "You generate only code without explanation.\n"
        "You follow the following template for generating unit tests:\n"
        "1. Import unittest library.\n"
        "2. Define the test class named `Test{FunctionName}`.\n"
        "3. Create at least 3 test methods that cover various cases, including edge cases.\n"
        "4. Include a `main` block to run the tests.\n"
        "You generate consistent responses every time."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    test_code = response.choices[0].message.content
    return test_code


def extract_function_code(function_name: str, code: str) -> str | None:
    """Extracts the code for a specific function from the full source code."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.unparse(node)
    return None
