var $songs = $('#songs');

// perform log out action
$(window).bind('beforeunload', function() {
  var username = $('.js-username').val(),
      room_name = $('.js-roomname').val();
  $.post('/leave/' + room_name + '/' + username + '/');
  return 'Going to this url will log you out of this room.';
});

// By default show the top 20 songs
var top_songs = function() {
  $.get('/toptracks', function(data) {
    var res = "";
    for (var i = 0; i < Object.keys(data.data).length; i++) {
      var $element = data.data[i];
      if (res.length !== 0) {
        res += "<br>";
      }
      res += '<a value="' + $element.embedUrl + '">' + $element.name + ' &mdash; ' + $element.artist + '</a>';
    }
    $songs.html(res);

    $songs.find('a').on('click', function() {
      $songs.html('<embed src="/static/images/spinner.gif"> ');
      var url = $(this).attr('value');
      var res = '<embed src="' + url + '">';
      $songs.html(res);
    });
  });
};
top_songs();

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
