import git
from pathlib import Path

def clone_repo(repo_url, target_dir="cloned_repo"):
    target_path = Path(target_dir)

    # Skip if path exists and is not empty
    if target_path.exists() and any(target_path.iterdir()):
        print(f"Skipping clone. Repo already exists at: {target_dir}")
        return

    # Make sure the directory exists
    target_path.mkdir(parents=True, exist_ok=True)

    # Clone the repository
    git.Repo.clone_from(repo_url, target_dir)
    print(f"Repo cloned into: {target_dir}")
