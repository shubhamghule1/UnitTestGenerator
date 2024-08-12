
# Unit Test Generator for Python

This Project Takes GitHub URL as input and Generates Unit Test for each function in the given GitHub Repo.

## Steps to run the Project
- Clone the repo.
- Change Directory to repo directory
- Run 'pip install -r requirements.txt' 
- Create .env file.
- Add OPENAI_API_KEY='<Your_OPENAI_API_KEY>' in .env file.
- run main.py file.


## API Reference

#### Get the form to submit GitHub Repo URL

```http
  GET /
```

Fetches Index page.

#### Post URL and generate tests

```http
  POST /
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `url`      | `string` | **Required**. Valid Github Repo URL. Checks for empty or invalid URLs.|

Returns repo.zip file with unit test for all the functions in the given Github Repo.




## Features
 - Generates a single .zip file with unit tests for all functions, also maintaining the complete heirarchy.
 - Generates 3 test cases for each function covering edge cases.
  - Supports unit test cases for recursive functions.


## Future Scope
- Currently only generates Unit Tests for Python Files. We should extend this to work with other languages too.
- Does not work for functions calling other functions. Because we're defining the function in test file. It does not automatically imports or defines called functions. instead of defining functions we should import the function from original repository.(Haven't Figured out yet)
- Dynamic importing the functions in test files will also reduce LLM output token size and in turn will reduce cost.
- Currently the repo cloning, test repo generation and test zip generation is done in current working directory and it is cleaned after downloading .zip file by client. Better approach would be to perform repo cloning, test generation and test zip generation in virtual directory. Also add a timeout for zip download, after which it will be cleaned automatically in order to save server resources. 
- Add Rate Limiting.
- Add logging for debugging instead of print statements.

