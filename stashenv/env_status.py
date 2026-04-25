"""Report the current stashenv status for a project directory."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from stashenv.pin import get_pinned, is_pinned
from stashenv.history import last_loaded
from stashenv.lock import is_locked
from stashenv.expire import is_expired, get_expiry
from stashenv.store import list_profiles


@dataclass
class EnvStatus:
    project: str
    pinned_profile: Optional[str]
    last_loaded_profile: Optional[str]
    total_profiles: int
    locked_profiles: list = field(default_factory=list)
    expired_profiles: list = field(default_factory=list)
    dotenv_present: bool = False

    def __str__(self) -> str:
        lines = [
            f"Project      : {self.project}",
            f"Profiles     : {self.total_profiles}",
            f"Pinned       : {self.pinned_profile or '(none)'}",
            f"Last loaded  : {self.last_loaded_profile or '(none)'}",
            f".env present : {'yes' if self.dotenv_present else 'no'}",
        ]
        if self.locked_profiles:
            lines.append(f"Locked       : {', '.join(self.locked_profiles)}")
        if self.expired_profiles:
            lines.append(f"Expired      : {', '.join(self.expired_profiles)}")
        return "\n".join(lines)


def get_status(project: str, cwd: Optional[Path] = None) -> EnvStatus:
    """Gather status information for *project*."""
    cwd = cwd or Path.cwd()
    profiles = list_profiles(project)

    locked = [p for p in profiles if is_locked(project, p)]
    expired = [p for p in profiles if is_expired(project, p)]

    pinned = get_pinned(project)
    last = last_loaded(project)
    last_name = last["profile"] if last else None

    dotenv_present = (cwd / ".env").exists()

    return EnvStatus(
        project=project,
        pinned_profile=pinned,
        last_loaded_profile=last_name,
        total_profiles=len(profiles),
        locked_profiles=locked,
        expired_profiles=expired,
        dotenv_present=dotenv_present,
    )
