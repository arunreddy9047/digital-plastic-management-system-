import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "arun_pro"

# Expose names at module level so Vercel's static analyzer finds them.
app = None
application = None

sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "app"))

if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/e_plastic.db")

# Import the Flask app; on failure create a minimal fallback that returns
# the import traceback so logs show the root cause.
try:
    from app.run import app as _imported_app
    app = _imported_app
except Exception as exc:  # pragma: no cover - runtime debug helper
    print("ERROR importing app.run:")
    traceback.print_exc()
    # create a minimal fallback Flask app to expose the error via HTTP
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

# Also expose `application` alias for WSGI-aware tooling
application = app
