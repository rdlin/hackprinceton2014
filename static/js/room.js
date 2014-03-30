var players = [];
var player;
var call;
var $spinner = $('#ajax-spinner');
var $results = $('#results');
var $selected = $('#selected');
var curSelected;
var socket;
var playerSelected = false;
var pl1;
var pl2;

$(document).ready(function() {
  socket = io.connect();
  player = $('.js-username').val();
  // this function logs you out when you leave the room (refresh, close window, back, e.t.c.)
  var username = $('.js-username').val(),
      room_name = $('.js-room').val();
  $(window).bind('beforeunload', function() {
    $.post('/leave/' + room_name + '/' + username + '/', function(data) {
      socket.emit('leave', {room: $('.js-room').val(), username: player});
    });
    return 'Going to this url will log you out of this room.';
  });

  // this function binds the proper listeners to the buttons that are generated when you search.
  // It checks if each button is an album or a song, and binds the appropriate embeded link
  var bindResultsListeners = function() {
    $results.find('button').on('click', function() {
      var $this = $(this);
      if ($this.hasClass('album')) {

      } else if ($this.hasClass('song')) {
        var url = $this.attr('value');
        var res = '<embed src="' + url + '">';
        var name = $this.data('name');
        var artist = $this.data('artist');
        $.get('/lyrics/'+name+'/'+artist, function(data) {
          $selected.html(res+'<p>'+data+'/>');
          $selected.slideDown();
          //set curSelected here
        });
      }
    });
  };

  // for the rdio widget, hides the results and returns options to original state
  var hideResults = function(func) {
    var onComplete = function() {
        $('#options-list').children().slideDown();
        func();
    };
    $results.slideUp(onComplete);
  };

  var showResults = function($this) {
    $children = $('#options-list').children();
    for (var i = 0; i < $children.length; i++) {
      var $child = $($children.get(i));
      if ($child.attr('id') != $this.attr('id')) {
        $child.slideUp();
      }
    }
    $results.slideDown();
  };

  var songSearchListener = function() {
    $('#song-search').on('click', function() {
      var $this = $('#song-search-input');
      $spinner.slideDown();
      $.get('/endpoint/search/' + $this.val(), function(data) {
        $results.html(data);
      });
    });
  };

  // binds a listener to top tracks
  var topTracksListener = function() {
    $('#top-tracks').on('click', function() {
      var $this = $(this);
      var $glyph = $this.children('span');
      if ($this.hasClass('selected-option')) {
        $this.removeClass('selected-option');
        hideResults(function() {
          $glyph.removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
          $results.html('');
        });
      } else {
        $spinner.slideDown();
        $.get('/toptracks/', function(data) {
          var res = "";
          for (var i = 0; i < Object.keys(data.data).length; i++) {
            var $element = data.data[i];
            if (res.length !== 0) {
              res += "<br>";
            }
            res += '<button class="song result" value="' +
              $element.embedUrl + '" data-name="' + $element.name + '" data-artist="' +
              $element.artist + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
          }
          $results.html(res);
          $spinner.hide();
          showResults($this);
          bindResultsListeners();
          $this.addClass('selected-option');
          $glyph.removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
        });
      }
    });
  };

  // binds a listener to trending albums
  var trendingAlbumsListener = function() {
  };

  // binds a listener to new albums
  var newAlbumListener = function() {

  };

  // binds all listeners needed for the rdio widget
  var bindListeners = function() {
    songSearchListener();
    topTracksListener();
    trendingAlbumsListener();
    newAlbumListener();
  };

  // By default show the top 20 songs
  // var trending_albums = function() {
  //   $.get('/trendingalbums', function(data) {
  //     var res = "";
  //     for (var i = 0; i < Object.keys(data.data).length; i++) {
  //       var $element = data.data[i];
  //       if (res.length !== 0) {
  //         res += "<br>";
  //       }
  //       res += '<button style="width:500px" value="' + $element.key + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
  //     }
  //    $albums.html(res);

  //     $albums.find('button').on('click', function() {
  //       var key = $(this).attr('value');
  //       var top_songs = function() {
  //         $("#albums").hide();
  //         $.get('/tracks/' + key, function(data) {
  //           var res = "";
  //           for (var i = 0; i < Object.keys(data.data).length; i++) {
  //             var $element = data.data[i];
  //             if (res.length !== 0) {
  //               res += "<br>";
  //             }
  //             res += '<button style="width:500px" value="' + $element.embedUrl + '" data-name="' + $element.name + '" data-artist="' + $element.artist + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
  //         }
  //         $songs.html(res);

  //         $songs.find('button').on('click', function() {
  //           $songs.html('<embed src="/static/images/spinner.gif"> ');
  //           var url = $(this).attr('value');
  //           var res = '<embed src="' + url + '">';
  //           var name = $(this).data('name');
  //           var artist = $(this).data('artist');
  //           $.get('/lyrics/'+name+'/'+artist, function(data) { $songs.html(res+'<p>'+data+'/>') });
  //           });
  //         });
  //       };
  //       top_songs();
  //       $("#songs").show();
  //     });
  //   });
  // };
  // trending_albums();

//   // By default show the top 20 songs
//   var new_albums = function() {
//     $.get('/newalbums', function(data) {
//       var res = "";
//       for (var i = 0; i < Object.keys(data.data).length; i++) {
//         var $element = data.data[i];
//         if (res.length !== 0) {
//           res += "<br>";
//         }
//         res += '<button style="width:500px" value="' + $element.key + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
//       }
//       $albums.html(res);

//       $albums.find('button').on('click', function() {
//         var key = $(this).attr('value');
//         var top_songs = function() {
//           $("#albums").hide();
//           $.get('/tracks/' + key, function(data) {
//             var res = "";
//             for (var i = 0; i < Object.keys(data.data).length; i++) {
//               var $element = data.data[i];
//               if (res.length !== 0) {
//                 res += "<br>";
//               }
//               res += '<button style="width:500px" value="' + $element.embedUrl + '" data-name="' + $element.name + '" data-artist="' + $element.artist + '">' + $element.name + ' &mdash; ' + $element.artist + '</button>';
//           }
//           $songs.html(res);

//           $songs.find('button').on('click', function() {
//             $songs.html('<embed src="/static/images/spinner.gif"> ');
//             var url = $(this).attr('value');
//             var res = '<embed src="' + url + '">';
//             var name = $(this).data('name');
//             var artist = $(this).data('artist');
//             $.get('/lyrics/'+name+'/'+artist, function(data) { debugger; $songs.html(res+'<p>'+data+'/>') });
//             });
//           });
//         };
//         top_songs();
//         $("#songs").show();
//       });
//     });
//   };

  bindListeners();

  // Constantly Update player list
  (function poll() {
    $.ajax({ url: '/room/' + $('.js-room').val() + '/all_players', success: function(data){
      //Update players
      players = data.data;
      res = '';
      for (var i = 0; i < players.length; i++) {
        res += '<h2><div class="label label-warning player"><span class="glyphicon glyphicon-user"></span> ' + players[i] + '</div></h2>';
      }
      $('#users').html(res);
    }, dataType: "json", complete: poll, timeout: 2000 });
  })();

  (function poll1() {
    if (!playerSelected) {
      $.ajax({ url: '/room/' + room_name + '/get_pair', success: function(data){
        if (data.length == 0) {
          var i = 0;
          // To nothing
        } else {
          initGame(data.p1, data.p2);
        }
      }, dataType: "json", complete: poll1, timeout: 2000 });
    }
  })();

  // TODO: Make unique by room level
  // Initalize peers
  var peer = new Peer(player, {key: 'p9bjyjl6vzxpf1or'});
  peer.on('open', function(id) {
    socket.emit('join', {room: $('.js-room').val(), username: player});
    // Enable start button
    $('#start-button').show();
  });

  // TESTED DONE
  // Confirm player ready
  $('#start-button').on('click', function() {
    socket.emit('readyPlayer', {room: $('.js-room').val(), username: player});
    $('#start-button').prop('disabled', true);
  });

  // Game ready, initialize!
  socket.on('game_ready', function(asdf) {
    $.get('/room/' + room_name, function(data) {
      initGame(data.p1, data.p2);
    });
  });

  function initGame(p1, p2) {
    // p1, p2 call all other players
    pl1 = p1;
    pl2 = p2;
    if (player === p1) {
      playerSelected = true;
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

      // Call all other players with active media stream
      navigator.getUserMedia({video: true, audio: true}, function(stream) {
        // Show player 1 stream
        window.localStream = stream;
        $('#p1-vid').prop('src', URL.createObjectURL(stream));

        for (var i = 0; i < players.length; i++) {
          if (players[i] !== player) {
            call = peer.call(players[i], stream);
          }
        }

        // Answer call from player 2
        peer.on('call', function(call) {
          call.answer(stream);
          //Show player 1 stream
          call.on('stream', function(remoteStream) {
            $('#p2-vid').prop('src', URL.createObjectURL(remoteStream));
            window.remoteStream = remoteStream;
          });
        });
      }, function(err) {
        console.log(err)
      });
    } else if (player === p2) {
      playerSelected = true;
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

      navigator.getUserMedia({video: true, audio: true}, function(stream) {
        // Show player 2 stream
        window.localStream = stream;
        $('#p1-vid').prop('src', URL.createObjectURL(stream));

        // Call all other players EXCEPT p1 with active media stream
        for (var i = 0; i < players.length; i++) {
          if (players[i] !== player) {
            call = peer.call(players[i], stream);
          }
        }

        // Answer call from player 1
        peer.on('call', function(call) {
          call.answer(stream);
          //Show player 1 stream
          call.on('stream', function(remoteStream) {
            $('#p2-vid').prop('src', URL.createObjectURL(remoteStream));
            window.remoteStream = remoteStream;
          });
        });
      }, function(err) {
        console.log(err)
      });
    } else {
      // Answer the call with no media (judges)
      peer.on('call', function(call) {
        call.answer();
        if (call.peer === p1) {
          call.on('stream', function(stream) {
            $('#p1-vid').prop('src', URL.createObjectURL(stream));
          });
        } else {
          call.on('stream', function(stream) {
            $('#p2-vid').prop('src', URL.createObjectURL(stream));
          });
        }
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
});
