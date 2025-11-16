from flask import Flask, render_template, request, session, redirect, url_for, flash
from models import db, M_AppUser, M_Conversa, M_Mensagem
from config import Config
from flask_migrate import Migrate
from typing import List

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

            user : M_AppUser = M_AppUser.query.filter_by(usuario=usuario).first()
            if user and user.checa_senha(senha):
                session["user_id"] = user.id
                session["usuario"] = user.usuario
                return redirect(url_for("dashboard"))
            else:
                flash("Credenciais invalidas.")
                return redirect(url_for("login"))
        return render_template("login.html")

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
            if M_AppUser.query.filter((M_AppUser.usuario == usuario) | (M_AppUser.email == email)).first():
                flash("Nome de usuario ou email em uso.")
                return redirect(url_for("register"))

            user = M_AppUser(nomeCompleto=nomeCompleto, usuario=usuario, email=email)
            user.set_senha_hasheada(senha)

            # PLACEHOLDER
            conversa_inicial = M_Conversa(t_appuser=user, titulo="Conversa inicial")

            db.session.add(user)
            db.session.add(conversa_inicial)
            db.session.commit()

            return redirect(url_for("login"))
        return render_template("register.html")


    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        # PLACEHOLDER
        if request.method == "GET":
            print(session["usuario"])
            conversaInicial : M_Conversa = M_Conversa.query.filter(
                (M_Conversa.appuser_id == session["user_id"]) & (M_Conversa.titulo == "Conversa inicial")
            ).first()
            mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversaInicial.id)).all()

            lista_mensagens = [(["USUARIO" if mensagem.autor == session["usuario"] else "BOT"], mensagem.texto) for mensagem in mensagens]
            print(lista_mensagens)

            return render_template("dashboard.html", lista_mensagens=lista_mensagens)

        elif request.method == "POST":
            usuarioAppUser : M_AppUser = M_AppUser.query.filter((M_AppUser.id == session["user_id"])).first()
            conversaInicial : M_Conversa = M_Conversa.query.filter(
                (M_Conversa.appuser_id == session["user_id"]) & (M_Conversa.titulo == "Conversa inicial")
            ).first()

            msg = M_Mensagem(
                conversa_id=conversaInicial.id,
                autor=session["usuario"],
                text=request.form["user_message"]
            )
            db.session.add(msg)
            db.session.commit()
        return render_template("dashboard.html")










    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    inforbot = app()
    inforbot.run(debug=True)

# .venv/Scripts/activate
# pip install -r requirements.txt
# flask --app inforbot run