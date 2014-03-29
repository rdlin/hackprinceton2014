var $songs = $('#songs');

$(window).bind('beforeunload', function() {
  var username = $('.js-username').val(),
      room_name = $('.js-roomname').val();
  $.post('/leave/' + room_name + '/' + username + '/', function(data) { });
  return 'Going to this url will log you out of this room.';
});

// By default show the top 20 songs
var top_songs = function() {
  $.get('/toptracks', function(data) {
    var res = "";
    for (var i = 0; i < Object.keys(data.data).length; i++) {
      var $element = data.data[i];
      if (res.length != 0) {
        res += "<br>";
      }
      res += '<a value="' + $element.embedUrl + '">' + $element.name + ' &mdash; ' + $element.artist + '</a>';
    }
    $songs.html(res);
    
    $songs.find('a').on('click', function() {
      var url = $(this).attr('value');
      var res = '<embed src="' + url + '">';
      $songs.html(res);
    });
  });
};
top_songs();
