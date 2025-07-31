# paperpile-to-markdown
Convert Paperpile JSON exports to individual Markdown files for use in my
Obsidian vault.

## Usage

```
python pp2md.py path/to/export.json
```

If no path is supplied the script looks for a ``*.json`` file next to itself.

### macOS Quick Action

The script can be used from a macOS Quick Action by passing the selected JSON
file as an argument. The generated markdown files are written next to the
source JSON file so they appear in the same folder after the action finishes.

#### Setting up the Quick Action

1. Copy ``quickaction.sh`` somewhere on your ``$PATH`` and make it executable.
2. Open **Automator** and create a new **Quick Action**.
3. Configure the action to receive ``files or folders`` in **Finder** and set it
   to ``pass input as arguments``.
4. Add a **Run Shell Script** step containing the full path to ``quickaction.sh``.
5. Set the shell to either ``/bin/zsh`` or ``/bin/bash``.
6. Save the workflow (e.g. *Paperpile to Markdown*). Now you can right-click any
   Paperpile JSON export and run the Quick Action to create the Markdown files
   next to it. The helper script accepts file paths as arguments or via
   ``stdin`` so it works with either Automator setting.
