random = Math.floor(Math.random() * 1000) + 1;
client = new Paho.MQTT.Client("192.168.1.102", Number(8083), "clientId1" + random);
// set callback handlers

client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({ onSuccess: onConnect });

// called when the client connects
function onConnect() {
  document.getElementById("merda").src = "images/state_on.png";
  console.log("Mosquitto Broker Connect client");
  client.subscribe("droneInfo", { qos: 2 });
  client.subscribe("videoProcessing", { qos: 2 });
  
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:" + responseObject.errorMessage);
    document.getElementById("merda").src = "images/state_off.png";
  }
}

// called when a message arrives
function onMessageArrived(message) {
  if (message.destinationName == "droneInfo") {
    var msg = JSON.parse(message.payloadString);;
    if (msg.module_type == "droneInfo") {
      document.getElementById("progress").style.width = msg.btl+ "%";
      document.getElementById("battery").innerHTML = msg.btl + "%" + " of battery left";
    }
  }
}
