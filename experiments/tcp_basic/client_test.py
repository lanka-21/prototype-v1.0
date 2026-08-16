# python -m experiments.tcp_basic.client_test

import socket
import threading

from shared.protocol.packet import Packet
from shared.protocol.serializer import Serializer
from shared.protocol.packet_types import TEXT, IMAGE, FILE, VOICE


HOST = "127.0.0.1"
PORT = 5000


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receive_messages():

    while True:

        try:

            packet = Serializer.receive_packet(client_socket)

            if packet is None:
                break

            # ---------- FILE ----------
            if packet.packet_type == FILE:

                filename = packet.metadata.get("filename")

                with open("received_" + filename, "wb") as file:
                    file.write(packet.data)

                print(f"\n>> File received: received_{filename}")

            # ---------- IMAGE ----------
            elif packet.packet_type == IMAGE:

                filename = packet.metadata.get("filename")

                with open("received_" + filename, "wb") as image:
                    image.write(packet.data)

                print(f"\n>> Image received: received_{filename}")

            # ---------- VOICE ----------
            elif packet.packet_type == VOICE:

                filename = packet.metadata.get("filename")

                with open("received_" + filename, "wb") as voice:
                    voice.write(packet.data)

                print(f"\n>> Voice received: received_{filename}")

            # ---------- TEXT ----------
            else:

                print(f"\n>> {packet.data}")

        except Exception as e:
            print(e)
            break


try:

    client_socket.connect((HOST, PORT))
    print("Connected to server successfully.")

except ConnectionRefusedError:

    print("Could not connect. Server is not running.")
    client_socket.close()
    exit()


# ---------------- Username ----------------

username = input("Enter Username : ")

username_packet = Packet(
    TEXT,
    f"__USERNAME__:{username}"
)

Serializer.send_packet(
    client_socket,
    username_packet
)

# ------------------------------------------


receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()


while True:

    message = input("You : ")

    if message.lower() == "exit":
        break

    # ---------------- Stage 9 : File Transfer ----------------
    if message.startswith("/file"):

        parts = message.split(" ", 2)

        if len(parts) < 3:
            print("Usage: /file <username> <filename>")
            continue

        receiver = parts[1]
        filename = parts[2]

        try:

            with open(filename, "rb") as file:
                file_data = file.read()

            packet = Packet(
                FILE,
                file_data,
                {
                    "receiver": receiver,
                    "filename": filename
                }
            )

            Serializer.send_packet(
                client_socket,
                packet
            )

            print("File sent to server.")

        except FileNotFoundError:
            print("File not found.")

    # ---------------- Stage 10 : Image Sharing ----------------
    # ---------------- Stage 10 : Image Sharing ----------------
    elif message.startswith("/image"):

        parts = message.split(" ", 2)

        # ---------- Broadcast Image ----------
        if len(parts) == 2:

            receiver = None
            filename = parts[1]

        # ---------- Direct Image ----------
        elif len(parts) == 3:

            receiver = parts[1]
            filename = parts[2]

        else:

            print("Usage:")
            print("/image <imagefile>")
            print("/image <username> <imagefile>")
            continue

        try:

            with open(filename, "rb") as image:
                image_data = image.read()

            packet = Packet(
                IMAGE,
                image_data,
                {
                    "receiver": receiver,
                    "filename": filename
                }
            )

            Serializer.send_packet(
                client_socket,
                packet
            )

            print("Image sent to server.")

        except FileNotFoundError:
    
           print("Image file not found.")

    # ---------------- Stage 12 : Voice Sharing ----------------
    elif message.startswith("/voice"):

        parts = message.split(" ", 2)

        # ---------- Broadcast Voice ----------
        if len(parts) == 2:

            receiver = None
            filename = parts[1]

        # ---------- Direct Voice ----------
        elif len(parts) == 3:

            receiver = parts[1]
            filename = parts[2]

        else:

            print("Usage:")
            print("/voice <voicefile>")
            print("/voice <username> <voicefile>")
            continue

        try:

            with open(filename, "rb") as voice:
                voice_data = voice.read()

            packet = Packet(
                VOICE,
                voice_data,
                {
                    "receiver": receiver,
                    "filename": filename
                }
            )

            Serializer.send_packet(
                client_socket,
                packet
            )

            print("Voice sent to server.")

        except FileNotFoundError:
            print("Voice file not found.")

    # ---------------- Normal Text ----------------
    else:

        packet = Packet(TEXT, message)

        Serializer.send_packet(
            client_socket,
            packet
        )

   


client_socket.close()

print("Socket closed.")