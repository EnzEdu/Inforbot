from flask import Flask, render_template, request, session, redirect, url_for, flash
from models import db, AppUser
from config import Config
from flask_migrate import Migrate

def app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route("/")
    def home():
        if 'usuario' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = request.form["usuario"]
            senha = request.form["senha"]

            user : AppUser = AppUser.query.filter_by(usuario=usuario).first()
            if user and user.checa_senha(senha):
                session["user_id"] = user.id
                session["usuario"] = user.usuario
                return redirect(url_for("dashboard"))
            else:
                flash("Credenciais invalidas.")
                return redirect(url_for("login"))
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            nomeCompleto = request.form["nome"].strip()
            usuario = request.form["usuario"].strip()
            email = request.form["email"].strip().lower()
            senha = request.form["senha"]

            # Check de validacao de campos
            #if not nomeCompleto or not usuario or not email or not senha:
                #flash("Campos invalidos.")
                #return redirect(url_for("register"))

            # Check de campos em uso
            if AppUser.query.filter((AppUser.usuario == usuario) | (AppUser.email == email)).first():
                flash("Nome de usuario ou email em uso.")
                return redirect(url_for("register"))

            user = AppUser(nomeCompleto=nomeCompleto, usuario=usuario, email=email)
            user.set_senha_hasheada(senha)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("login"))
        return render_template("register.html")
    
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    inforbot = app()
    inforbot.run(debug=True)

# .venv/Scripts/activate
# pip install -r requirements.txt
# flask --app inforbot run