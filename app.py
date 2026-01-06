from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
import datetime
from functools import wraps
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # User interests table
    c.execute('''CREATE TABLE IF NOT EXISTS user_interests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  interest TEXT NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Career data table (for storing career information)
    c.execute('''CREATE TABLE IF NOT EXISTS careers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL,
                  description TEXT NOT NULL,
                  required_interests TEXT NOT NULL,
                  skills TEXT)''')
    
    conn.commit()
    conn.close()
    
    # Initialize default careers if not exists
    init_default_careers()

def init_default_careers():
    """Initialize default career data"""
    careers_data = [
        {
            'name': 'Software Developer',
            'description': 'Software developers design, develop, and maintain software applications. They work with programming languages, frameworks, and tools to create solutions for various industries.',
            'required_interests': ['Technology', 'Programming', 'Problem Solving', 'Mathematics', 'Innovation'],
            'skills': 'Programming, Algorithms, Software Design, Debugging'
        },
        {
            'name': 'Data Scientist',
            'description': 'Data scientists analyze complex data to extract insights and help organizations make data-driven decisions. They use statistical methods, machine learning, and data visualization.',
            'required_interests': ['Mathematics', 'Statistics', 'Technology', 'Analytics', 'Research'],
            'skills': 'Python, R, Machine Learning, Statistics, Data Visualization'
        },
        {
            'name': 'Graphic Designer',
            'description': 'Graphic designers create visual concepts using computer software or by hand to communicate ideas that inspire, inform, and captivate consumers.',
            'required_interests': ['Art', 'Design', 'Creativity', 'Visual Arts', 'Aesthetics'],
            'skills': 'Adobe Creative Suite, Typography, Color Theory, Layout Design'
        },
        {
            'name': 'Marketing Manager',
            'description': 'Marketing managers develop strategies to promote products and services, analyze market trends, and coordinate marketing campaigns across various channels.',
            'required_interests': ['Business', 'Communication', 'Analytics', 'Social Media', 'Strategy'],
            'skills': 'Digital Marketing, Market Research, Content Creation, Analytics'
        },
        {
            'name': 'Mechanical Engineer',
            'description': 'Mechanical engineers design, develop, and test mechanical devices and systems. They work on everything from engines to manufacturing equipment.',
            'required_interests': ['Engineering', 'Mathematics', 'Physics', 'Problem Solving', 'Innovation'],
            'skills': 'CAD Software, Engineering Principles, Mathematics, Physics'
        },
        {
            'name': 'Psychologist',
            'description': 'Psychologists study human behavior and mental processes. They help individuals understand and overcome psychological challenges.',
            'required_interests': ['Psychology', 'Human Behavior', 'Research', 'Communication', 'Empathy'],
            'skills': 'Research Methods, Counseling, Data Analysis, Communication'
        },
        {
            'name': 'Financial Analyst',
            'description': 'Financial analysts evaluate investment opportunities, analyze financial data, and provide recommendations to help businesses make financial decisions.',
            'required_interests': ['Finance', 'Mathematics', 'Analytics', 'Business', 'Economics'],
            'skills': 'Financial Modeling, Excel, Data Analysis, Market Research'
        },
        {
            'name': 'Biomedical Engineer',
            'description': 'Biomedical engineers combine engineering principles with medical sciences to design and create equipment, devices, and software used in healthcare.',
            'required_interests': ['Biology', 'Engineering', 'Medicine', 'Technology', 'Research'],
            'skills': 'Biomedical Systems, Engineering Design, Medical Devices, Research'
        },
        {
            'name': 'Content Writer',
            'description': 'Content writers create written content for websites, blogs, marketing materials, and other publications. They research topics and write engaging, informative content.',
            'required_interests': ['Writing', 'Communication', 'Research', 'Creativity', 'Language'],
            'skills': 'Writing, Research, SEO, Content Strategy, Editing'
        },
        {
            'name': 'Environmental Scientist',
            'description': 'Environmental scientists study the environment and develop solutions to environmental problems. They analyze data and conduct research to protect natural resources.',
            'required_interests': ['Environment', 'Science', 'Research', 'Nature', 'Sustainability'],
            'skills': 'Data Analysis, Field Research, Environmental Assessment, Report Writing'
        }
    ]
    
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    
    for career in careers_data:
        c.execute('''INSERT OR IGNORE INTO careers (name, description, required_interests, skills)
                     VALUES (?, ?, ?, ?)''',
                  (career['name'], career['description'], 
                   ','.join(career['required_interests']), career['skills']))
    
    conn.commit()
    conn.close()

# JWT Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Serve index page
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# API Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    hashed_password = generate_password_hash(password)
    c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
              (name, email, hashed_password))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Generate token
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'user': {'id': user_id, 'name': name, 'email': email}
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, password FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user[3], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user[0],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'user': {'id': user[0], 'name': user[1], 'email': user[2]}
    })

@app.route('/api/interests', methods=['GET'])
def get_interests():
    interests = [
        'Technology', 'Programming', 'Mathematics', 'Science', 'Engineering',
        'Art', 'Design', 'Creativity', 'Writing', 'Communication',
        'Business', 'Finance', 'Marketing', 'Analytics', 'Strategy',
        'Psychology', 'Human Behavior', 'Research', 'Medicine', 'Biology',
        'Environment', 'Sustainability', 'Nature', 'Problem Solving',
        'Innovation', 'Statistics', 'Visual Arts', 'Aesthetics', 'Social Media',
        'Economics', 'Physics', 'Empathy', 'Language'
    ]
    return jsonify({'interests': sorted(interests)})

@app.route('/api/user/interests', methods=['GET'])
@token_required
def get_user_interests(user_id):
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    c.execute('SELECT interest FROM user_interests WHERE user_id = ?', (user_id,))
    interests = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({'interests': interests})

@app.route('/api/user/interests', methods=['POST'])
@token_required
def save_user_interests(user_id):
    data = request.json
    interests = data.get('interests', [])
    
    if not interests:
        return jsonify({'error': 'At least one interest is required'}), 400
    
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    
    # Delete existing interests
    c.execute('DELETE FROM user_interests WHERE user_id = ?', (user_id,))
    
    # Insert new interests
    for interest in interests:
        c.execute('INSERT INTO user_interests (user_id, interest) VALUES (?, ?)',
                  (user_id, interest))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Interests saved successfully'})

@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(user_id):
    # Import the recommendation model
    from model import CareerRecommendationModel
    
    # Get user interests
    conn = sqlite3.connect('career_recommendations.db')
    c = conn.cursor()
    c.execute('SELECT interest FROM user_interests WHERE user_id = ?', (user_id,))
    user_interests = [row[0] for row in c.fetchall()]
    
    if not user_interests:
        conn.close()
        return jsonify({'error': 'Please submit your interests first'}), 400
    
    # Get all careers
    c.execute('SELECT name, description, required_interests, skills FROM careers')
    careers = c.fetchall()
    conn.close()
    
    if not careers:
        return jsonify({'error': 'No careers available'}), 500
    
    # Use the ML model to get recommendations
    model = CareerRecommendationModel()
    recommendations = model.get_recommendations(user_interests, careers)
    
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)