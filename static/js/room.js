var players = [];
var player;
var call;
var getUserMedia;
var $songs = $('#songs');
var $albums = $('#albums');
var socket;

$(document).ready(function() {
  socket = io.connect('http://' + document.domain + ':' + location.port + '/macedonia');
  player = $('.js-username').val();
  $(window).bind('beforeunload', function() {
    var username = $('.js-username').val(),
        room_name = $('.js-room').val();
    $.post('/leave/' + room_name + '/' + username + '/', function(data) { });
    return 'Going to this url will log you out of this room.';
  });

  // SONGS
  // By default show the top 20 songs
  var top_songs = function() {
    $.get('/toptracks', function(data) {
      var res = "";
      for (var i = 0; i < Object.keys(data.data).length; i++) {
        var $element = data.data[i];
        if (res.length !== 0) {
          res += "<br>";
        }
        res += '<button style="width:500px" value="' + $element.embedUrl + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
    }
    $songs.html(res);

    $songs.find('button').on('click', function() {
      $songs.html('<embed src="/static/images/spinner.gif"> ');
      var url = $(this).attr('value');
      var res = '<embed src="' + url + '">';
        $songs.html(res);
      });
    });
  };
  top_songs();

    // By default show the top 20 songs
  var trending_albums = function() {
    $.get('/trendingalbums', function(data) {
      var res = "";
      for (var i = 0; i < Object.keys(data.data).length; i++) {
        var $element = data.data[i];
        if (res.length !== 0) {
          res += "<br>";
        }
        res += '<button style="width:500px" value="' + $element.key + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
      }
      $albums.html(res);

      $albums.find('button').on('click', function() {
        var key = $(this).attr('value');
        var top_songs = function() {
          $("#albums").hide();
          $.get('/tracks/' + key, function(data) {
            var res = "";
            for (var i = 0; i < Object.keys(data.data).length; i++) {
              var $element = data.data[i];
              if (res.length !== 0) {
                res += "<br>";
              }
              res += '<button style="width:500px" value="' + $element.embedUrl + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
            }
          $songs.html(res);

          $songs.find('button').on('click', function() {
            $songs.html('<embed src="/static/images/spinner.gif"> ');
            var url = $(this).attr('value');
            var res = '<embed src="' + url + '">';
              $songs.html(res);
            });
          });
        };
        top_songs();
        $("#songs").show();
      });
    });
  };
  trending_albums();

  // By default show the top 20 songs
  var new_albums = function() {
    $.get('/newalbums', function(data) {
      var res = "";
      for (var i = 0; i < Object.keys(data.data).length; i++) {
        var $element = data.data[i];
        if (res.length !== 0) {
          res += "<br>";
        }
        res += '<button style="width:500px" value="' + $element.key + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
      }
      $albums.html(res);

      $albums.find('button').on('click', function() {
        var key = $(this).attr('value');
        var top_songs = function() {
          $("#albums").hide();
          $.get('/tracks/' + key, function(data) {
            var res = "";
            for (var i = 0; i < Object.keys(data.data).length; i++) {
              var $element = data.data[i];
              if (res.length !== 0) {
                res += "<br>";
              }
              res += '<button style="width:500px" value="' + $element.embedUrl + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
            }
          $songs.html(res);

          $songs.find('button').on('click', function() {
            $songs.html('<embed src="/static/images/spinner.gif"> ');
            var url = $(this).attr('value');
            var res = '<embed src="' + url + '">';
              $songs.html(res);
            });
          });
        };
        top_songs();
        $("#songs").show();
      });
    });
  }
  new_albums();

  // Constantly Update player list
  (function poll() {
    $.ajax({ url: "/room/" + $('.js-room').val() + '/all_players', success: function(data){
      //Update players
      players = data.data;
    }, dataType: "json", complete: poll, timeout: 2000 });
  })();

  // TODO: Make unique by room level
  // Initalize peers
  var peer = new Peer(player, {key: 'p9bjyjl6vzxpf1or'});
  peer.on('open', function(id) {
    // Enable start button
    $('#start-button').show();
  });

  // TESTED DONE
  // Confirm player ready
  $('.button-search').on('click', function() {
    socket.emit('readyPlayer', {room: $('.js-room').val(), username: player});
    $('.button-search').prop('disabled', true);
  });

  // Game ready, initialize!
  socket.on('game_ready', function() {
    // TODO NEXT
    //initGame(0, 1);
    var i = 0;
  });

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
    }
  }

  $('.button-start').on('click', function() {
    var room_name = $('.js-roomname').val();
    $.get('/room/' + room_name, function(data) {
      if (data.hasOwnProperty('error')) {
        $('.js-room-error').html(data.error);
        $('.js-room-error-wrap').attr('style', 'display: display');
      } else {
        // You have the names here
        // Don't forget to change the number in the python function to 3
        // the minimum number of people needed for a game to start
        var players = data.data;
      }
    });
  });
  // Answer the call with no media (judges)
  peer.on('call', function(call) {
    call.answer();
    if (call.peer === p1) {
      $('#p1-vid').prop('src', URL.createObjectURL(stream));
    } else {
      $('#p2-vid').prop('src', URL.createObjectURL(stream));
    }
  });

  $(".btn-get-top-chart").on('click', function() {
      top_songs();
      $("#songs").show();
  });

  $(".btn-get-trending-albums").on('click', function() {
      trending_albums();
      $("#albums").show();
  });

  $(".btn-get-new-albums").on('click', function() {
      new_albums();
      $("#albums").show();
  });

  $(".btn-option").on('click', function() {
      $(".btn-option").hide();
      $(".btn-dropdown").show();
      $("#option-list").hide();
  });

  $(".btn-dropdown").on('click', function() {
      $(".btn-option").show();
      $("#option-list").show();
      $(".btn-dropdown").hide();
      $("#songs").hide();
      $("#albums").hide();
  });
});
