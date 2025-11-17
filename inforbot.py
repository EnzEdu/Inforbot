from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from typing import List
from models import db, M_AppUser, M_Conversa, M_Mensagem
from config import Config
from agent import Agent

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
        if user and user.confere_senha(senha):
            session["user_id"] = user.id
            session["usuario"] = user.usuario
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciais invalidas.")
            return redirect(url_for("login"))
    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



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

        # Salva o usuario no bd
        db.session.add(user)

        # PLACEHOLDER
        db.session.add(conversa_inicial)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")



@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "GET":
        # Recebe a lista de mensagens da conversa selecionada
        # PLACEHOLDER
        conversaInicial : M_Conversa = M_Conversa.query.filter(
            (M_Conversa.appuser_id == session["user_id"]) & (M_Conversa.titulo == "Conversa inicial")
        ).first()
        mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversaInicial.id)).all()

        # Converte em uma lista de tuplas (mais controlavel no html)
        lista_mensagens = [{
            "autor": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
            "texto": mensagem.texto
        } for mensagem in mensagens]
        print(mensagens)
        print(lista_mensagens)

        return render_template("dashboard.html", conversa=conversaInicial, lista_mensagens=lista_mensagens)
    return render_template("dashboard.html")



@app.route("/api/chat", methods=["POST"])
def send_message():
    data = request.get_json()
    mensagem_usuario = data.get("message")
    conversa_id = data.get("conversa_id")

    if not mensagem_usuario:
        return jsonify({"error": "Nenhuma mensagem digitada."}), 400



    # Define o historico
    # PLACEHOLDER
    conversaInicial : M_Conversa = M_Conversa.query.filter(
        (M_Conversa.appuser_id == session["user_id"]) & (M_Conversa.titulo == "Conversa inicial")
    ).first()
    mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversaInicial.id)).all()
    historico = [{
        "papel": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
        "mensagem": mensagem.texto
    } for mensagem in mensagens]

    # Cria um resumo a cada 6 mensagens
    if (len(historico) > 0 and len(historico) % 6 == 0):
        # Separa as ultimas seis mensagens do historico
        historico1 = historico[-6:]

        # Gera um resumo das ultimas mensagens
        resumo : str = "Este é o histórico de prompts da conversa até agora. " \
            "Retorne um resumo, utilizando o menor número possível de tokens, " \
            "mas mantendo a descrição de pontos importantes que podem vir a ser utilizados " \
            "novamente na conversa."
        ai_text_res = Agent.enviar_mensagem(historico1, resumo)

        # Salva a resposta
        ai_msg_res = M_Mensagem(
            conversa_id=conversa_id,
            autor="GPT-5.0_Nano",
            texto=ai_text_res
        )
        db.session.add(ai_msg_res)
        db.session.commit()

        # Coleta o novo historico
        mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversaInicial.id)).all()
        historico = [{
            "papel": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
            "mensagem": mensagem.texto
        } for mensagem in mensagens]

        # Restringe o historico para apenas o resumo
        historico = historico[-1:]

    else:
        # Retorna as mensagens desde o ultimo resumo
        qnt_faltante_resumo = len(historico) % 6
        historico = historico[(qnt_faltante_resumo * -1):]


    # Envia mensagem para o modelo
    ai_text = Agent.enviar_mensagem(historico, mensagem_usuario)

    # Salva a pergunta
    db.session.expunge_all()
    msg = M_Mensagem(
        conversa_id=conversa_id,
        autor=session["usuario"],
        texto=mensagem_usuario
    )
    db.session.add(msg)
    db.session.commit()

    # Salva a resposta
    db.session.expunge_all()
    ai_msg = M_Mensagem(
        conversa_id=conversa_id,
        autor="GPT-5.0_Nano",
        texto=ai_text
    )
    db.session.add(ai_msg)
    db.session.commit()

    # Retorna a resposta
    return jsonify({"response": ai_text})



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

# .venv/Scripts/activate
# pip install -r requirements.txt
# flask --app inforbot run