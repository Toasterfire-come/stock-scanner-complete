# Import tasks only if not in startup phase to avoid database access
import sys

# Only import tasks if we're not in a problematic startup phase
if len(sys.argv) > 1 and sys.argv[1] not in ['test', 'check']:
    try:
        from . import tasks  # forces task registration at import time
    except Exception:
        # If there's any issue importing tasks, skip it
        pass
