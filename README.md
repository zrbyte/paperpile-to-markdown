# paperpile-to-markdown
Convert Paperpile JSON exports to individual Markdown files for use in my
Obsidian vault.

## Usage

```
python pp2md.py path/to/export.json
```

If no path is supplied the script looks for a ``*.json`` file next to itself.

### macOS Quick Action

The script can be used from a macOS Quick Action by passing the selected
JSON file as an argument. The generated markdown files are written next to the
source JSON file so they appear in the same folder after the action finishes.
