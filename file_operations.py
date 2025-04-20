import os
from pathlib import Path
from typing import Optional

class FileOperationError(Exception):
    """Custom exception for file operation errors"""
    pass

class RepoFileManager:
    def __init__(self, repo_base_path: str = None):
        """
        Initialize with the base path of the git repository.
        If no path is provided, uses current working directory.

        Args:
            repo_base_path: Absolute or relative path to the git repository
        """
        if repo_base_path is None:
            repo_base_path = os.getcwd()

        self.repo_base_path = os.path.abspath(repo_base_path)
        if not os.path.exists(self.repo_base_path):
            raise FileOperationError(f"Repository path does not exist: {self.repo_base_path}")
        if not os.path.isdir(self.repo_base_path):
            raise FileOperationError(f"Repository path is not a directory: {self.repo_base_path}")

        print(f"File operations initialized with base path: {self.repo_base_path}")

    def get_absolute_path(self, file_path: str) -> str:
        """
        Convert a relative or absolute path to an absolute path within the repository.

        Args:
            file_path: Relative or absolute path to convert

        Returns:
            str: Normalized absolute path
        """
        # If path is already absolute, use it directly
        if os.path.isabs(file_path):
            abs_path = os.path.normpath(file_path)
        else:
            # If path is relative, make it relative to repo base path
            abs_path = os.path.normpath(os.path.join(self.repo_base_path, file_path))

        return abs_path

    def validate_path(self, file_path: str) -> str:
        """
        Validate and normalize the file path to ensure it's within the repository.

        Args:
            file_path: Path to validate

        Returns:
            str: Normalized absolute path

        Raises:
            FileOperationError: If path is outside repository or contains invalid characters
        """
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

        Args:
            file_path: Absolute or relative path to the file to write
            content: Content to write to the file

        Returns:
            bool: True if write was successful

        Raises:
            FileOperationError: If path validation fails or write fails
        """
        try:
            # Validate and normalize path
            abs_path = self.validate_path(file_path)

            # Create directory if it doesn't exist
            directory = os.path.dirname(abs_path)
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)

            # Write the content to the file
            with open(abs_path, 'w') as f:
                f.write(content)

            print(f"✓ Successfully wrote to file: {abs_path}")
            return True

        except FileOperationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Error writing to file {file_path}: {str(e)}")

    def read_file(self, file_path: str) -> Optional[str]:
        """
        Read content from a file within the repository.

        Args:
            file_path: Absolute or relative path to the file to read

        Returns:
            str: Content of the file or None if file doesn't exist

        Raises:
            FileOperationError: If path validation fails or read fails
        """
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
            raise FileOperationError(f"Error reading file {file_path}: {str(e)}")

    def is_file_in_repo(self, file_path: str) -> bool:
        """
        Check if a file path is within the repository directory.

        Args:
            file_path: Absolute or relative path to check

        Returns:
            bool: True if path is within repository
        """
        try:
            self.validate_path(file_path)
            return True
        except FileOperationError:
            return False

    def get_relative_path(self, abs_path: str) -> str:
        """
        Convert an absolute path to a path relative to the repository root.

        Args:
            abs_path: Absolute path to convert

        Returns:
            str: Path relative to repository root
        """
        try:
            return os.path.relpath(abs_path, self.repo_base_path)
        except ValueError:
            return abs_path
