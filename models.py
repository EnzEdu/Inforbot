from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()

class M_AppUser(db.Model):
    __tablename__ = "t_appuser"

    uuid            = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    criado_em       = db.Column(db.DateTime, default=datetime.now)
    fotoPath        = db.Column(db.String(300), nullable=False)
    descricao       = db.Column(db.String(400), nullable=False)
    nomeCompleto    = db.Column(db.String(400), unique=True, nullable=False)
    usuario         = db.Column(db.String(80), unique=True, nullable=False)
    email           = db.Column(db.String(200), unique=True, nullable=False)
    senha_hash      = db.Column(db.String(128), nullable=False)

    # Usuario pode ter n conversas
    conversas = db.relationship(
        "M_Conversa",
        back_populates="t_appuser",
        cascade="all, delete-orphan",
        order_by="M_Conversa.criado_em"
    )

    def __repr__(self):
        return f"<M_AppUser {self.usuario}>"
    
    def set_foto_perfil_caminho(self, path: str):
        self.fotoPath = path

    def set_senha_hasheada(self, senha: str):
        self.senha_hash = generate_password_hash(senha)

    # Checa senha inserida com a senha da entrada do bd
    def confere_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)




class M_Conversa(db.Model):
    __tablename__ = "t_conversa"

    appuser_id      = db.Column(db.Integer, db.ForeignKey("t_appuser.id"), nullable=False)
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    criado_em       = db.Column(db.DateTime, default=datetime.now)
    titulo          = db.Column(db.String(100), nullable=False)

    # Conversa esta ligada a 1 usuario
    t_appuser = db.relationship(
        "M_AppUser", 
        back_populates="conversas"
    )

    # Conversa pode ter n mensagens
    mensagens = db.relationship(
        "M_Mensagem",
        back_populates="t_conversa",
        cascade="all, delete-orphan",
        order_by="M_Mensagem.enviada_em"
    )

    # Conversa pode ter n documentos
    documentos = db.relationship(
        "M_Documento",
        back_populates="t_conversa",
        cascade="all, delete-orphan",
        order_by="M_Documento.enviada_em"
    )




class M_Mensagem(db.Model):
    __tablename__ = "t_mensagem"

    conversa_id     = db.Column(db.Integer, db.ForeignKey("t_conversa.id"), nullable=False) # chave estrangeira
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enviada_em      = db.Column(db.DateTime, default=datetime.now)
    autor           = db.Column(db.String(80), nullable=False)
    texto           = db.Column(db.Text, nullable=False)

    # Mensagem esta ligada a 1 conversa
    t_conversa = db.relationship("M_Conversa", back_populates="mensagens")




class M_Documento(db.Model):
    __tablename__ = "t_documento"

    conversa_id     = db.Column(db.Integer, db.ForeignKey("t_conversa.id"), nullable=False) # chave estrangeira
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enviada_em      = db.Column(db.DateTime, default=datetime.now)
    nome            = db.Column(db.String(100), nullable=False)
    path            = db.Column(db.String(300), nullable=False)

    # Mensagem esta ligada a 1 conversa
    t_conversa = db.relationship("M_Conversa", back_populates="documentos")