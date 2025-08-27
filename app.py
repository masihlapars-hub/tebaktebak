from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rahasia123"
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['AVATAR_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Pastikan folder upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

def load_categories():
    try:
        with open("categories.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_categories(categories):
    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_questions(questions):
    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def load_avatars():
    try:
        with open("avatars.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        # Avatar default jika file tidak ada
        default_avatars = [
            {"name": "Cat", "img": "cat.png"},
            {"name": "Dog", "img": "dog.png"},
            {"name": "Bear", "img": "bear.png"},
            {"name": "Allen", "img": "allen.png"},
            {"name": "Astro", "img": "astro.png"},
            {"name": "Dragon", "img": "dragon.png"},
            {"name": "Fox", "img": "fox.png"},
            {"name": "Panda", "img": "panda.png"},
            {"name": "Duck", "img": "duck.png"},
            {"name": "Monkey", "img": "monkey.png"},
            {"name": "Owl", "img": "owl.png"},
            {"name": "Lemon", "img": "lemon.png"}
        ]
        return default_avatars

def save_avatars(avatars):
    with open("avatars.json", "w", encoding="utf-8") as f:
        json.dump(avatars, f, indent=2, ensure_ascii=False)

@app.route("/", methods=["GET", "POST"])
def login():
    avatars = load_avatars()
    if request.method == "POST":
        username = request.form["username"]
        selected_avatar = request.form["avatar"]
        session["username"] = username
        session["avatar"] = selected_avatar
        return redirect(url_for("home"))
    return render_template("login.html", avatars=avatars)

@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    categories = load_categories()
    return render_template("home.html",
                           username=session["username"],
                           avatar=session["avatar"],
                           categories=categories)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form["password"]
        if password == "281105":
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            flash("Password admin salah!", "error")
    return render_template("admin_login.html")

@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    categories = load_categories()
    questions = load_questions()
    avatars = load_avatars()
    return render_template("admin_panel.html", 
                          categories=categories, 
                          questions=questions,
                          avatars=avatars)

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/add_category", methods=["POST"])
def add_category():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    name = request.form["name"]
    desc = request.form["desc"]
    file = request.files["image"]
    filename = secure_filename(file.filename) if file and file.filename else None
    if filename:
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    categories = load_categories()
    categories.append({"name": name, "desc": desc, "img": filename})
    save_categories(categories)
    return redirect(url_for("admin_panel"))

@app.route("/edit_category/<int:index>", methods=["GET", "POST"])
def edit_category(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    categories = load_categories()
    if request.method == "POST":
        categories[index]["name"] = request.form["name"]
        categories[index]["desc"] = request.form["desc"]
        file = request.files["image"]
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            categories[index]["img"] = filename
        save_categories(categories)
        return redirect(url_for("admin_panel"))
    return render_template("edit_category.html", category=categories[index], index=index)

@app.route("/delete_category/<int:index>")
def delete_category(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    categories = load_categories()
    if 0 <= index < len(categories):
        categories.pop(index)
        save_categories(categories)
    return redirect(url_for("admin_panel"))

@app.route("/add_question", methods=["POST"])
def add_question():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    category = request.form["category"]
    difficulty = request.form["difficulty"]
    question_text = request.form["question_text"]
    options = [
        request.form["option1"],
        request.form["option2"],
        request.form["option3"],
        request.form["option4"]
    ]
    correct_answer = int(request.form["correct_answer"])
    
    questions = load_questions()
    questions.append({
        "category": category,
        "difficulty": difficulty,
        "question_text": question_text,
        "options": options,
        "correct_answer": correct_answer
    })
    save_questions(questions)
    return redirect(url_for("admin_panel"))

@app.route("/edit_question/<int:index>", methods=["GET", "POST"])
def edit_question(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    questions = load_questions()
    categories = load_categories()
    
    if request.method == "POST":
        questions[index]["category"] = request.form["category"]
        questions[index]["difficulty"] = request.form["difficulty"]
        questions[index]["question_text"] = request.form["question_text"]
        questions[index]["options"] = [
            request.form["option1"],
            request.form["option2"],
            request.form["option3"],
            request.form["option4"]
        ]
        questions[index]["correct_answer"] = int(request.form["correct_answer"])
        save_questions(questions)
        return redirect(url_for("admin_panel"))
    
    return render_template("edit_question.html", 
                          question=questions[index], 
                          index=index,
                          categories=categories)

@app.route("/delete_question/<int:index>")
def delete_question(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    questions = load_questions()
    if 0 <= index < len(questions):
        questions.pop(index)
        save_questions(questions)
    return redirect(url_for("admin_panel"))

@app.route("/add_avatar", methods=["POST"])
def add_avatar():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    name = request.form["name"]
    avatar_file = request.files["avatar_file"]
    avatar_url = request.form["avatar_url"]
    
    avatars = load_avatars()
    
    if avatar_file and avatar_file.filename:
        filename = secure_filename(avatar_file.filename)
        avatar_file.save(os.path.join(app.config["AVATAR_FOLDER"], filename))
        avatars.append({"name": name, "img": filename})
    elif avatar_url:
        # Untuk URL, kita simpan langsung URL-nya
        avatars.append({"name": name, "img": avatar_url, "is_url": True})
    
    save_avatars(avatars)
    return redirect(url_for("admin_panel"))

@app.route("/delete_avatar/<int:index>")
def delete_avatar(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    avatars = load_avatars()
    if 0 <= index < len(avatars):
        # Hapus file fisik jika bukan URL
        avatar = avatars[index]
        if "is_url" not in avatar or not avatar["is_url"]:
            img_path = os.path.join(app.config["AVATAR_FOLDER"], avatar["img"])
            if os.path.exists(img_path):
                os.remove(img_path)
        avatars.pop(index)
        save_avatars(avatars)
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    app.run(debug=True)
