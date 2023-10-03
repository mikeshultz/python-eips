from pathlib import Path

from dulwich.porcelain import clone, fetch, pull
from dulwich.repo import Repo

from eips.object import CommitHash

ENCODING = "utf8"
HEAD = b"HEAD"


def is_dir_repo(repo_path: Path) -> bool:
    return repo_path.joinpath(".git").is_dir()


def git_rev(repo_path: Path) -> CommitHash:
    """Get the current revision/commit for the repo"""
    return CommitHash(Repo(str(repo_path)).refs[HEAD].decode(ENCODING))


def ensure_repo(repo_path: Path, repo_uri: str) -> bool:
    """Make sure a repo has been cloned from uri to path.

    Returns if a repo has been newly cloned"""
    if is_dir_repo(repo_path):
        return False
    else:
        repo_path.mkdir(mode=0o750, parents=True)

    clone(repo_uri, target=repo_path)

    if not is_dir_repo(repo_path):
        raise FileNotFoundError(f"Cloned repo not found at {repo_path}")

    return True


def ensure_repo_updated(repo_path: Path, repo_uri: str) -> CommitHash:
    cloned = ensure_repo(repo_path, repo_uri)

    if not cloned:
        pull(repo_path)

    return git_rev(repo_path)
