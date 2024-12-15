# main.py
import os
import hashlib
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps

# Configurar la API de Google Generative AI
genai.configure(api_key='AIzaSyArx0mh-l9Edjpl8nbi9gae28J_fXnUbh8')

# Configuración de generación
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Variable global para el modelo actual
current_model_name = 'gemini-1.0-pro'

# Inicialización del modelo principal
model = genai.GenerativeModel(
    model_name=current_model_name,
    generation_config=generation_config
)

# Sesión de chat inicial
chat_session = model.start_chat(history=[])

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para sesiones

# Configuraciones de modelos y usuarios
AVAILABLE_MODELS = {
    'gemini-pro': 'gemini-pro',
    'gemini-1.5-pro': 'Models',
    'gemini-1.0-pro': 'gemini-1.0-pro',
    'tunedModels/aion-xghgsg5gdv5b': 'aion-1.0',
    'gemini-1.5-flash': 'gemini-1.5-flash',
    'gemini-1.5-flash-8b': 'gemini-1.5-flash-8b',
    'gemini-2.0-flash-exp': 'gemini-2.0-flash-exp',
    'gemini-exp-1121': 'gemini-exp-1121',
    'learnml-1.5-pro-experimental': 'learnml-1.5-pro-experimental'
}

# Usa una forma más segura de almacenar contraseñas
USUARIOS = {
    'admin': hashlib.sha256('-qX3NSZRuvAEpv'.encode()).hexdigest()
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        if usuario in USUARIOS and USUARIOS[usuario] == password:
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            error = 'Credenciales inválidas'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', modelos=AVAILABLE_MODELS)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    global model
    global chat_session
    global current_model_name
    user_message = request.json['message']
    
    try:
        # Verificar si es un comando para cambiar de modelo
        if '/set' in user_message:
            new_model = user_message.split(':')[1].strip()
            if new_model == 'aion-1.0':
                new_model = 'tunedModels/aion-xghgsg5gdv5b'

            if new_model in AVAILABLE_MODELS:
                # Crear un nuevo modelo con el nombre seleccionado
                model = genai.GenerativeModel(
                    model_name=new_model, 
                    generation_config=generation_config
                )
                # Reiniciar la sesión de chat con el nuevo modelo
                chat_session = model.start_chat(history=[])
                current_model_name = new_model

                return jsonify({
                    'response': f'Modelo cambiado a {current_model_name}',
                    'success': True
                })
            else:
                return jsonify({
                    'response': 'Modelo no válido',
                    'success': False
                })
        
        # Enviar mensaje y obtener respuesta manteniendo el historial
        response = chat_session.send_message(user_message)
        
        return jsonify({
            'response': response.text,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'response': f'Error: {str(e)}',
            'success': False
        })

if __name__ == '__main__':
    app.run(debug=True)