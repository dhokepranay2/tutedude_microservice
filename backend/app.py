from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

app = Flask(__name__)

# Fetch the MongoDB URI securely from Docker
ATLAS_URI = os.getenv("ATLAS_URI")

# Connect to MongoDB Atlas
if ATLAS_URI:
    client = MongoClient(ATLAS_URI, server_api=ServerApi('1'))
    db = client["school"]
    grades_collection = db["grades"]
    todo_collection = db["todos"]
else:
    grades_collection = None
    todo_collection = None
    print("WARNING: ATLAS_URI not found!")

# --- ROUTE: Process Grades ---
@app.route('/process_grade', methods=['POST'])
def process_grade():
    data = request.json
    student_name = data.get('name')
    student_grade = data.get('grade')

    if grades_collection is None:
        return jsonify({"status": "error", "message": "Database not connected!"}), 500

    try:
        grades_collection.insert_one({"name": student_name, "grade": int(student_grade)})
        return jsonify({"status": "success", "message": f"Saved {student_name}'s grade to MongoDB!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- ROUTE: Process To-Dos ---
@app.route('/process_todo', methods=['POST'])
def process_todo():
    data = request.json
    
    if todo_collection is None:
        return jsonify({"status": "error", "message": "Database not connected!"}), 500

    try:
        todo_collection.insert_one({
            "itemName": data.get('itemName'),
            "itemDescription": data.get('itemDescription'),
            "itemId": data.get('itemId'),
            "itemUuid": data.get('itemUuid'),
            "itemHash": data.get('itemHash')
        })
        return jsonify({"status": "success", "message": f"Saved To-Do: '{data.get('itemName')}' to MongoDB!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- GET ROUTE: Fetch all Grades ---
@app.route('/api/grades', methods=['GET'])
def get_grades():
    if grades_collection is None:
        return jsonify({"error": "Database not connected!"}), 500
        
    grades_list = []
    # Loop through MongoDB and convert the _id to a string
    for grade in grades_collection.find():
        grade['_id'] = str(grade['_id'])
        grades_list.append(grade)
        
    return jsonify(grades_list)

# --- GET ROUTE: Fetch all To-Dos ---
@app.route('/api/todos', methods=['GET'])
def get_todos():
    if todo_collection is None:
        return jsonify({"error": "Database not connected!"}), 500
        
    todo_list = []
    for todo in todo_collection.find():
        todo['_id'] = str(todo['_id'])
        todo_list.append(todo)
        
    return jsonify(todo_list)

# --- GET ROUTE: Test MongoDB Connection ---
@app.route('/api/test_db', methods=['GET'])
def test_db():
    # First, check if the environment variable made it inside the container
    if not ATLAS_URI:
        return jsonify({
            "status": "error", 
            "message": "ATLAS_URI is missing! Docker did not read your .env file."
        }), 500
    
    try:
        # Use PyMongo's built-in 'ping' command to force a connection test
        client.admin.command('ping')
        return jsonify({
            "status": "success", 
            "message": "✅ Ping successful! Flask is securely connected to MongoDB Atlas."
        }), 200
    except Exception as e:
        # If the password is wrong, or IP is blocked, it will print the exact reason here
        return jsonify({
            "status": "error", 
            "message": f"❌ MongoDB Connection Failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker
    app.run(host='0.0.0.0', port=5000)