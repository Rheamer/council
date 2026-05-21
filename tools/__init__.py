"""Tools available to the decision-support agent.

Only the task manager ships as a code API, because its design point is
*sequential / hierarchical* tool calling (list tasks, then fetch subtasks
per task):

    - tasker: task manager API

The rest of the user's data is plain files under ``data/`` -- read them
however you like (open the markdown, load the JSON):

    - data/user_kb.md      structured dossier on the user
    - data/notes.json      ~30 personal notes (mostly noise)
    - data/corpus/*.md     reference articles / saved posts
"""

from . import tasker

__all__ = ["tasker"]
