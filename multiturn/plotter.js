var locations = [
    ['Turn1_NW_SW', 48.7751719849,11.4096909879, 4],
    ['Turn2_S_E', 48.7749571994,11.4171988121, 5],
    ['Turn3_N_E', 48.7902749773,11.3816505382, 3],
    ['Turn4_W_S', 48.7903583135,11.3814125959, 2],
    ['Turn5_W_N',48.7880566803,11.3811085721 , 1],
    ['Turn6_NW_N',48.7366648289,11.4557780456, 6],
    ['Turn7_S_E',48.7880144539,11.3811151809 , 7]
];
var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 10,
    center: new google.maps.LatLng(48.5, 11.5),
    mapTypeId: google.maps.MapTypeId.ROADMAP
});
var infowindow = new google.maps.InfoWindow();
var marker, i;
for (i = 0; i < locations.length; i++) {
    marker = new google.maps.Marker({
        position: new google.maps.LatLng(locations[i][1], locations[i][2]),
        map: map
    });
    google.maps.event.addListener(marker, 'click', (function (marker, i) {
        return function () {
            infowindow.setContent(locations[i][0]);
            infowindow.open(map, marker);
        }
    })(marker, i));
}
