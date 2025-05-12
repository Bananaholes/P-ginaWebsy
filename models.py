from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Reseña(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
