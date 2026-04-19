"""Template support: extract required keys from a .env.template file and check profiles against it."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class TemplateCheckResult:
    missing: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def __str__(self) -> str:
        lines = []
        if self.missing:
            lines.append("Missing keys:")
            for k in self.missing:
                lines.append(f"  - {k}")
        if self.extra:
            lines.append("Extra keys (not in template):")
            for k in self.extra:
                lines.append(f"  + {k}")
        if not lines:
            return "Profile satisfies template."
        return "\n".join(lines)


def parse_template(path: Path) -> list[str]:
    """Return list of required keys from a .env.template file.
    Lines starting with # or blank are ignored.
    Values are ignored — only key names matter.
    """
    keys = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            if key:
                keys.append(key)
    return keys


def check_profile_against_template(
    profile_env: dict[str, str],
    template_keys: list[str],
) -> TemplateCheckResult:
    profile_keys = set(profile_env.keys())
    required = set(template_keys)
    return TemplateCheckResult(
        missing=sorted(required - profile_keys),
        extra=sorted(profile_keys - required),
    )
