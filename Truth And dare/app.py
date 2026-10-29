from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# The Single Source of Truth
game_state = {
    "players": [],       # List of player names
    "current_turn": "",  # Whose turn is it?
    "status": "waiting", # 'waiting', 'choosing' (Truth or Dare), 'answering'
    "current_prompt": "" # The actual truth question or dare
}

# Some dummy questions for the game
TRUTHS = ["What is your most embarrassing memory?", "Who is your best friend?", "what is the name of your secret crush."]
DARES = ["Do 10 pushups right now.", "Sing the chorus of your favorite song loudly.", "Dancing to a panjabi song in front of the girls across the way."
         , ]
import random

@app.route('/')
def index():
    # We will create this HTML file in the next step
    return render_template('index.html')

@socketio.on('join_game')
def handle_join(username):
    if username not in game_state["players"]:
        game_state["players"].append(username)
    
    # If this is the first player, make it their turn
    if len(game_state["players"]) == 1:
        game_state["current_turn"] = username
        game_state["status"] = "choosing"

    # Broadcast the updated state to EVERYONE
    emit('state_update', game_state, broadcast=True)

@socketio.on('choose_action')
def handle_choice(data):
    choice = data.get('choice') # 'truth' or 'dare'
    
    if choice == 'truth':
        game_state['current_prompt'] = random.choice(TRUTHS)
    else:
        game_state['current_prompt'] = random.choice(DARES)
        
    game_state['status'] = 'answering'
    emit('state_update', game_state, broadcast=True)

@socketio.on('next_turn')
def handle_next_turn():
    # Move to the next player in the list
    players = game_state["players"]
    if players:
        current_index = players.index(game_state["current_turn"])
        next_index = (current_index + 1) % len(players)
        
        game_state["current_turn"] = players[next_index]
        game_state["status"] = "choosing"
        game_state["current_prompt"] = ""
        
        emit('state_update', game_state, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
    
@socketio.on('send_answer')
def handle_answer(data):
    # Answer sabhi players ko bhej do
    emit('show_answer', data, broadcast=True)