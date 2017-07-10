var feeling = -1;

$(".em").hover(function() {
    makeBig(this.id);
});


//Get query parameter
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function makeBig(id) {
    for (var i = 1; i < 11; i++) { makeSmall(i); }
    $("#" + id).css("transform", "scale(2,2)");
}

function makeSmall(id) {
    $("#" + id).css("transform","scale(1,1)");
}

$(".em").click(function() {
    makeBig(this.id);
    feeling = this.id;
    $(".em").unbind("mouseenter mouseleave");
});

$("#go").click(function() {
  if (feeling < 0) { console.log("Feeling not selected"); return;}
  var username = getParameterByName("username");

  $.ajax({
    type: "POST",
    dataType: "json",
    url: "https://interncorner.herokuapp.com/newPostExt",
    data: {
      username: username,
      feeling: feeling,
      anon: "",
      title: "",
      message: ""
    }
  }).complete(function(o) {
    j = o.responseText;
    var failure = (j.success == "false");
    if (!failure) { window.close(); }
  });
});
