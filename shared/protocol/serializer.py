import json

from shared.protocol.packet import Packet


class Serializer:

    @staticmethod
    def serialize(packet: Packet):

        metadata = json.dumps(packet.metadata)

        if isinstance(packet.data, bytes):
            payload = packet.data.decode("latin1")
        else:
            payload = packet.data

        message = (
            f"{packet.packet_type}|"
            f"{metadata}|"
            f"{payload}"
        )

        return message.encode("latin1")

    @staticmethod
    def deserialize(data: bytes):

        message = data.decode("latin1")

        packet_type, metadata, payload = message.split("|", 2)

        packet_type = int(packet_type)

        metadata = json.loads(metadata)

        if packet_type == 1:
            data = payload
        else:
            data = payload.encode("latin1")

        return Packet(
            packet_type,
            data,
            metadata
        )

    # ---------------- Packet Framing ----------------

    @staticmethod
    def send_packet(sock, packet):

        data = Serializer.serialize(packet)

        length = len(data)

        sock.sendall(length.to_bytes(4, "big"))

        sock.sendall(data)

    @staticmethod
    def receive_packet(sock):

        length_data = b""

        while len(length_data) < 4:

            chunk = sock.recv(4 - len(length_data))

            if not chunk:
                return None

            length_data += chunk

        packet_length = int.from_bytes(length_data, "big")

        packet_data = b""

        while len(packet_data) < packet_length:

            chunk = sock.recv(
                min(4096, packet_length - len(packet_data))
            )

            if not chunk:
                return None

            packet_data += chunk

        return Serializer.deserialize(packet_data)