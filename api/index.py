import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "arun pro"

sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "app"))

if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/e_plastic.db")

# Import the Flask app; if import fails, provide a debug fallback that logs
# the traceback to stdout (visible in Vercel function logs) and returns
# a simple 500 response so the function doesn't crash silently.
try:
    from app.run import app
except Exception as exc:  # pragma: no cover - runtime debug helper
    print("ERROR importing app.run:")
    traceback.print_exc()
    # create a minimal fallback Flask app to expose the error via HTTP
    try:
        from flask import Flask, Response
        fallback = Flask(__name__)

        @fallback.route("/", defaults={"path": ""})
        @fallback.route("/<path:path>")
        def _import_error(path=""):
            tb = traceback.format_exc()
            body = (
                "ImportError during startup. Check logs for full traceback.\n\n"
                "Exception: {}\n\nTraceback:\n{}".format(repr(exc), tb)
            )
            return Response(body, status=500, mimetype="text/plain")

        app = fallback
    except Exception:
        # If Flask itself isn't available, re-raise the original exception
        raise
