$(window).bind('beforeunload', function() {
  var username = $('.js-username').val(),
      room_name = $('.js-roomname').val();
  $.post('/leave/' + room_name + '/' + username + '/', function(data) { });
  return 'Going to this url will log you out of this room.';
});

// By default show the top 20 songs
var top_songs = function() {
  $.get('/topchart', function(data) {
    $('#songs').html(data);
  });
};
top_songs();
