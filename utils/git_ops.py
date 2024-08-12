import os
from urllib.parse import urlparse
import git

def get_repo_name_from_url(repo_url: str) -> str:
    """Extract the repository name from the GitHub URL."""
    path = urlparse(repo_url).path
    return os.path.splitext(os.path.basename(path))[0]

def clone_repo(repo_url: str) -> str:
    repo_name = get_repo_name_from_url(repo_url)
    repo_path = repo_name
    if os.path.exists(repo_path):
        print(f"Repository already exists at {repo_path}. Skipping cloning.")
    else:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned repository to {repo_path}")
    return repo_path
