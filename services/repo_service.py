import os
import shutil

from fastapi import HTTPException

from utils.git_ops import clone_repo, get_repo_name_from_url
from utils.test_generation import extract_functions_from_repo, generate_unit_test, extract_function_code

def generate_unit_tests(repo_url: str):
    repo_name = get_repo_name_from_url(repo_url)
    repo_dir = clone_repo(repo_url)  # Clone the repository

    test_dir = f"{repo_name}_tests"
    os.makedirs(test_dir, exist_ok=True)

    functions = extract_functions_from_repo(repo_dir)
    print("Functions Extracted Successfully")

    function_counts = {}
    for file_path, funcs in functions.items():
        relative_path = os.path.relpath(file_path, repo_dir)
        dir_name = os.path.dirname(relative_path)
        file_base_name = os.path.splitext(os.path.basename(file_path))[0]

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

    zip_file_base_name = os.path.join(os.getcwd(), f"{repo_name}_tests")
    shutil.make_archive(zip_file_base_name, 'zip', test_dir)
    zip_file_path = f"{zip_file_base_name}.zip"
    print(f"All unit tests have been generated and zipped to {zip_file_path}")
    if not os.path.exists(zip_file_path):
        raise HTTPException(status_code=500, detail="Failed to create the zip file")

    return zip_file_path, repo_dir, test_dir
