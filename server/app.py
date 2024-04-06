from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    data = [{"id": message.id, "body": message.body, "username": message.username, "created_at": message.created_at} for
            message in messages]
    return jsonify(data)


@app.route('/messages/<int:id>', methods=['GET'])
def messages_by_id(id):
    # Returns a message by its id as JSON
    message = db.session.get(Message, id)
    if message:
        return jsonify(
            {"id": message.id, "body": message.body, "username": message.username, "created_at": message.created_at})
    else:
        return make_response(jsonify({"error": "Message not found"}), 404)


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.json
    body = data.get('body')
    username = data.get('username')

    if body and username:
        new_message = Message(body=body, username=username, created_at=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"id": new_message.id, "body": new_message.body, "username": new_message.username,
                        "created_at": new_message.created_at}), 201
    else:
        return make_response(jsonify({"error": "Missing required parameters"}), 400)


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    data = request.json
    body = data.get('body')

    if body:
        message.body = body
        db.session.commit()
        return jsonify(
            {"id": message.id, "body": message.body, "username": message.username, "created_at": message.created_at})
    else:
        return make_response(jsonify({"error": "Missing required parameters"}), 400)


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()
    return jsonify({"message": "Message deleted successfully"})


if __name__ == '__main__':
    app.run(port=5555)
