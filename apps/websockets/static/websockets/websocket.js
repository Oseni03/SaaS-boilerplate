let url = "ws://${window.location.host}/ws/notification/";

const socket = new WebSocket(url);

socket.onmessage(function(e) {
    let data = JSON.parse(e.data);
    console.log(data);
    
    if (data.type === "notification") {
        let notification = document.getElementById("notifications");
        notification.insertAdjacentHTML("beforeend", data.message)
    }
});

socket.onclose = function(e) {
    console.error("Websocket close unexpectedly!");
}