import git
from pathlib import Path

def clone_repo(repo_url, target_dir="cloned_repo"):
    target_path = Path(target_dir)

    if target_path.exists() and any(target_path.iterdir()):
        print(f"Skipping clone. Repo already exists at: {target_dir}")
        return

    target_path.mkdir(parents=True, exist_ok=True)

    git.Repo.clone_from(repo_url, target_dir)
    print(f"Repo cloned into: {target_dir}")
