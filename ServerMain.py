import socket
import threading
import time
import json
import random

HOST = '127.0.0.1'  # or use your LAN IP to allow local network connections
PORT = 5000
TOTAL_PLAYERS = 4  # Example: 1 Witness, 1 Sketch Artist, 2 Detectives
ROUND_COUNT = 5
ROUND_DURATION = 60
PAUSE_DURATION = 10

# Global state
clients = []  # list of (conn, addr)
roles = {}  # mapping: conn -> role
scores = {}  # mapping: conn -> score
culprit_conn = None
all_players_ready = threading.Event()


def send_message(conn, message_dict):
    """Send a dictionary as a JSON-encoded string."""
    msg = json.dumps(message_dict).encode('utf-8')
    # Send length first
    conn.sendall(len(msg).to_bytes(4, 'big'))
    conn.sendall(msg)


def recv_message(conn):
    """Receive a dictionary from the client, assuming length-prefix protocol."""
    length_data = conn.recv(4)
    if not length_data:
        return None
    length = int.from_bytes(length_data, 'big')
    data = conn.recv(length)
    if not data:
        return None
    return json.loads(data.decode('utf-8'))


def handle_client(conn, addr):
    # Just add client to global list once connected
    clients.append((conn, addr))
    # Wait until all players connected
    all_players_ready.wait()

    # After roles assigned, this client will receive role and possibly culprit info
    # Then it just waits for server messages and sends back guesses/clues when prompted
    # Actual input handling from clients would be triggered by their UI code.

    # This handler could listen for messages if needed:
    # While game is running, we might want to store their messages somewhere.
    while True:
        msg = recv_message(conn)
        if not msg:
            # Client disconnected
            break
        # Handle incoming messages from client
        # For example, witness clue: { "action": "CLUE", "message": "They have glasses" }
        # Detective guess: { "action": "GUESS", "guess_id": <some_id> }
        # These messages can be put into a queue or handled directly here.
        process_incoming_message(conn, msg)

    conn.close()


incoming_messages = []
incoming_lock = threading.Lock()


def process_incoming_message(conn, msg):
    with incoming_lock:
        incoming_messages.append((conn, msg))


def wait_for_action_from_role(role_name, action_type, timeout=ROUND_DURATION):
    """Wait for a specific message from a given role (e.g., witness clue)."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        with incoming_lock:
            for i, (c, m) in enumerate(incoming_messages):
                if roles[c] == role_name and m.get('action') == action_type:
                    # Return and remove from queue
                    return incoming_messages.pop(i)
        time.sleep(0.1)
    return None


def wait_for_detective_guesses(timeout=PAUSE_DURATION):
    """Wait until pause time for detectives to submit guesses."""
    # Collect guesses until time runs out or we have all guesses
    guesses = []
    start_time = time.time()
    while time.time() - start_time < timeout:
        with incoming_lock:
            # Gather all guesses
            i = 0
            while i < len(incoming_messages):
                c, m = incoming_messages[i]
                if roles[c] == 'detective' and m.get('action') == 'GUESS':
                    guesses.append((c, m['guess_id']))
                    incoming_messages.pop(i)
                else:
                    i += 1
        time.sleep(0.1)
    return guesses


def assign_roles():
    # We have TOTAL_PLAYERS in clients
    # Assign 1 witness, 1 sketch artist, rest detectives
    random.shuffle(clients)
    witness_conn, _ = clients[0]
    artist_conn, _ = clients[1]
    detective_conns = [c for c, a in clients[2:]]

    # Pick a culprit (could be anyone)
    all_conns = [c for c, a in clients]
    culprit_conn = random.choice(all_conns)

    # Assign roles
    roles[witness_conn] = 'witness'
    roles[artist_conn] = 'artist'
    for dc in detective_conns:
        roles[dc] = 'detective'

    # Scores start at 0
    for c, a in clients:
        scores[c] = 0

    # Send roles to each player
    for c, a in clients:
        msg = {
            "action": "ASSIGN_ROLE",
            "role": roles[c]
        }
        # If this is the witness, also tell them culprit index or ID
        # Let's identify culprit by their index in clients array
        culprit_id = all_conns.index(culprit_conn)  # an integer ID
        if roles[c] == 'witness':
            msg["culprit_id"] = culprit_id
        send_message(c, msg)

    return culprit_conn


def run_game():
    global culprit_conn
    culprit_conn = assign_roles()

    # 5 rounds
    for round_number in range(1, ROUND_COUNT + 1):
        # Start round
        broadcast({"action": "START_ROUND", "round_number": round_number})

        # Wait for witness clue
        # The witness must send { "action": "CLUE", "message": "They have glasses" }
        witness_clue = wait_for_action_from_role("witness", "CLUE", ROUND_DURATION)
        if not witness_clue:
            # No clue received, continue anyway or handle accordingly
            clue_msg = "No clue provided."
        else:
            _, clue_data = witness_clue
            clue_msg = clue_data['message']

        # Broadcast clue
        broadcast({"action": "CLUE", "message": clue_msg})

        # Now wait for detective guesses during PAUSE_DURATION
        guesses = wait_for_detective_guesses(PAUSE_DURATION)

        # Evaluate guesses
        correct_detectives = [c for c, g in guesses if clients[g][0] == culprit_conn]
        # If culprit_conn matches the guessed id: correct guess
        # Actually we stored culprit_id as an index in this example; we need to clarify that.
        # Let's assume guess_id is also an index of the clients list:
        # correct_detectives = []
        # for c, guess_id in guesses:
        #     if clients[guess_id][0] == culprit_conn:
        #         correct_detectives.append(c)

        # Scoring: If any detective got it right:
        # Points = 5 - (round_number - 1) = 6 - round_number
        points_awarded = 6 - round_number
        if points_awarded < 1:
            points_awarded = 1

        if correct_detectives:
            for d in correct_detectives:
                scores[d] += points_awarded
            # Witness and Artist also get points_awarded/5
            for c, a in clients:
                if roles[c] in ['witness', 'artist']:
                    scores[c] += points_awarded / 5.0
        # Could broadcast round results
        broadcast({"action": "ROUND_END", "round_number": round_number, "scores": serialize_scores()})

    # Game over
    broadcast({"action": "GAME_OVER", "scores": serialize_scores()})


def serialize_scores():
    # Convert scores to something like { "0": score, "1": score, ... }
    # Index players by their order in clients:
    score_dict = {}
    for i, (c, a) in enumerate(clients):
        score_dict[i] = scores[c]
    return score_dict


def broadcast(message_dict):
    for c, a in clients:
        send_message(c, message_dict)


def accept_players(server_socket):
    print(f"Waiting for {TOTAL_PLAYERS} players...")
    while len(clients) < TOTAL_PLAYERS:
        conn, addr = server_socket.accept()
        print(f"Player connected from {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    # Once we have all players:
    all_players_ready.set()


if __name__ == "__main__":
    # Start the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server running on {HOST}:{PORT}")

    # Wait for all players to connect
    accept_players(server_socket)

    # Run the game logic
    run_game()

    # Close all connections
    for c, a in clients:
        c.close()
    server_socket.close()
