$(document).ready(function() {

    var socket = io.connect('http://127.0.0.1:5000/chat');
    
    socket.on('connect', function() {
      socket.send({
        'text': 'User ' + sender + ' has connected',
        'category': 'alert',
        'sender': 'System'
      });
    });

    socket.on('message', function(msg) {
      $('#messages').append('<li class="list-group-item">'+msg.sender + ': ' +msg.text+'</li>')
    });

    $('#send-btn').on('click', function() {
      socket.send({
        'text': $('#msg').val(),
        'category': 'plain',
        'sender': sender
      });
      $('#msg').val('');
    });

  });
