
// javascript related to google maps including:
//     initializing the map,
//     setting start and end markers,
//     getting elevation for start location,
//     getting directions and displaying route on map,
//     updating database with route duration information,
//     updating storyline modal.


var map;
var San_Francisco = {lat: 37.7749, lng: -122.4194};
var start_marker;
var end_marker;
var directionsDisplay;
var directionsService;
var elevator;
var start_elevation;
function initMap() {
    console.log("I am a map");
    directionsService = new google.maps.DirectionsService();
    map = new google.maps.Map(document.getElementById('google_map'), {
        center: San_Francisco,
        zoom: 12,
        styles: styles
    });
    console.log(map);
    start_marker = new google.maps.Marker({
        position: San_Francisco,
        draggable: true,
        map: map,
        title: 'You are here!',
        icon: '/static/face.png'
    });
    end_marker = new google.maps.Marker({
        position: San_Francisco,
        draggable: false,
        map: map,
        visible: false,
        title: 'ESCAPE!',
        icon: '/static/gps.png'
    });
    google.maps.event.addListener(map, 'click', function(event) {
        updateMarker(event.latLng);
        start_marker.setOptions({visible:true});
    });
    var geocoder = new google.maps.Geocoder();
    elevator = new google.maps.ElevationService;
    document.getElementById('geo-submit').addEventListener('click', function() {
      geocodeAddress(geocoder, map);
      start_marker.setOptions({visible:true});
    });
    var rendererOptions = {
        map: map,
        polylineOptions: {strokeColor: "black", strokeWeight: 5},
        markerOptions: {animation: "DROP",
                        icon: '/static/gps.png'}
    };
    directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
    }
function updateMarker(data){
    start_marker.setPosition(data);
}
function geocodeAddress(geocoder, map) {
    var address = document.getElementById('address').value;
    geocoder.geocode({'address': address}, function(results, status) {
        if (status === 'OK') {
            map.setCenter(results[0].geometry.location);
            updateMarker(results[0].geometry.location);
        } else {
            $("#messageBody").html('Geocode was not successful for the following reason: ' + status);
            $('#messageModal').modal("show");
        }
    });
}
function endMarker(latitude, longitude) {
    end_marker.setPosition({lat: latitude, lng: longitude});
}
function updatedHistory(result) {
    console.log(result);
    $("#messageBody").html(result["message"]);
    // $('#messageModal').modal("show");
}
function calcRoute(mode, id) {
    console.log(start_marker.getPosition().lat(), start_marker.getPosition().lng(), end_marker.getPosition().lat(), end_marker.getPosition().lng());
    var request = {
        origin: {lat: start_marker.getPosition().lat(), lng: start_marker.getPosition().lng()},
        destination: {lat: end_marker.getPosition().lat(), lng: end_marker.getPosition().lng()},
        provideRouteAlternatives: true,
        travelMode: mode
    };
    directionsService.route(request, function(result, status) {
        if (status == 'OK') {
            console.dir(request);
            directionsDisplay.setDirections(result);
            console.log(result['routes'][0]['legs'][0]['duration']['value']);
            console.log(result['routes'][0]['legs'][0]['distance']['value']);
            var directionResults = {
                "duration": result['routes'][0]['legs'][0]['duration']['value'],
                "distance": result['routes'][0]['legs'][0]['distance']['value'],
                "search_id": id
            };
            // if ((result['routes'][0]['legs'][0]['duration']['value'] / 60) > )
            $.post("/results.json", directionResults, updatedHistory);
        } else {
            $("#messageBody").html('Directions request has failed! Please try a new search. error status: '+ status);
            $('#messageModal').modal("show");
            $.post("/route_fail.json", {"search_id": id}, updatedHistory);
        }
    });
    start_marker.setOptions({visible:false});
    directionsDisplay.setMap(map);
    directionsDisplay.setPanel(document.getElementById('directionsPanel'));
}
function showPoints(results) {
    console.dir(results);
    var lat = results["latitude"];
    var lng = results["longitude"];
    endMarker(lat, lng);
    var end_elevation = results["point_elevation"].toString();
    var start_elevation = results["elevation"].toString();
    $("#escapeStory").html("<h1>"+results["message"]+"</h1>");
    $("#escapeStory").append("<h2>Your start elevation was: "+start_elevation+" meters</h2>");
    $("#escapeStory").append("<h2>Your end elevation is: "+end_elevation+" meters!</h2>");
    $('#escape-story').modal("show");
    calcRoute(results["travel_mode"].toString(), results["search_id"].toString());
}
function getPoints(start_elevation) {
    $("#escapeStory").empty();
    console.log('getting points' + start_elevation.toString());
    var formInputs = {
        "latitude": start_marker.getPosition().lat(),
        "longitude": start_marker.getPosition().lng(),
        "min_height": $("#elevationThreshold").val(),
        "max_time": $("#timeThreshold").val(),
        "travel_mode": $("#travelModes").val(),
        "elevation": start_elevation
    };
    console.log(formInputs);
    $.get("/start.json", formInputs, showPoints);
}
function getElevation(evt) {
    evt.preventDefault();
    elevator.getElevationForLocations({
        'locations': [{lat: start_marker.getPosition().lat(), lng: start_marker.getPosition().lng()}]
        }, function (results, status) {
            console.log(status);
            if (status === 'OK') {
                if (results[0]) {
                    start_elevation = results[0].elevation;
                    console.log(start_elevation);
                    getPoints(start_elevation);
                }
            }
        });
}
$("#LocationPicker").on("submit", getElevation);
