# stashenv

> CLI tool to securely store and switch between named `.env` profiles per project

---

## Installation

```bash
pip install stashenv
```

---

## Usage

Initialize stashenv in your project directory, save your current `.env` as a named profile, and switch between profiles as needed.

```bash
# Save current .env as a profile
stashenv save production

# List available profiles
stashenv list

# Switch to a different profile
stashenv use staging

# Delete a profile
stashenv delete old-profile
```

Profiles are encrypted and stored locally under `~/.stashenv/`.

---

## Commands

| Command | Description |
|---|---|
| `stashenv save <name>` | Save current `.env` as a named profile |
| `stashenv use <name>` | Switch active `.env` to a saved profile |
| `stashenv list` | List all saved profiles for the project |
| `stashenv delete <name>` | Remove a saved profile |
| `stashenv show <name>` | Print a profile's contents to stdout |

---

## License

MIT © stashenv contributors