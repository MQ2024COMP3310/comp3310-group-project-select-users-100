#Ambrose
# Import necessary libraries
from flask import Flask, request, jsonify, make_response
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Secure Coding Principle: Use environment variables for sensitive information like secret keys.

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Secure Coding Principle: Ensure tokens are passed securely via headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            # Secure Coding Principle: Validate and decode token to ensure it has not been tampered with
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        # Secure Coding Principle: Use generic error messages to avoid giving hints to attackers
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if auth.username == 'admin' and auth.password == 'password':
        # Secure Coding Principle: Token generation after successful authentication
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

# Example of a protected route
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': 'This is only available for people with valid tokens.'})
