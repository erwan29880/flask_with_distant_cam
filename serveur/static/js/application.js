$(document).ready(function(){
    //connection au socket
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //réception des données
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        if (numbers_received.length >= 1){
            numbers_received.shift()
        }            
        numbers_received.push(msg.number);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }

        // affichage sur la page send_to_init.html
        $('#log').html(numbers_string);
    });

});