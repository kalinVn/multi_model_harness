INSTRUCTIONS = (
    "Create a concise, ordered execution plan for the provided task. "
    "Use read_file only to inspect relevant project context. "
    "Use list_directory to inspect the existing files in .caisa/plans. "
    "Find the highest number at the end of an existing plan file name and use the next number, starting with 1. "
    "Create exactly one Markdown file named plan-<task-name>-<number>.md under .caisa/plans. "
    "Use a short lowercase kebab-case task name and include a task summary followed by the ordered plan. "
    "Do not write outside .caisa/plans, modify project files, execute the plan, or invent information. "
    "Return the plan file path and a concise summary."
)
