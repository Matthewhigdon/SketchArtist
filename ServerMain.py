import socket
import threading
import time
import json
import random

# Use '0.0.0.0' to listen on all interfaces, so other machines on LAN can connect.
# If testing locally on the same machine, connecting with 127.0.0.1 from the client is fine.
HOST = '10.20.193.115'
PORT = 50000
TOTAL_PLAYERS = 2
ROUND_COUNT = 5
ROUND_DURATION = 60
PAUSE_DURATION = 10

clients = []
roles = {}
scores = {}
culprit_conn = None
all_players_ready = threading.Event()

def send_message(conn, message_dict):
    msg = json.dumps(message_dict).encode('utf-8')
    conn.sendall(len(msg).to_bytes(4, 'big'))
    conn.sendall(msg)

def recv_message(conn):
    try:
        length_data = conn.recv(4)
        if not length_data:
            return None
        length = int.from_bytes(length_data, 'big')
        data = conn.recv(length)
        if not data:
            return None
        return json.loads(data.decode('utf-8'))
    except:
        return None

incoming_messages = []
incoming_lock = threading.Lock()

def process_incoming_message(conn, msg):
    with incoming_lock:
        incoming_messages.append((conn, msg))

def handle_client(conn, addr):
    print(f"Player connected from {addr}")
    clients.append((conn, addr))
    # Wait until all players connected
    all_players_ready.wait()

    while True:
        msg = recv_message(conn)
        if not msg:
            # Client disconnected
            print(f"Client {addr} disconnected.")
            break
        process_incoming_message(conn, msg)
    conn.close()

def wait_for_action_from_role(role_name, action_type, timeout=ROUND_DURATION):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with incoming_lock:
            for i, (c, m) in enumerate(incoming_messages):
                if roles.get(c) == role_name and m.get('action') == action_type:
                    return incoming_messages.pop(i)
        time.sleep(0.1)
    return None

def wait_for_detective_guesses(timeout=PAUSE_DURATION):
    guesses = []
    start_time = time.time()
    while time.time() - start_time < timeout:
        with incoming_lock:
            i = 0
            while i < len(incoming_messages):
                c, m = incoming_messages[i]
                if roles.get(c) == 'detective' and m.get('action') == 'GUESS':
                    guesses.append((c, m['guess_id']))
                    incoming_messages.pop(i)
                else:
                    i += 1
        time.sleep(0.1)
    return guesses

def assign_roles():
    random.shuffle(clients)
    witness_conn, _ = clients[0]
    artist_conn, _ = clients[1]
    detective_conns = [c for c, a in clients[2:]]

    all_conns = [c for c, a in clients]
    culprit_conn = random.choice(all_conns)

    roles[witness_conn] = 'witness'
    roles[artist_conn] = 'artist'
    for dc in detective_conns:
        roles[dc] = 'detective'

    for c, a in clients:
        scores[c] = 0

    for c, a in clients:
        msg = {"action": "ASSIGN_ROLE", "role": roles[c]}
        culprit_id = all_conns.index(culprit_conn)
        if roles[c] == 'witness':
            msg["culprit_id"] = culprit_id
        send_message(c, msg)

    print("Roles assigned and ASSIGN_ROLE messages sent.")
    return culprit_conn

def broadcast(message_dict):
    for c, a in clients:
        send_message(c, message_dict)

def serialize_scores():
    score_dict = {}
    for i, (c, a) in enumerate(clients):
        score_dict[i] = scores[c]
    return score_dict

def run_game():
    global culprit_conn
    culprit_conn = assign_roles()

    for round_number in range(1, ROUND_COUNT + 1):
        broadcast({"action": "START_ROUND", "round_number": round_number})
        witness_clue = wait_for_action_from_role("witness", "CLUE", ROUND_DURATION)
        if not witness_clue:
            clue_msg = "No clue provided."
        else:
            _, clue_data = witness_clue
            clue_msg = clue_data['message']

        broadcast({"action": "CLUE", "message": clue_msg})
        guesses = wait_for_detective_guesses(PAUSE_DURATION)

        broadcast({"action": "ROUND_END", "round_number": round_number, "scores": serialize_scores()})

    broadcast({"action": "GAME_OVER", "scores": serialize_scores()})
    print("Game over. Scores sent.")

def accept_players(server_socket):
    print(f"Waiting for {TOTAL_PLAYERS} players...")
    while len(clients) < TOTAL_PLAYERS:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    all_players_ready.set()

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(f"Failed to bind to {HOST}:{PORT}: {e}")
        exit(1)

    server_socket.listen()
    print(f"Server running on {HOST}:{PORT}")

    accept_players(server_socket)
    run_game()

    for c, a in clients:
        c.close()
    server_socket.close()
    print("Server shutdown.")
