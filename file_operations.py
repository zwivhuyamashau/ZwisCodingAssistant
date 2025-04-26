import os
from pathlib import Path
from typing import Optional
import difflib
import hashlib

class FileOperationError(Exception):
    """Custom exception for file operation errors"""
    pass

class RepoFileManager:
    def __init__(self, repo_base_path: str = None):
        if repo_base_path is None:
            repo_base_path = os.getcwd()

        self.repo_base_path = os.path.abspath(repo_base_path)
        if not os.path.exists(self.repo_base_path):
            raise FileOperationError(f"Repository path does not exist: {self.repo_base_path}")
        if not os.path.isdir(self.repo_base_path):
            raise FileOperationError(f"Repository path is not a directory: {self.repo_base_path}")

        print(f"File operations initialized with base path: {self.repo_base_path}")

    def get_absolute_path(self, file_path: str) -> str:
        # If path is already absolute, use it directly
        if os.path.isabs(file_path):
            abs_path = os.path.normpath(file_path)
        else:
            # If path is relative, make it relative to repo base path
            abs_path = os.path.normpath(os.path.join(self.repo_base_path, file_path))

        return abs_path

    def validate_path(self, file_path: str) -> str:
        abs_path = self.get_absolute_path(file_path)

        # Check if path is within repository
        if not abs_path.startswith(self.repo_base_path):
            raise FileOperationError(
                f"File path must be within repository:\n"
                f"File path (absolute): {abs_path}\n"
                f"Repository base: {self.repo_base_path}"
            )

        # Check for suspicious path components
        path_parts = Path(abs_path).parts
        suspicious = [part for part in path_parts if part.startswith('.') and part != '.']
        if suspicious:
            raise FileOperationError(
                f"Suspicious path components found: {suspicious}"
            )

        return abs_path

    def safe_write_to_file(self, file_path: str, content: str) -> bool:
        """
        Safely write content to a file within the repository.

        - Validates the path
        - Creates parent directories if needed
        - Shows a diff if the file already exists
        - Handles encoding issues
        - Prevents accidental writes to critical system files

        Args:
            file_path: Path to the file (absolute or relative to repo)
            content: Content to write to the file

        Returns:
            bool: True if write was successful

        Raises:
            FileOperationError: If write operation cannot be performed safely
        """
        try:
            # Validate and normalize path
            abs_path = self.validate_path(file_path)

            # Additional safety checks for critical files
            if any(keyword in abs_path.lower() for keyword in [
                'passwd', 'shadow', 'hosts', 'sudoers', '.ssh', '.aws',
                '.env', 'credential', '.git', '.github'
            ]):
                raise FileOperationError(f"Cannot modify potentially sensitive file: {abs_path}")

            # Check if this would overwrite an existing file
            existing_content = None
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()

                    # If content is identical, no need to write
                    if existing_content == content:
                        print(f" No changes needed for file: {abs_path}")
                        return True

                    # Generate and log the diff
                    diff = difflib.unified_diff(
                        existing_content.splitlines(keepends=True),
                        content.splitlines(keepends=True),
                        fromfile=f"a/{os.path.basename(abs_path)}",
                        tofile=f"b/{os.path.basename(abs_path)}"
                    )
                    print(f"\nChanges for {abs_path}:\n{''.join(diff)}")
                except UnicodeDecodeError:
                    # If we can't read the existing file as text, just note that we'll overwrite binary
                    print(f" Warning: Overwriting possibly binary file: {abs_path}")

            # Create directory if it doesn't exist
            directory = os.path.dirname(abs_path)
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)

            # Write the content to the file
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Generate file hash for verification
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            print(f" Successfully wrote to file: {abs_path} (MD5: {content_hash})")
            return True

        except FileOperationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Error writing to file {file_path}: {str(e)}")

    def read_file(self, file_path: str) -> Optional[str]:
        try:
            # Validate and normalize path
            abs_path = self.validate_path(file_path)

            # Read and return file content
            with open(abs_path, 'r') as f:
                return f.read()

        except FileOperationError:
            raise
        except FileNotFoundError:
            return None
        except Exception as e:
                return f.read()

        except FileOperationError:
            raise
        except FileNotFoundError:
            return None
        except Exception as e:
            raise FileOperationError(f"Error reading file {file_path}: {str(e)}")

    def is_file_in_repo(self, file_path: str) -> bool:
        try:
            self.validate_path(file_path)
            return True
        except FileOperationError:
            return False

    def get_relative_path(self, abs_path: str) -> str:
        try:
            return os.path.relpath(abs_path, self.repo_base_path)
        except ValueError:
            return abs_path
