#python -m experiments.tcp_basic.server_test
import socket
import threading
print("===== NEW SERVER CODE LOADED =====")


from shared.protocol.packet import Packet
from shared.protocol.packet_types import TEXT, IMAGE, FILE, VOICE
from shared.protocol.serializer import Serializer


HOST = "0.0.0.0"
PORT = 5000


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

clients = {}

print("TCP Server Started")
print(f"Listening on {HOST}:{PORT}")
print("-" * 40)


def broadcast(sender_socket, packet):

    print("BROADCAST:", repr(packet.data))

    for client in clients:

        if client != sender_socket and clients[client] != "Unknown":

            try:
                print(" -> sending to", clients[client])

                Serializer.send_packet(
                    client,
                    packet
                )

            except Exception as e:
                print(e)


def handle_client(client_socket, client_address):

    print(f"\nClient Connected : {client_address}")

    clients[client_socket] = "Unknown"

    print(f"Total Clients : {len(clients)}")

    while True:

        try:

            packet = Serializer.receive_packet(client_socket)

            if packet is None:
                break

            print("================================")
            print("RAW :", repr(packet.data))

            # ---------------- Stage 9 : FILE ----------------
            # ---------------- Stage 10 : FILE / IMAGE ----------------
            # ---------------- Stage 9 & 10 : FILE / IMAGE ----------------
            if (
                    packet.packet_type == FILE or
                    packet.packet_type == IMAGE or
                    packet.packet_type == VOICE
                ):

                if packet.packet_type == FILE:
                    print("FILE Packet Received")

                elif packet.packet_type == IMAGE:
                    print("IMAGE Packet Received")

                else:
                    print("VOICE Packet Received")

                receiver = packet.metadata.get("receiver")

                # ---------- Broadcast ----------
                if receiver is None:

                    print("Broadcast Media")

                    for client, name in clients.items():

                        if client != client_socket and name != "Unknown":

                            Serializer.send_packet(
                                client,
                                packet
                            )

                    if packet.packet_type == FILE:
                        print("File broadcast completed.")

                    elif packet.packet_type == IMAGE:
                        print("Image broadcast completed.")

                    else:
                        print("Voice broadcast completed.")

                # ---------- Direct ----------
                else:

                    target_socket = None

                    for client, name in clients.items():

                        if name == receiver:
                            target_socket = client
                            break

                    if target_socket:

                        Serializer.send_packet(
                            target_socket,
                            packet
                        )

                        if packet.packet_type == FILE:
                            print(f"File forwarded to {receiver}")

                        elif packet.packet_type == IMAGE:
                            print(f"Image forwarded to {receiver}")

                        else:
                            print(f"Voice forwarded to {receiver}")

                    else:

                        error_packet = Packet(
                            TEXT,
                            f'User "{receiver}" is not online.'
                        )

                        Serializer.send_packet(
                            client_socket,
                            error_packet
                        )

                continue

            if packet.data.startswith("__USERNAME__:"):

                username = packet.data.replace("__USERNAME__:", "")

                clients[client_socket] = username

                print(f"{username} joined the chat.")

                join_packet = Packet(
                    TEXT,
                    f"{username} joined the chat."
                )

                broadcast(client_socket, join_packet)

                continue

            username = clients[client_socket]

            

            # ---------------- Stage 6 : DM ----------------
                        # ---------------- Stage 6 : DM ----------------
            if packet.data.startswith("/dm"):

                print("DM Command Detected :", packet.data)

                parts = packet.data.split(" ", 2)

                # Validate DM command format
                if len(parts) < 3:

                    error_packet = Packet(
                        TEXT,
                        "Invalid DM format.\nUsage: /dm <username> <message>"
                    )

                    Serializer.send_packet(
                        client_socket,
                        error_packet
                    )

                    continue

                receiver = parts[1]
                message = parts[2]

                # Prevent sending DM to yourself
                if receiver == username:

                    error_packet = Packet(
                        TEXT,
                        "You cannot send a DM to yourself."
                    )

                    Serializer.send_packet(
                        client_socket,
                        error_packet
                    )

                    continue

                target_socket = None

                # Find receiver socket
                for client, name in clients.items():

                    if name == receiver:
                        target_socket = client
                        break

                print("Target Socket :", target_socket)
                print("Command :", parts[0])
                print("Receiver :", receiver)
                print("Message :", message)

                if target_socket:

                    # Send DM to receiver
                    dm_packet = Packet(
                        TEXT,
                        f"[DM][{username}] {message}"
                    )

                    Serializer.send_packet(
                        target_socket,
                        dm_packet
                    )

                    # Send confirmation back to sender
                    sender_packet = Packet(
                        TEXT,
                        f"[DM to {receiver}] {message}"
                    )

                    Serializer.send_packet(
                        client_socket,
                        sender_packet
                    )

                    print("--------------------------------")
                    print("DM Delivered")
                    print(f"Sender   : {username}")
                    print(f"Receiver : {receiver}")
                    print(f"Message  : {message}")
                    print("--------------------------------")

                else:

                    error_packet = Packet(
                        TEXT,
                        f'User "{receiver}" is not online.'
                    )

                    Serializer.send_packet(
                        client_socket,
                        error_packet
                    )

                    print("--------------------------------")
                    print("DM Failed")
                    print(f'Sender : {username}')
                    print(f'Receiver "{receiver}" not found')
                    print("--------------------------------")

            # ---------------- Stage 7 : Online Users ----------------
            elif packet.data == "/users":

                print("Online Users Command Detected")

                online_users = "Online Users:\n"

                for name in clients.values():
                    online_users += f"- {name}\n"

                response_packet = Packet(
                    TEXT,
                    online_users
                )

                Serializer.send_packet(
                    client_socket,
                    response_packet
                )

            # ---------------- Normal Broadcast ----------------
            else:

                new_packet = Packet(
                    TEXT,
                    f"[{username}] {packet.data}"
                )

                print("SEND :", repr(new_packet.data))

                broadcast(client_socket, new_packet)

            print("================================")

        except Exception as e:

            print(e)

            break

    print(f"Client Disconnected : {client_address}")

    username = clients.get(client_socket, "Unknown")

    leave_packet = Packet(
        TEXT,
        f"{username} left the chat."
    )

    broadcast(client_socket, leave_packet)

    if client_socket in clients:
        del clients[client_socket]

    client_socket.close()


while True:

    client_socket, client_address = server_socket.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address)
    )

    thread.start()