import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from detection import detect_cheating

app = Flask(__name__)
app.secret_key = "super_secret_key"

warnings_store = {}


def reset_warning(user):
    warnings_store[user] = 0


def add_warning(user):
    warnings_store[user] = warnings_store.get(user, 0) + 1
    return warnings_store[user]


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            return render_template("login.html", error="Username required")

        session["user"] = username
        reset_warning(username)
        return redirect(url_for("exam"))

    return render_template("login.html")


@app.route("/exam")
def exam():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("exam.html", user=session["user"])


@app.route("/detect", methods=["POST"])
def detect():
    if "user" not in session:
        return jsonify({"status": "Session Expired"}), 401

    data = request.get_json()
    image = data.get("image")

    result = detect_cheating(image)

    if result != "OK":
        count = add_warning(session["user"])

        if count >= 2:
            return jsonify({
                "status": "Terminate",
                "reason": result,
                "warnings": count
            })

        return jsonify({
            "status": "Warning",
            "reason": result,
            "warnings": count
        })

    return jsonify({"status": "Normal"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
