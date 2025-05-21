from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}

db = SQLAlchemy(app)

# ========== Models ==========

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    species = db.Column(db.String(50))
    breed = db.Column(db.String(100))
    age = db.Column(db.String(20))
    description = db.Column(db.Text)
    images = db.Column(db.Text)  # Comma-separated

class AdoptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    pet_name = db.Column(db.String(120))
    time = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    pet_name = db.Column(db.String(120))
    time = db.Column(db.String(100))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(120))
    saved_pets = db.Column(db.Text)

# ========== Helpers ==========

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ========== Routes ==========

@app.route('/api/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([
        {
            'id': pet.id,
            'name': pet.name,
            'species': pet.species,
            'breed': pet.breed,
            'age': pet.age,
            'description': pet.description,
            'images': pet.images.split(',') if pet.images else []
        } for pet in pets
    ])

@app.route('/api/pet/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return jsonify({
        'id': pet.id,
        'name': pet.name,
        'species': pet.species,
        'breed': pet.breed,
        'age': pet.age,
        'description': pet.description,
        'images': pet.images.split(',') if pet.images else []
    })

@app.route('/api/pet', methods=['POST'])
def add_pet():
    name = request.form['name']
    species = request.form['species']
    breed = request.form['breed']
    age = request.form['age']
    description = request.form['description']

    image_files = request.files.getlist('images')
    filenames = []
    for file in image_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filenames.append(filename)

    new_pet = Pet(
        name=name,
        species=species,
        breed=breed,
        age=age,
        description=description,
        images=','.join(filenames)
    )
    db.session.add(new_pet)
    db.session.commit()
    return jsonify({'message': 'Pet added successfully'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/pet/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': 'Pet deleted'})

@app.route('/api/pet/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    data = request.get_json()
    pet = Pet.query.get_or_404(pet_id)

    pet.name = data.get('name', pet.name)
    pet.species = data.get('species', pet.species)
    pet.breed = data.get('breed', pet.breed)
    pet.age = data.get('age', pet.age)
    pet.description = data.get('description', pet.description)

    db.session.commit()
    return jsonify({'message': 'Pet updated'})

@app.route('/api/adoption', methods=['POST'])
def submit_adoption():
    data = request.get_json()
    new_request = AdoptionRequest(
        name=data['name'],
        email=data['email'],
        message=data['message'],
        pet_name=data['pet_name'],
        time=data['time']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Adoption request submitted'})

@app.route('/api/adoptions', methods=['GET'])
def get_adoptions():
    forms = AdoptionRequest.query.all()
    return jsonify([{
        'name': f.name,
        'email': f.email,
        'message': f.message,
        'pet_name': f.pet_name,
        'time': f.time
    } for f in forms])

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    new_appt = Appointment(
        name=data['name'],
        email=data['email'],
        pet_name=data['pet_name'],
        time=data['time']
    )
    db.session.add(new_appt)
    db.session.commit()
    return jsonify({'message': 'Appointment created'})

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    appts = Appointment.query.all()
    return jsonify([{
        'name': a.name,
        'email': a.email,
        'pet_name': a.pet_name,
        'time': a.time
    } for a in appts])

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data['username'] == 'admin' and data['password'] == 'admin123':
        return jsonify({'message': 'Admin login successful', 'isAdmin': True})
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Login successful', 'isAdmin': False})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/save_pet', methods=['POST'])
def save_pet():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    saved = user.saved_pets.split(',') if user.saved_pets else []
    if str(data['pet_id']) not in saved:
        saved.append(str(data['pet_id']))
        user.saved_pets = ','.join(saved)
        db.session.commit()
    return jsonify({'message': 'Pet saved'})

@app.route('/api/saved_pets/<username>', methods=['GET'])
def get_saved_pets(username):
    user = User.query.filter_by(username=username).first()
    if not user or not user.saved_pets:
        return jsonify([])
    pet_ids = [int(pid) for pid in user.saved_pets.split(',')]
    pets = Pet.query.filter(Pet.id.in_(pet_ids)).all()
    return jsonify([{
        'id': pet.id,
        'name': pet.name,
        'species': pet.species,
        'breed': pet.breed,
        'age': pet.age,
        'description': pet.description,
        'images': pet.images.split(',') if pet.images else []
    } for pet in pets])

# ========== Init ==========

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
