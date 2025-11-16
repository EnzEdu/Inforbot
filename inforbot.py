from flask import Flask, render_template, request

app = Flask(__name__)
'''
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
'''

@app.route("/", methods=["GET", "POST"])
def login():
    print(request.method)
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/register")
def register():
    return render_template("register.html")

# .venv/Scripts/activate
# flask --app inforbot run