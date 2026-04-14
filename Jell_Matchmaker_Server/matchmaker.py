from flask import Flask, request, jsonify
import random
import string
import time

app = Flask(__name__)

# This dictionary acts as our live database in the cloud.
# Format: {"A7X9": {"ip": "12.34.56.78", "port": 5555, "last_ping": 1612345678}}
active_rooms = {}

def generate_code():
    """Generates a random 4-character uppercase code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.route('/host', methods=['POST'])
def host_room():
    """The Host's Pygame calls this to get an invite code."""
    data = request.json
    # Flask automatically detects the public IP of whoever sent the request!
    host_ip = request.remote_addr 
    host_port = data.get('port', 5555)

    # Generate a unique code
    code = generate_code()
    while code in active_rooms:
        code = generate_code()

    # Save the room to our cloud memory
    active_rooms[code] = {
        "ip": host_ip,
        "port": host_port,
        "last_ping": time.time()
    }
    
    print(f"Room {code} created at {host_ip}:{host_port}")
    return jsonify({"success": True, "code": code})

@app.route('/join/<code>', methods=['GET'])
def join_room(code):
    """A friend's Pygame calls this with the code to find the Host."""
    code = code.upper()
    if code in active_rooms:
        room_info = active_rooms[code]
        return jsonify({
            "success": True, 
            "ip": room_info["ip"], 
            "port": room_info["port"]
        })
        
    return jsonify({"success": False, "error": "Room not found or expired."}), 404

if __name__ == '__main__':
    # Runs the server on port 10000
    app.run(host='0.0.0.0', port=10000)