from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_URI = os.getenv('SQLALCHEMY_URI')

engine = create_engine(SQLALCHEMY_URI)


app = Flask(__name__)

# For simplicity, let's assume you have a list of subscribed users.
subscribed_users = ['user1', 'user2', 'user3']

# Dictionary to store tokens and associated users
tokens = {}

# Example message that requires a valid token to access
example_message = "This is a secret message for authorized users."

# Generate a token
import secrets

def generate_token():
    return secrets.token_hex(16)

# Verify token
def verify_token(token):
    return token in tokens

# Endpoint to generate a token
@app.route('/generate_token', methods=['POST'])
def generate_user_token():
    user_id = request.json.get('user_id')

    if user_id not in subscribed_users:
        return jsonify({'message': 'User is not subscribed'}), 401

    token = generate_token()
    tokens[token] = user_id
    return jsonify({'token': token}), 201

# Endpoint to access the example message
@app.route('/example_message', methods=['GET'])
def get_example_message():
    token = request.headers.get('Authorization')

    if not token or not verify_token(token):
        return jsonify({'message': 'Unauthorized'}), 401

    return jsonify({'message': example_message}), 200


# Runner code
if __name__ == '__main__':
    app.run()
