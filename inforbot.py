from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, abort
from flask_migrate import Migrate
from flasgger import Swagger
from werkzeug.utils import secure_filename
from typing import List
from models import db, M_AppUser, M_Conversa, M_Mensagem, M_Documento
from config import Config, PASTA_USERS
from agent import Agent
import os
import uuid
import shutil

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
swagger = Swagger(app)



@app.route("/")
def home():
    """
    Endpoint inicial.
    ---
    responses:
        200:
            description: OK
        500:
            description: Erro no server.
    """
    if 'usuario' in session:
        return redirect(url_for('dashboard', user_uuid=session["user_uuid"], conversa_id=session["conversa_id"]))
    return redirect(url_for('login'))



@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Endpoint de login
    ---
    tags:
      - Login
    
    summary: Realiza o login.
    
    description: Permite acesso ao sistema ao informar as credenciais.
    
    parameters:
      - name: usuario
        in: formData
        type: string
        required: true
        description: Nome de usuário.
      - name: senha
        in: formData
        type: string
        required: true
        description: Senha do usuário.
    
    consumes:
      - application/x-www-form-urlencoded
    
    responses:
        200:
            description: OK
        500:
            description: Erro no server.
    """
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        user : M_AppUser = M_AppUser.query.filter_by(usuario=usuario).first()
        if user and user.confere_senha(senha):
            conversa_padrao : M_Conversa = M_Conversa.query.filter_by(t_appuser=user).first()

            session["user_id"] = user.id
            session["user_uuid"] = user.uuid
            session["usuario"] = user.usuario
            if conversa_padrao:
                session["conversa_id"] = conversa_padrao.id
            else:
                # Cria uma sessao caso ainda nao exista
                conversa_inicial = M_Conversa(t_appuser=user, titulo="Sessão inicial")
                db.session.add(conversa_inicial)
                db.session.commit()
                session["conversa_id"] = conversa_inicial.id
            return redirect(url_for("dashboard", user_uuid=session["user_uuid"], conversa_id=session["conversa_id"]))
        else:
            flash("Credenciais invalidas.")
            return redirect(url_for("login"))
    return render_template("login.html")



@app.route("/logout")
def logout():
    """
    Endpoint de logout
    ---
    tags:
      - Login
    
    summary: Realiza o logout.
    
    description: Permite a desconexão do sistema ao utilizar as credenciais da sessão atual.

    responses:
        200:
            description: OK
        500:
            description: Erro no server.
    """
    session.clear()
    return redirect(url_for("login"))



@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Endpoint de criação de usuário
    ---
    tags:
      - Usuário

    summary: Realiza o cadastro de um usuário.

    description: Permite a desconexão do sistema ao utilizar as credenciais da sessão atual.

    consumes:
      - application/x-www-form-urlencoded

    parameters:
      - name: Nome
        in: formData
        type: string
        required: true
        description: Nome completo do usuário.

      - name: Nome de usuário
        in: formData
        type: string
        required: true
        description: Nome de usuário único.

      - name: E-mail
        in: formData
        type: string
        required: true
        description: E-mail do usuário.

      - name: Senha
        in: formData
        type: string
        required: true
        description: Senha escolhida pelo usuário.

    responses:
        200:
            description: OK
        500:
            description: Erro no server.
    """
    if request.method == "POST":
        fotoPerfil = request.files.get("fileInput") # PLACEHOLDER: trocar pelo termo no campo "name" no input da foto
        descricao = request.form["desc"]            # PLACEHOLDER: trocar pelo termo no campo "name" no input da descricao
        nomeCompleto = request.form["nome"].strip()
        usuario = request.form["usuario"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        # Check de campos em uso
        if M_AppUser.query.filter((M_AppUser.usuario == usuario) | (M_AppUser.email == email)).first():
            flash("Nome de usuario ou email em uso.")
            return redirect(url_for("register"))

        # Criação do objeto do usuario
        user = M_AppUser(
            uuid=str(uuid.uuid4()),
            descricao=descricao,
            nomeCompleto=nomeCompleto, 
            usuario=usuario, 
            email=email)
        user.set_senha_hasheada(senha)

        # Salva a foto de perfil se existir
        if fotoPerfil:
            PASTA_USER = os.path.join(PASTA_USERS, str(user.uuid))
            os.makedirs(PASTA_USER, exist_ok=True)

            fotoPfpCaminho = os.path.join(PASTA_USER, secure_filename(fotoPerfil.filename))
            fotoPerfil.save(fotoPfpCaminho)
        else:
            fotoPfpCaminho = ''
        user.set_foto_perfil_caminho(fotoPfpCaminho)

        # Cria uma conversa inicial
        conversa_inicial = M_Conversa(t_appuser=user, titulo="Sessão inicial")

        # Salva o usuario no bd
        db.session.add(user)

        # Salva a conversa inicial
        db.session.add(conversa_inicial)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")



@app.route("/<user_uuid>/dashboard/<conversa_id>", methods=["GET", "POST"])
def dashboard(user_uuid, conversa_id):
    """
    Endpoint de acesso a uma conversa do dashboard.
    ---
    tags:
      - Usuário

    summary: Acesso a uma conversa do dashboard.

    description: >
        Retorna a pagina do dashboard para o usuário aberto em uma conversa.
        Acesso proibido se a sessão não estiver batendo com o login.
    
    parameters:
      - name: user_uuid
        in: path
        type: string
        required: true
        description: UUID do usuário.

      - name: conversa_id
        in: path
        type: integer
        required: true
        description: ID da conversa escolhida.

    responses:
        200:
            description: OK
        403:
            description: Você não tem acesso a esta página.
        500:
            description: Erro no server.
    """
    # Previne acessos externos
    if session.get("user_uuid") != user_uuid:
        abort(403)

    if request.method == "POST":
        documento = request.files.get("pdfInput") # PLACEHOLDER: trocar pelo termo no campo "name" no input do documento

        # Se documento esta sendo enviado
        if (documento):
            # Salva o documento localmente
            PASTA_CONV = os.path.join(PASTA_USERS, session.get("user_uuid"), session.get("conversa_id"))
            os.makedirs(PASTA_CONV, exist_ok=True)

            docCaminho = os.path.join(PASTA_CONV, secure_filename(documento.filename))
            documento.save(docCaminho)

            # Salva o documento na db
            doc = M_Documento(
                conversa_id=session["conversa_id"],
                nome=secure_filename(documento.filename), 
                path=docCaminho
            )
            db.session.add(doc)
            db.session.commit()

        # Se conversa esta sendo criada
        else:
            nova_conversa = M_Conversa(appuser_id=session["user_id"], titulo="Sessão inicial")
            db.session.add(nova_conversa)
            db.session.commit()
            session["conversa_id"] = nova_conversa.id
    else:
        if (session["conversa_id"]):
            session["conversa_id"] = conversa_id

    # Recebe a lista de conversas
    lista_conversas = M_Conversa.query.filter((M_Conversa.appuser_id == session["user_id"])).all()

    if (session.get("conversa_id")):
        # Recebe a lista de mensagens da conversa selecionada
        conversa : M_Conversa = M_Conversa.query.filter(((M_Conversa.appuser_id == session["user_id"]) & (M_Conversa.id == conversa_id))).first()
        mensagens : List[M_Mensagem] = M_Mensagem.query.filter((M_Mensagem.conversa_id == conversa.id)).all()
        documentos : List[M_Documento] = M_Documento.query.filter((M_Documento.conversa_id == conversa.id)).all()

        # Converte em uma lista de tuplas (mais controlavel no html)
        lista_mensagens = [{
            "autor": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
            "texto": mensagem.texto
        } for mensagem in mensagens]
        lista_mensagens = [result for result in lista_mensagens if "Resumo:" not in result["texto"] and "Titulo:" not in result["texto"]]
        lista_documentos = [doc.nome for doc in documentos]

        return render_template("dashboard.html", conversa=conversa, lista_conversas=lista_conversas, lista_mensagens=lista_mensagens, lista_documentos=documentos)
    else:
        return render_template("dashboard.html", conversa=conversa, lista_conversas=lista_conversas, lista_mensagens=[], lista_documentos=[])



@app.route("/api/chat", methods=["POST"])
def enviar_mensagem():
    """
    Endpoint de envio de mensagem para API do modelo.
    ---
    tags:
      - Operações
    
    summary: Manda uma mensagem para o modelo utilizado.
    
    description: Recebe a mensagem do usuário, repassa para o modelo, e aguarda sua resposta.

    requestBody:
    required: true
    content:
        application/json:
        schema:
            type: object
            properties:
            message:
                type: string
                example: "Olá!"
            conversa_id:
                type: integer
                example: 67
            required:
            - message
            - conversa_id

    responses:
        200:
            description: OK
        500:
            description: Erro no server.
    """
    data = request.get_json()
    mensagem_usuario = data.get("message")
    conversa_id = data.get("conversa_id")
    documentos_escolhidos_ids = data.get("documentosEscolhidos") # PLACEHOLDER: trocar pelo campo no JSON.stringify em dashboard.js 

    if not mensagem_usuario:
        return jsonify({"error": "Nenhuma mensagem digitada."}), 400



    # Define o historico
    mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversa_id)).all()
    historico = [{
        "papel": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
        "mensagem": mensagem.texto
    } for mensagem in mensagens]
    historico = [result for result in historico if "Resumo:" not in result["mensagem"] and "Titulo:" not in result["mensagem"]]

    # Cria um resumo a cada 6 mensagens
    if (len(historico) > 0 and len(historico) % 6 == 0):
        # Separa as ultimas seis mensagens do historico
        historico1 = historico[-6:]

        # Gera um resumo das ultimas mensagens
        resumo : str = "Este é o histórico de prompts da conversa até agora. " \
            "Retorne um resumo, utilizando o menor número possível de tokens, " \
            "mas mantendo a descrição de pontos importantes que podem vir a ser utilizados " \
            "novamente na conversa. Comece sua resposta com a palavra Resumo."
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
        mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversa_id)).all()
        historico = [{
            "papel": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
            "mensagem": mensagem.texto
        } for mensagem in mensagens]
        historico = [result for result in historico if "Resumo:" not in result["mensagem"] and "Titulo:" not in result["mensagem"]]

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

    # Se o historico anterior a este dialogo estava vazio,
    # gera um titulo para a conversa
    if len(historico) == 0:
        mensagens : List[M_Mensagem]= M_Mensagem.query.filter((M_Mensagem.conversa_id == conversa_id)).all()
        historico = [{
            "papel": "USUARIO" if mensagem.autor == session["usuario"] else "BOT", 
            "mensagem": mensagem.texto
        } for mensagem in mensagens]

        # Gera um resumo das ultimas mensagens
        titulo : str = "Este é o histórico de prompts da conversa até agora. " \
            "Retorne um titulo para esta conversa, baseado no dialogo recente. " \
            "Sua resposta deve começar com \"Titulo:\", seguido por sua sugestão de título. Nada mais." \
            "Sua sugestão de título está limitada a no máximo 5 palavras."
        ai_text_res = Agent.enviar_mensagem(historico, titulo)

        # Salva a resposta
        ai_msg_res = M_Mensagem(
            conversa_id=conversa_id,
            autor="GPT-5.0_Nano",
            texto=ai_text_res
        )
        db.session.add(ai_msg_res)

        # Atualiza o titulo
        nova_conv : M_Conversa = M_Conversa.query.get(conversa_id)
        nova_conv.titulo = ai_text_res.split("Titulo: ", 1)[1]
    db.session.commit()

    # Retorna a resposta
    return jsonify({"response": ai_text})



@app.route("/deletar_conversa/<conversa_id>", methods=["POST"])
def deletar_conversa(conversa_id):
    """
    Endpoint de deleção de conversa.
    ---
    tags:
      - Operações
    
    summary: Apaga uma conversa existente.
    
    description: Remove uma conversa do usuário e suas mensagens. Cria uma conversa nova caso o usuário se esgote de conversas.

    responses:
        200:
            description: OK
        500:
            description: Erro no server.
    """
    # Busca a conversa no banco
    conversa = M_Conversa.query.filter_by(id=conversa_id, appuser_id=session["user_id"]).first()

    if conversa:
        try:
            # Deleta a conversa em si
            db.session.delete(conversa)
            
            # Deleta a pasta relacionada, se existir
            PASTA_CONV = os.path.join(PASTA_USERS, session.get("user_uuid"), session.get("conversa_id"))
            if (os.path.exists(PASTA_CONV)):
                shutil.rmtree(PASTA_CONV)

            # Salva as alterações
            db.session.commit()
            
        except Exception as e:
            db.session.rollback() # Desfaz se der erro
            print(f"Erro ao deletar: {e}")
            flash("Erro ao excluir a conversa.")
    else:
        flash("Conversa não encontrada ou você não tem permissão.")

    # Redireciona para dashboard
    ultima_conversa : M_Conversa = M_Conversa.query.filter_by(appuser_id=session["user_id"]).first()
    if ultima_conversa:
        session["conversa_id"] = ultima_conversa.id
        return redirect(url_for("dashboard", user_uuid=session["user_uuid"], conversa_id=session["conversa_id"]))
    else:
        # Cria uma sessao caso ainda nao exista
        user : M_AppUser = M_AppUser.query.get(session["user_id"])
        conversa_inicial = M_Conversa(t_appuser=user, titulo="Sessão inicial")
        db.session.add(conversa_inicial)
        db.session.commit()
        session["conversa_id"] = conversa_inicial.id
        return redirect(url_for("dashboard", user_uuid=session["user_uuid"], conversa_id=session["conversa_id"]))



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

# .venv/Scripts/activate
# pip install -r requirements.txt
# flask --app inforbot run