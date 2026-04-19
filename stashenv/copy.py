"""Copy or rename profiles within a project."""

from stashenv.store import load_profile, save_profile, delete_profile, list_profiles


def copy_profile(project: str, src: str, dst: str, password: str) -> None:
    """Copy src profile to dst within the same project."""
    if src not in list_profiles(project):
        raise KeyError(f"Profile '{src}' does not exist in project '{project}'")
    if dst in list_profiles(project):
        raise ValueError(f"Profile '{dst}' already exists in project '{project}'")

    env = load_profile(project, src, password)
    save_profile(project, dst, env, password)


def rename_profile(project: str, src: str, dst: str, password: str) -> None:
    """Rename src profile to dst within the same project."""
    copy_profile(project, src, dst, password)
    delete_profile(project, src)
