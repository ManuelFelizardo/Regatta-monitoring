random = Math.floor(Math.random() * 1000) + 1;
client = new Paho.MQTT.Client("192.168.1.102", Number(8083), "clientId1" + random);
// set callback handlers

client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({ onSuccess: onConnect });

// called when the client connects
function onConnect() {
  console.log("Mosquitto Broker Connect client");
  if (document.getElementById("status") != null)
    document.getElementById("status").src = "images/state_on.png";
  client.subscribe("droneInfo", { qos: 2 });
  client.subscribe("videoProcessing", { qos: 2 });

}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  console.log("onConnectionLost:" + responseObject.errorMessage);
  if (responseObject.errorCode !== 0) {
    if (document.getElementById("status") != null)
      document.getElementById("status").src = "images/state_off.png";
  }
}

// called when a message arrives
function onMessageArrived(message) {
  if (message.destinationName == "droneInfo") {
    var msg = JSON.parse(message.payloadString);
    if (msg.module_type == "droneInfo") {
      if (document.getElementById("di_st") != null) {
        document.getElementById("di_st").innerHTML = "Status : " + msg.status;
        document.getElementById("di_lt").innerHTML = "Latitude : " + msg.lat;
        document.getElementById("di_lg").innerHTML = "Longitude : " + msg.log;
        document.getElementById("di_or").innerHTML = "Orientation : " + msg.ort + " º";
        document.getElementById("di_alt").innerHTML = "Altitude : " + msg.alt + " m";
        document.getElementById("progress").style.width = msg.btl + "%";
        document.getElementById("battery").innerHTML = msg.btl + "%" + " of battery left";
      }
    }
  }
  else if (message.destinationName == "videoProcessing") {
    var msg = JSON.parse(message.payloadString);
    var modal = document.getElementById('myModal_record');
    var modalContent = document.getElementById('modalcontent2_record');
    if (msg.status == "finish") {
      document.getElementById("loader_id").style = "display: none;";
      var video = '<source src="' + " http://localhost:5000/static/videos/" + msg.name + ".mp4 " + '" type="video/mp4">';
      document.getElementById("videoReplay").innerHTML = video;
      document.getElementById("videoReplay").load();
      // jQuery('#loader_id').replaceWith(jQuery(""));
      loadData(msg.name);
    }
  }
}
