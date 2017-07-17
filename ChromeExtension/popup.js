$("#submit").click(function() {

<<<<<<< HEAD
=======


$("#loginForExt").click(function() {
>>>>>>> 80686fa7c4fd60824bd1ad03cd83a4dc9f7bcc0e
  var username = $("#username").val();
  var password = $("#password").val();
  $.ajax({
    type: "POST",
    url: "https://interncorner.herokuapp.com/login-ext",
    data: {
      username: username,
      password: password
    }
  }).complete(function(o) {
    j = o.responseText;
    console.log(j);
    obj = JSON.parse(j);
    if (obj["success"] === 0) {
      $("#failure").css('visibility','visible').hide().fadeIn();
    } else {
      window.location = "emoji-bar.html?username=" + obj.username;
    }
  });
});
