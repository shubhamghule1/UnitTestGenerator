import os
import shutil

import git
import ast

import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_repo_name_from_url(repo_url):
    """Extracts the repository name from the GitHub URL."""
    path = urlparse(repo_url).path
    return os.path.splitext(os.path.basename(path))[0]

def clone_repo(repo_url):
    repo_name = get_repo_name_from_url(repo_url)
    repo_path = repo_name
    if os.path.exists(repo_path):
        print(f"Repository already exists at {repo_path}. Skipping cloning.")
    else:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned repository to {repo_path}")
    return repo_path

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
    """Generates unit test code for a given function."""
    prompt = f"Generate a unit test for the following Python function:\n\n{code_snippet}\n\n# Unit test for {function_name} using unittest."
    system_prompt = (
        "You are a helpful assistant that writes unit tests using the unittest library.\n"
        "You generate only code without explanation.\n"
        "You follow following template for generating unit tests\n"
        "1. Import unittest library\n"
        "2. Define the given function\n"
        "3. Generate the class\n"
        "4. Add 3 different test cases handling various edge cases\n"
        "5. Provide main class to run the given code\n"
        "Also you generate consistent response every single time.\n"
        "You do not generate ```python at the start and ``` at the end."
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

def extract_function_code(function_name, code):
    """Extracts the code for a specific function from a file."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.unparse(node)
    return None

def delete_file_after_send(file_path: str):
    """Delete the specified file."""
    if os.path.exists(file_path):
        print(f"Deleting {file_path} File")
        os.remove(file_path)

def delete_dir_after_send(file_path: str):
    if os.path.exists(file_path):
        print(f"Deleting {file_path} Directory")
        shutil.rmtree(file_path)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", status_code=201)
async def generate_unit_test_from_URL(request: Request, backgroundTasks: BackgroundTasks):
    try:
        data = await request.json()
        repo_url = data.get('repo_url')
        if not repo_url:
            raise HTTPException(status_code=400, detail="Repository URL is required")

        repo_name = get_repo_name_from_url(repo_url)
        repo_dir = repo_name

        # Remove existing repository directory if it exists
        if os.path.exists(repo_dir):
            print(f"{repo_dir} Exists. Deleting Repo and cloning again")
            shutil.rmtree(repo_dir)
        clone_repo(repo_url)  # Clone the repository

        print("Clone Repo completed Successfully")

        test_dir = f"{repo_name}_tests"
        # Remove existing test directory if it exists
        if os.path.exists(test_dir):
            print(f"{test_dir} Exists. Deleting test directory")
            shutil.rmtree(test_dir)
        os.makedirs(test_dir, exist_ok=True)

        functions = extract_functions_from_repo(repo_dir)
        print("Functions are extracted Successfully")

        function_counts = {}

        for file_path, funcs in functions.items():
            # Create subdirectory structure in the test directory, removing .py extension from the folder name
            relative_path = os.path.relpath(file_path, repo_dir)
            dir_name = os.path.dirname(relative_path)
            file_base_name = os.path.splitext(os.path.basename(file_path))[0]  # Remove .py extension

            # Create a directory for each file inside its respective subfolder
            sub_dir = os.path.join(test_dir, dir_name, file_base_name)
            os.makedirs(sub_dir, exist_ok=True)

            with open(file_path, "r") as file:
                code = file.read()

            for func in funcs:
                if func not in function_counts:
                    function_counts[func] = 0
                function_counts[func] += 1

                func_code_snippet = extract_function_code(func, code)
                if func_code_snippet:
                    test_code = generate_unit_test(func, func_code_snippet)

                    if function_counts[func] > 1:
                        test_file_name = f"{func}_{function_counts[func]}_test.py"
                    else:
                        test_file_name = f"test_{func}_test.py"

                    output_file = os.path.join(sub_dir, test_file_name)
                    with open(output_file, "w") as test_file:
                        test_file.write(f"{test_code.replace('\n', '\n')}\n")
                    print(f"Unit test for {func} written to {output_file}")

        # Create a zip file of the test directory
        zip_file_base_name = os.path.join(os.getcwd(), f"{repo_name}_tests")
        shutil.make_archive(zip_file_base_name, 'zip', test_dir)
        zip_file_path = f"{zip_file_base_name}.zip"

        print(f"All unit tests have been generated and zipped to {zip_file_path}")
        if not os.path.exists(zip_file_path):
            raise HTTPException(status_code=500, detail="Failed to create the zip file")

        # if os.path.exists():
        #     print(f"Deleting {repo_dir} Repo")
        #     shutil.rmtree(repo_dir)
        #


        # Schedule the cleanup task to run in the background
        backgroundTasks.add_task(delete_dir_after_send, repo_dir)
        backgroundTasks.add_task(delete_dir_after_send, test_dir)
        backgroundTasks.add_task(delete_file_after_send, zip_file_path)

        return FileResponse(path=zip_file_path, media_type='application/zip', filename=f"{repo_name}_tests.zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)