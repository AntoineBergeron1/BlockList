from django.conf import settings
from pathlib import Path


def git_version(request):
    """
    Context processor to add git commit hash to all templates.
    Reads from version.txt file generated at deployment.
    """
    version_file = settings.BASE_DIR / "version.txt"
    try:
        with open(version_file, "r") as f:
            commit_hash = f.read().strip()
    except FileNotFoundError:
        commit_hash = "unknown"

    return {"GIT_COMMIT_HASH": commit_hash}
