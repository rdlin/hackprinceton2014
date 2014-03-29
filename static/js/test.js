var players = [];
var player;
var call;
var getUserMedia;

$(document).ready(function() {
  // TODO: Make unique by room level
  var peer = new Peer(player, {key: 'p9bjyjl6vzxpf1or'});
  peer.on('open', function(id) {
    console.log('Peer open with id ' + id);
  });

  $('#start-button').on('click', function() {
    data = findPlayers();
    initGame(data.p1, data.p2);
  });

  function findPlayers() {
    $.get('/randomizePlayers', function(data) {
      return data;
    });
  }

  function initGame(p1, p2) {
    // p1, p2 call all other players
    if (player === p1) {
      getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

      // Call all other players with active media stream
      getUserMedia({video: true, audio: true}, function(stream) {
        // Show player 1 stream
        window.localStream = stream;
        $('#p1-vid').prop('src', URL.createObjectURL(stream));

        for (var i = 0; i < players.length; i++) {
          call = peer.call(players[i], stream);
        }

        // Show player 2 stream
        call.on('stream', function(remoteStream) {
          if (remoteStream) {
            $('#p2-vid').prop('src', URL.createObjectURL(remoteStream));
            window.remoteStream = remoteStream;
          }
        });
      }, function(err) {
        //Failed to initalize stream, pick next player

      });
    } else if (player === p2) {
      getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

      getUserMedia({video: true, audio: true}, function(stream) {
        // Show player 2 stream
        window.localStream = stream;
        $('#p1-vid').prop('src', URL.createObjectURL(stream));

        // Call all other players EXCEPT p1 with active media stream
        for (var i = 0; i < players.length; i++) {
          if (players[i] !== p1) {
            call = peer.call(players[i], stream);
          }
        }

        // Answer call from player 1
        peer.on('call', function(call) {
          call.answer(stream);
        });

        //Show player 1 stream
        call.on('stream', function(remoteStream) {
          if (remoteStream) {
            $('#p2-vid').prop('src', URL.createObjectURL(remoteStream));
            window.remoteStream = remoteStream;
          }
        });
      });
    } else {
      // Answer the call with no media (judges)
      peer.on('call', function(call) {
        call.answer();
        if (call.peer === p1) {
          $('#p1-vid').prop('src', URL.createObjectURL(stream));
        } else {
          $('#p2-vid').prop('src', URL.createObjectURL(stream));
        }
      });
    }
  }
});
