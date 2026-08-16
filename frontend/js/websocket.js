const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
    console.log("Connected to SUPER-HUMAN Server");
};

socket.onmessage = (event) => {
    console.log("Message:", event.data);
};

socket.onclose = () => {
    console.log("Disconnected");
};

socket.onerror = (error) => {
    console.log(error);
};