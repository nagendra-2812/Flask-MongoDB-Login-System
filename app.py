from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# ==========================================================
# CONFIGURATION
# ==========================================================
# Local default:
#   mongodb://127.0.0.1:27017/
#
# Atlas/Render:
#   Set MONGO_URI as an environment variable.
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017/"
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["LoginDB"]
users = db["Users"]

# Ensure username uniqueness.
users.create_index(
    [("username", ASCENDING)],
    unique=True
)


# ==========================================================
# DATABASE HEALTH CHECK
# ==========================================================
@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return {"status": "ok", "database": "LoginDB", "collection": "Users"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}, 500


# ==========================================================
# HOME
# ==========================================================
@app.get("/")
def home():
    return render_template("home.html")


# ==========================================================
# REGISTER
# ==========================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            return "Password and Confirm Password do not match.", 400

        if len(password) < 6:
            return "Password must contain at least 6 characters.", 400

        if users.find_one({"username": username}):
            return "Username already exists.", 409

        document = {
            "name": name,
            "username": username,
            "password": generate_password_hash(password),
            "age": 25,
            "department": "CSE",
            "skills": ["Python", "MongoDB"],
            "address": {
                "city": "Ghaziabad",
                "state": "Uttar Pradesh"
            }
        }

        try:
            users.insert_one(document)
        except DuplicateKeyError:
            return "Username already exists.", 409

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================================================
# LOGIN
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = users.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            return "Login Successful!"

        return "Invalid username or password.", 401

    return render_template("login.html")


# ==========================================================
# DISPLAY ALL USERS
# ==========================================================
@app.get("/users")
def users_page():
    all_users = users.find(
        {},
        {
            "_id": 0,
            "password": 0
        }
    )
    return render_template("users.html", users=all_users)


# ==========================================================
# DELETE USER
# ==========================================================
@app.get("/delete/<username>")
def delete_user(username):
    users.delete_one({"username": username})
    return redirect(url_for("users_page"))


# ==========================================================
# SEARCH USER
# ==========================================================
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        username = request.form["username"].strip()

        user = users.find_one(
            {"username": username},
            {
                "_id": 0,
                "password": 0
            }
        )

        if user:
            return render_template("search.html", user=user)

        return "User not found.", 404

    return render_template("search.html")


# ==========================================================
# EDIT USER
# ==========================================================
@app.route("/edit/<username>", methods=["GET", "POST"])
def edit_user(username):
    user = users.find_one(
        {"username": username},
        {"password": 0}
    )

    if not user:
        return "User not found.", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        new_username = request.form["username"].strip()

        try:
            users.update_one(
                {"username": username},
                {
                    "$set": {
                        "name": name,
                        "username": new_username
                    }
                }
            )
        except DuplicateKeyError:
            return "The new username already exists.", 409

        return redirect(url_for("users_page"))

    return render_template("edit_user.html", user=user)


# ==========================================================
# QUERY DEMO
# ==========================================================
@app.route("/query-demo", methods=["GET", "POST"])
def query_demo():
    result = None
    result_title = "All Users — Initial find()"
    message = None

    safe_projection = {"_id": 0, "password": 0}

    if request.method == "POST":
        operation = request.form["operation"]

        if operation == "find":
            result_title = "find() — All Documents"
            result = list(users.find({}, safe_projection))

        
        elif operation == "findOne":
            username = request.form["username"].strip()
            result_title = "find_one()"

            found_user = users.find_one(
                {"username": username},
                safe_projection
            )

            if found_user:
                result = [found_user]
            else:
                result = []
                message = "User not found."


        elif operation in {"gt", "lt", "gte", "lte"}:
            age = int(request.form["age"])
            operators = {
                "gt": ("$gt", "Age Greater Than"),
                "lt": ("$lt", "Age Less Than"),
                "gte": ("$gte", "Age Greater Than or Equal"),
                "lte": ("$lte", "Age Less Than or Equal"),
            }
            operator, label = operators[operation]
            result_title = f"{operator} — {label}"
            result = list(
                users.find(
                    {"age": {operator: age}},
                    safe_projection
                )
            )

        elif operation == "in":
            result_title = "$in — Department Match"
            result = list(
                users.find(
                    {"department": {"$in": ["CSE", "IT"]}},
                    safe_projection
                )
            )

        elif operation == "ne":
            result_title = "$ne — Department Not Equal"
            result = list(
                users.find(
                    {"department": {"$ne": "CSE"}},
                    safe_projection
                )
            )

        elif operation == "projection":
            result_title = "Projection — Selected Fields Only"
            result = list(
                users.find(
                    {},
                    {
                        "_id": 0,
                        "name": 1,
                        "username": 1,
                        "department": 1
                    }
                )
            )

        elif operation == "sort_asc":
            result_title = "Sorting — Age Ascending"
            result = list(
                users.find({}, safe_projection).sort("age", ASCENDING)
            )

        elif operation == "sort_desc":
            result_title = "Sorting — Age Descending"
            result = list(
                users.find({}, safe_projection).sort("age", DESCENDING)
            )

        elif operation == "limit":
            number = int(request.form["number"])
            result_title = f"Limit — First {number} Documents"
            result = list(
                users.find({}, safe_projection).limit(number)
            )

        elif operation == "array":
            result_title = "Array Query — Users Having MongoDB Skill"
            result = list(
                users.find({"skills": "MongoDB"}, safe_projection)
            )

        elif operation == "nested":
            result_title = "Nested Document — City = Ghaziabad"
            result = list(
                users.find({"address.city": "Ghaziabad"}, safe_projection)
            )

        elif operation == "cursor":
            result_title = "Cursor Handling"
            cursor = users.find({}, safe_projection)
            result = [user for user in cursor]

        elif operation == "index":
            index_name = users.create_index(
                [("username", ASCENDING)],
                unique=True
            )
            result_title = "Index Created"
            message = f"Index created successfully: {index_name}"
            result = []

        elif operation == "show_indexes":
            result_title = "Current Indexes"
            result = list(users.list_indexes())

    return render_template(
        "query_demo.html",
        result=result,
        result_title=result_title,
        message=message
    )


if __name__ == "__main__":
    # Development server only. Render uses Gunicorn.
    app.run(debug=True)
