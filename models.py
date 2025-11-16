from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AppUser(db.Model):
    __tablename__ = "appuser"

    id              = db.Column(db.Integer, primary_key=True)
    criado_em       = db.Column(db.DateTime, default=datetime.now)
    nomeCompleto    = db.Column(db.String(400), unique=True, nullable=False)
    usuario         = db.Column(db.String(80), unique=True, nullable=False)
    email           = db.Column(db.String(200), unique=True, nullable=False)
    password_hash   = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<AppUser {self.username}>"

    def set_senha_hasheada(self, password: str):
        self.password_hash = generate_password_hash(password)

    # Checa senha inserida com a senha da entrada do bd
    def checa_senha(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
