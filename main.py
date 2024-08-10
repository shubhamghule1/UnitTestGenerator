import os
import git
import ast
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)

def get_repo_name_from_url(repo_url):
    """Extracts the repository name from the GitHub URL."""
    path = urlparse(repo_url).path
    return os.path.splitext(os.path.basename(path))[0]

def clone_repo(repo_url):
    repo_name = get_repo_name_from_url(repo_url)
    if os.path.exists(repo_name):
        print(f"Repository already exists at {repo_name}. Skipping cloning.")
    else:
        git.Repo.clone_from(repo_url, repo_name)
        print(f"Cloned repository to {repo_name}")
    return repo_name

def extract_functions_from_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return functions


def extract_functions_from_repo(repo_dir):
    functions_dict = {}
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                functions = extract_functions_from_file(file_path)
                if functions:
                    functions_dict[file_path] = functions
    return functions_dict


def generate_unit_test(function_name, code_snippet):
    print(f"Function name: {function_name}, code: {code_snippet}")
    prompt = f"Generate a unit test for the following Python function:\n\n{code_snippet}\n\n# Unit test for {function_name}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes unit tests."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    return response.choices[0].message['content']


def main(repo_url):
    repo_dir = clone_repo(repo_url)
    print("Clone Repo completed Successfully")
    functions = extract_functions_from_repo(repo_dir)
    print("Functions are extracted Successfully")
    print(functions)

    for file_path, funcs in functions.items():
        with open(file_path, "r") as file:
            code = file.read()
            for func in funcs:
                func_code_snippet = extract_function_code(func, code)
                # print("function name {} : code {}".format(func, func_code_snippet))
                if func_code_snippet:
                    test_code = generate_unit_test(func, func_code_snippet)
                    print(f"Unit test for {func}:\n{test_code}\n")


def extract_function_code(function_name, code):
    """Extracts the code for a specific function from a file."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.unparse(node)
    return None


if __name__ == "__main__":
    repo_url = "https://github.com/MohammadGhnim/python-basics.git"
    main(repo_url)
