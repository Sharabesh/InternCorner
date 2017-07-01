$("#submit").click(function() {
  var username = $("#username").val();
  var password = $("#password").val();

  $.ajax({
    type: "POST",
    dataType: "json",
    url: "http://localhost:5000/login-ext",
    data: {
      username: username,
      password: password
    }
  }).complete(function(o) {
    j = o.responseJSON;
    var failure = (j.username == undefined || j.password == undefined);
    if (!failure) { window.location.href="emoji-bar.html?username=" + j.username; }
  });
});
