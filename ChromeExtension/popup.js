


$("#submit").click(function() {
  var username = $("#username").val();
  var password = $("#password").val();
  console.log("HERE");
  $.ajax({
    type: "POST",
    url: "https://devinterncorner.herokuapp.com/login-ext",
    data: {
      username: username,
      password: password
    }
  }).complete(function(o) {
    j = o.responseText;
    console.log(j);
    obj = JSON.parse(j);
    if (obj["success"] === 0) {
      $("#failure").fadeIn();
    } else {
      window.location = "emoji-bar.html?username=" + obj.username;
    }
  });
});
