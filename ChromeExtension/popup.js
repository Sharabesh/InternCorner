$("#submit").click(function() {
  var username = $("#username").val();
  var password = $("#password").val();
  $.ajax({
    type: "POST",
    url: "https://devinterncorner.herokuapp.com/login-ext",
    data: {
      username: username,
      password: password
    }
  }).complete(function(o) {
    j = o.responseText;
    obj = JSON.parse(j);
    if (j["success"] === 0) {
      $("#failure").fadeIn();
    } else {
      window.location="emoji-bar.html?username=" + j.username;
    }
  });
});
