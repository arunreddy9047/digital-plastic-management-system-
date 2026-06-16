from functools import wraps

from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user

from app.i18n import translate


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if current_user.is_admin():
            return view_func(*args, **kwargs)

        message = translate("admin_access_only")
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"message": message}), 403

        flash(message)
        return redirect(url_for("data.index"))

    return wrapped_view
