class Packet:

    def __init__(
        self,
        packet_type,
        data,
        metadata=None
    ):

        self.packet_type = packet_type
        self.data = data
        self.metadata = metadata or {}