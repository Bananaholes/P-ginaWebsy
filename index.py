from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_migrate import Migrate

app = Flask(__name__)


# Configuración de la base de datos SQLite
# Definir el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'reseñas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'  # Necesario para sesiones y flash messages

# Inicializa la base de datos y las migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)

    # Relación con reseñas
    reseñas = db.relationship('Reseña', backref='usuario', lazy=True)


class Reseña(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Integer)  # Nueva columna para las estrellas
    
    # Relación con Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Clave foránea correcta

    def __repr__(self):
        return f'<Reseña {self.id}>'


# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Rutas normales
@app.route('/index.html')
def principal():
    return render_template("index.html")

@app.route('/Servicios')
def servicios():
    return render_template("servicios.html")

@app.route('/Contactos')
def contacto():
    return render_template("contacto.html")

# Rutas para registro y login
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form['contraseña']
        hashed_password = generate_password_hash(contraseña, method='pbkdf2:sha256')

        nuevo_usuario = Usuario(nombre=nombre, email=email, contraseña=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.contraseña, contraseña):
            session['usuario_id'] = usuario.id  # Guardar el usuario en la sesión
            flash('¡Has iniciado sesión correctamente!', 'success')
            return redirect(url_for('reseñas'))
        else:
            flash('Email o contraseña incorrectos. Intenta de nuevo.', 'danger')

    return render_template('login.html')

# Ruta de reseñas con base de datos
@app.route("/Reseñas", methods=["GET", "POST"])
def reseñas():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        contenido = request.form.get("contenido")
        calificacion = request.form.get("calificacion")

        if not (nombre and contenido and calificacion):
            flash("Por favor completá todos los campos.")
            return redirect(url_for('reseñas'))

        nueva_reseña = Reseña(
            nombre=nombre,
            contenido=contenido,
            calificacion=int(calificacion),
            usuario_id=session.get("usuario_id")
        )
        db.session.add(nueva_reseña)
        db.session.commit()
        return redirect(url_for("reseñas"))

    todas_reseñas = Reseña.query.all()
    return render_template("reseñas.html", reseñas=todas_reseñas)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    nombre = request.form['nombre']
    contenido = request.form['contenido']
    calificacion = int(request.form['calificacion'])  # Convertir el valor a entero
    
    nueva_reseña = Reseña(nombre=nombre, contenido=contenido, calificacion=calificacion)
    db.session.add(nueva_reseña)
    db.session.commit()
    
    return redirect(url_for('reseñas'))

@app.route('/eliminar_reseña/<int:id>', methods=['POST'])
def eliminar_reseña(id):
    reseña = Reseña.query.get_or_404(id)

    # Verificar que el usuario esté logueado y que sea el autor de la reseña
    if 'usuario_id' not in session or reseña.usuario_id != session['usuario_id']:
        flash("No tenés permiso para eliminar esta reseña.", "danger")
        return redirect(url_for('reseñas'))

    db.session.delete(reseña)
    db.session.commit()
    flash("Reseña eliminada correctamente.", "success")
    return redirect(url_for('reseñas'))


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Eliminar al usuario de la sesión
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True, port=5020)
