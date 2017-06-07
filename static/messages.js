// javascript related to event handlers and modals including:
//     login/registration,
//     sidebar with search history,
//     error messages.


function doMessage(result) {
    var message = result["message"];
    $("#messageBody").html(message);
    $('#messageModal').modal("show");
    if (result["success"]) {
        $("#loginbutton").hide();
        $('#loggoutbutton').show();
    }
}
function loginUser(evt) {
    evt.preventDefault();
    var formInputs = {
        "email": $("#email").val(),
        "password": $("#password").val(),
        "nickname": $("#nickname").val()
    };
    console.log(formInputs);
    $.post("/login.json", formInputs, doMessage);
}
$("#loginForm").on("submit", loginUser);
$("#loggoutbutton").on("click", function() {
    $.get("/loggout.json", doMessage);
    $("#loggoutbutton").hide();
    $("#loginbutton").show();
    $("#sidebar-body").html('<p>Please login to view search history</p>');
});
function fillSidebar(result) {
    var response = result["response"];
    var history = result["history"];
    console.log(history);
    for (var old of history) {
        $("#sidebar-body").append('<li class="active" id="'+old["search_id"]+'"><button class="btn btn-default historybtn" type="button">Start: '+old["start_ele"]+' meters End: '+old["end_ele"]+' meters<br> Parameters: '+old["min_ele"]+' meters, '+old["max_time"]+' min, '+old["travel_mode"]+'<span class="sr-only">(current)</span></button></li>');
        $("#"+old["search_id"]).data(old);
    }
}
function loadSidebar(evt) {
  $("#sidenav").attr('style', 'width: 400px');
  $("#sidebar-body").empty();
  $.get("/search_history.json", fillSidebar);
}
function closeSidebar(evt) {
    console.log(this);
  $("#sidenav").attr('style', 'width: 0');
}
function loadInfowindow(evt) {
    var stuff = this.data();
    console.log("hello");
    $("#startingplace").html('Started at: '+stuff["start_lat"]+', '+stuff["start_lng"]+', and '+stuff["start_ele"]+' meters');
    $("#endingplace").html('Ended at: '+stuff["end_lat"]+', '+stuff["end_lng"]+', and '+stuff["end_ele"]+' meters');
    $("#routeduration").html('Height parameter: '+stuff["min_ele"]+' Time parameter: '+stuff["max_time"]+' Travel mode: '+stuff["travel_mode"]);
    var impact;
    if (stuff["start_ele"] < stuff["min_ele"]) {
        var difference = stuff["end_ele"] - stuff["start_ele"];
        impact = "This route helped you gain "+ difference + " meters!";
    } else {
        impact = "You were fine where you were! but if you follow this route you'll be even safer";
    }
    $("#impactanalysis").html(impact);
    $("#impactModal").modal("show");
}
function setHeight(evt) {
    var height = $(window).height();
    $("#map").height(height);
}
$("#sidebarPointer").on("click", loadSidebar);
$("#close-sidenav").on("click", closeSidebar);
$(".sidebtn").on("click", loadInfowindow);
$(document).on("load", setHeight);
