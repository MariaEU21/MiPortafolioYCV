from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:gQCx354qZRHfnoGmr7XYydFBmKC4VVnh@dpg-cqspjod6l47c7a5g6gg-a.oregon-postgres.render.com:5432/miportafolio_g2nc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo de usuario para autenticación
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Función para cargar un usuario por su ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modelo de datos personales
class DatosPersonales(db.Model):
    __tablename__ = 'datos_personales'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    github = db.Column(db.String(100))
    foto = db.Column(db.String(100))

# Modelo de certificaciones
class Certificaciones(db.Model):
    __tablename__ = 'certificaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre_certificacion = db.Column(db.String(550))
    organizacion_emisora = db.Column(db.String(100))
    fecha_expedicion = db.Column(db.String(20))
    credenciales_id = db.Column(db.String(50))
    url_credencial = db.Column(db.String(100))

# Modelo de educación
class Educacion(db.Model):
    __tablename__ = 'educacion'
    id = db.Column(db.Integer, primary_key=True)
    institucion = db.Column(db.String(100))
    titulo = db.Column(db.String(100))
    fecha_inicio = db.Column(db.String(20))
    fecha_fin = db.Column(db.String(20))

# Modelo de experiencia laboral
class ExperienciaLaboral(db.Model):
    __tablename__ = 'experiencia_laboral'
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    fecha_inicio = db.Column(db.String(20))
    fecha_fin = db.Column(db.String(20))
    descripcion = db.Column(db.String(200))

# Modelo de habilidades
class Habilidades(db.Model):
    __tablename__ = 'habilidades'
    id = db.Column(db.Integer, primary_key=True)
    habilidad = db.Column(db.String(100))
    nivel = db.Column(db.String(50))

# Modelo de proyectos
class Proyectos(db.Model):
    __tablename__ = 'proyectos'
    id = db.Column(db.Integer, primary_key=True)
    nombre_proyecto = db.Column(db.String(100))
    descripcion = db.Column(db.String(200))
    tecnologias_utilizadas = db.Column(db.String(100))
    enlace_proyecto = db.Column(db.String(100))
    imagen_proyecto = db.Column(db.String(100))  # Campo para la imagen

# Ruta para la página principal (home)
@app.route('/')
def home():
    proyectos = Proyectos.query.all()
    return render_template('index.html', proyectos=proyectos)

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('form'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

# Ruta para el logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Ruta para el formulario de datos personales
@app.route('/form')
@login_required
def form():
    datos = DatosPersonales.query.all()
    return render_template('form.html', datos=datos)

# Ruta para agregar datos personales
@app.route('/add', methods=['POST'])
@login_required
def add_dato():
    nombre = request.form.get('nombre')
    direccion = request.form.get('direccion')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    linkedin = request.form.get('linkedin')
    github = request.form.get('github')
    foto = request.files['foto']
    if foto:
        foto_filename = foto.filename
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
    else:
        foto_filename = None
    new_dato = DatosPersonales(
        nombre=nombre, direccion=direccion, telefono=telefono,
        email=email, linkedin=linkedin, github=github, foto=foto_filename)
    db.session.add(new_dato)
    db.session.commit()
    return redirect(url_for('form'))

# Ruta para editar datos personales
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dato(id):
    dato = DatosPersonales.query.get_or_404(id)
    if request.method == 'POST':
        dato.nombre = request.form['nombre']
        dato.direccion = request.form['direccion']
        dato.telefono = request.form['telefono']
        dato.email = request.form['email']
        dato.linkedin = request.form['linkedin']
        dato.github = request.form['github']
        foto = request.files.get('foto')
        if foto:
            foto_filename = foto.filename
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
            dato.foto = foto_filename
        db.session.commit()
        return redirect(url_for('form'))
    return render_template('edit_form.html', dato=dato)

# Ruta para eliminar datos personales
@app.route('/delete/<int:id>')
@login_required
def delete_dato(id):
    dato = DatosPersonales.query.get_or_404(id)
    db.session.delete(dato)
    db.session.commit()
    return redirect(url_for('form'))

# Ruta para mostrar certificaciones
@app.route('/certificaciones')
@login_required
def certificaciones():
    certs = Certificaciones.query.all()
    return render_template('certificaciones.html', certs=certs)

# Ruta para agregar certificaciones
@app.route('/certificaciones/add', methods=['POST'])
@login_required
def add_certificacion():
    nombre_certificacion = request.form.get('nombre_certificacion')
    organizacion_emisora = request.form.get('organizacion_emisora')
    fecha_expedicion = request.form.get('fecha_expedicion')
    credenciales_id = request.form.get('credenciales_id')
    url_credencial = request.form.get('url_credencial')
    new_cert = Certificaciones(
        nombre_certificacion=nombre_certificacion, organizacion_emisora=organizacion_emisora,
        fecha_expedicion=fecha_expedicion, credenciales_id=credenciales_id, url_credencial=url_credencial)
    db.session.add(new_cert)
    db.session.commit()
    return redirect(url_for('certificaciones'))

# Ruta para editar certificaciones
@app.route('/certificaciones/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_certificacion(id):
    cert = Certificaciones.query.get_or_404(id)
    if request.method == 'POST':
        cert.nombre_certificacion = request.form['nombre_certificacion']
        cert.organizacion_emisora = request.form['organizacion_emisora']
        cert.fecha_expedicion = request.form['fecha_expedicion']
        cert.credenciales_id = request.form['credenciales_id']
        cert.url_credencial = request.form['url_credencial']
        db.session.commit()
        return redirect(url_for('certificaciones'))
    return render_template('edit_certificaciones.html', cert=cert)

# Ruta para eliminar certificaciones
@app.route('/certificaciones/delete/<int:id>')
@login_required
def delete_certificacion(id):
    cert = Certificaciones.query.get_or_404(id)
    db.session.delete(cert)
    db.session.commit()
    return redirect(url_for('certificaciones'))

# Ruta para mostrar la educación
@app.route('/educacion')
@login_required
def educacion():
    edus = Educacion.query.all()
    return render_template('educacion.html', edus=edus)

# Ruta para agregar educación
@app.route('/educacion/add', methods=['POST'])
@login_required
def add_educacion():
    institucion = request.form.get('institucion')
    titulo = request.form.get('titulo')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    new_edu = Educacion(
        institucion=institucion, titulo=titulo,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    db.session.add(new_edu)
    db.session.commit()
    return redirect(url_for('educacion'))

# Ruta para editar educación
@app.route('/educacion/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_educacion(id):
    edu = Educacion.query.get_or_404(id)
    if request.method == 'POST':
        edu.institucion = request.form['institucion']
        edu.titulo = request.form['titulo']
        edu.fecha_inicio = request.form['fecha_inicio']
        edu.fecha_fin = request.form['fecha_fin']
        db.session.commit()
        return redirect(url_for('educacion'))
    return render_template('edit_educacion.html', edu=edu)

# Ruta para eliminar educación
@app.route('/educacion/delete/<int:id>')
@login_required
def delete_educacion(id):
    edu = Educacion.query.get_or_404(id)
    db.session.delete(edu)
    db.session.commit()
    return redirect(url_for('educacion'))

# Ruta para mostrar la experiencia laboral
@app.route('/experiencia_laboral')
@login_required
def experiencia_laboral():
    exps = ExperienciaLaboral.query.all()
    return render_template('experiencia_laboral.html', exps=exps)

# Ruta para agregar experiencia laboral
@app.route('/experiencia_laboral/add', methods=['POST'])
@login_required
def add_experiencia_laboral():
    empresa = request.form.get('empresa')
    cargo = request.form.get('cargo')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    descripcion = request.form.get('descripcion')
    new_exp = ExperienciaLaboral(
        empresa=empresa, cargo=cargo,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, descripcion=descripcion)
    db.session.add(new_exp)
    db.session.commit()
    return redirect(url_for('experiencia_laboral'))

# Ruta para editar experiencia laboral
@app.route('/experiencia_laboral/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_experiencia_laboral(id):
    exp = ExperienciaLaboral.query.get_or_404(id)
    if request.method == 'POST':
        exp.empresa = request.form['empresa']
        exp.cargo = request.form['cargo']
        exp.fecha_inicio = request.form['fecha_inicio']
        exp.fecha_fin = request.form['fecha_fin']
        exp.descripcion = request.form['descripcion']
        db.session.commit()
        return redirect(url_for('experiencia_laboral'))
    return render_template('edit_experiencia_laboral.html', exp=exp)

# Ruta para eliminar experiencia laboral
@app.route('/experiencia_laboral/delete/<int:id>')
@login_required
def delete_experiencia_laboral(id):
    exp = ExperienciaLaboral.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    return redirect(url_for('experiencia_laboral'))

# Ruta para mostrar habilidades
@app.route('/habilidades')
@login_required
def habilidades():
    skills = Habilidades.query.all()
    return render_template('habilidades.html', skills=skills)

# Ruta para agregar habilidades
@app.route('/habilidades/add', methods=['POST'])
@login_required
def add_habilidad():
    habilidad = request.form.get('habilidad')
    nivel = request.form.get('nivel')
    new_skill = Habilidades(
        habilidad=habilidad, nivel=nivel)
    db.session.add(new_skill)
    db.session.commit()
    return redirect(url_for('habilidades'))

# Ruta para editar habilidades
@app.route('/habilidades/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_habilidad(id):
    skill = Habilidades.query.get_or_404(id)
    if request.method == 'POST':
        skill.habilidad = request.form['habilidad']
        skill.nivel = request.form['nivel']
        db.session.commit()
        return redirect(url_for('habilidades'))
    return render_template('edit_habilidades.html', skill=skill)

# Ruta para eliminar habilidades
@app.route('/habilidades/delete/<int:id>')
@login_required
def delete_habilidad(id):
    skill = Habilidades.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    return redirect(url_for('habilidades'))

# Ruta para mostrar proyectos
@app.route('/proyectos')
@login_required
def proyectos():
    projects = Proyectos.query.all()
    return render_template('proyectos.html', projects=projects)

# Ruta para agregar proyectos
@app.route('/proyectos/add', methods=['POST'])
@login_required
def add_proyecto():
    nombre_proyecto = request.form.get('nombre_proyecto')
    descripcion = request.form.get('descripcion')
    tecnologias_utilizadas = request.form.get('tecnologias_utilizadas')
    enlace_proyecto = request.form.get('enlace_proyecto')
    imagen = request.files['imagen_proyecto']
    if imagen:
        imagen_filename = imagen.filename
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename))
    else:
        imagen_filename = None
    new_project = Proyectos(
        nombre_proyecto=nombre_proyecto, descripcion=descripcion,
        tecnologias_utilizadas=tecnologias_utilizadas, enlace_proyecto=enlace_proyecto,
        imagen_proyecto=imagen_filename)
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('proyectos'))

# Ruta para editar proyectos
@app.route('/proyectos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_proyecto(id):
    project = Proyectos.query.get_or_404(id)
    if request.method == 'POST':
        project.nombre_proyecto = request.form['nombre_proyecto']
        project.descripcion = request.form['descripcion']
        project.tecnologias_utilizadas = request.form['tecnologias_utilizadas']
        project.enlace_proyecto = request.form['enlace_proyecto']
        imagen = request.files.get('imagen_proyecto')
        if imagen:
            imagen_filename = imagen.filename
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename))
            project.imagen_proyecto = imagen_filename
        db.session.commit()
        return redirect(url_for('proyectos'))
    return render_template('edit_proyectos.html', project=project)

# Ruta para eliminar proyectos
@app.route('/proyectos/delete/<int:id>')
@login_required
def delete_proyecto(id):
    project = Proyectos.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('proyectos'))

# Ruta para ver el CV
@app.route('/cv')
def cv():
    datos_personales = DatosPersonales.query.first()
    experiencias = ExperienciaLaboral.query.all()
    educaciones = Educacion.query.all()
    certificaciones = Certificaciones.query.all()
    habilidades = Habilidades.query.all()  # Aquí se obtienen las habilidades
    proyectos = Proyectos.query.all()
    
    return render_template('cv.html', 
                           datos_personales=datos_personales, 
                           experiencias=experiencias, 
                           educaciones=educaciones, 
                           certificaciones=certificaciones,
                           habilidades=habilidades,  # Aquí se pasan al template
                           proyectos=proyectos)


if __name__ == '__main__':
    app.run()




