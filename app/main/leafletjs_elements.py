import jinja2



set_latlng_locate = jinja2.Template("""

{% macro script(this, kwargs) %}

parentWindow = window.parent;
var former_marker;

function remove_marker() { if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); } }

{{this._parent.get_name()}}.on('click', function(e) {
    
    //if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); }
    remove_marker();
    
    icon = L.AwesomeMarkers.icon(
               {"extraClasses": "fa-rotate-0", "icon": "check",
                "iconColor": "white", "markerColor": "red", "prefix": "glyphicon" }
           );
           
           var new_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
           new_marker.on('dblclick', function(e) {
               {{this._parent.get_name()}}.removeLayer(e.target);
               parentWindow.document.getElementById("latlng").value = "";
           });
           
           var lat = e.latlng.lat.toFixed(4), lng = e.latlng.lng.toFixed(4);
           new_marker.bindPopup("Latitude: " + lat + "<br>Longitude: " + lng );
           former_marker = new_marker;

           parentWindow.document.getElementById("latlng").value = "";
           var data = lat + ", " + lng;
           setTimeout( function() {
               parentWindow.document.getElementById("latlng").value = data;
           }, 2000);
});

{{this._parent.get_name()}}.on('locationfound', function (e) {
                          
    var data = e.latlng.lat.toFixed(4) + ", " + e.latlng.lng.toFixed(4);
    setTimeout( function() {
        parentWindow.document.getElementById("locate").value = data;
    }, 2000);

    var marker  = L.marker([e.latlng.lat, e.latlng.lng], {}).addTo({{this._parent.get_name()}});
    var popup = L.popup().setLatLng(e.latlng)
                         .setContent("<b>Your Current Location</b><br>" +
                                     "<br>Latitude: " + e.latlng.lat.toFixed(4) +
                                     "<br>Longitude: " + e.latlng.lng.toFixed(4))
                         .openOn({{this._parent.get_name()}});
    marker.bindPopup(popup);
});

{% endmacro %}""")


set_express_locations = jinja2.Template("""

{% macro header(this, kwargs) %}

<script src="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.css"/>

<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
<link rel="stylesheet" type="text/css" href="https://unpkg.com/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.css" />

<script src="https://unpkg.com/esri-leaflet/dist/esri-leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/esri-leaflet-geocoder@2.3.3/dist/esri-leaflet-geocoder.css">
<script src="https://unpkg.com/esri-leaflet-geocoder/dist/esri-leaflet-geocoder.js"></script>

{% endmacro %}

{% macro script(this, kwargs) %}

    map = {{this._parent.get_name()}};
    parentWindow = window.parent;
    var sender_marker=false, receiver_marker=false;
    var sender_lat, sender_lng, receiver_lat, receiver_lng;
    var routingControl;
    var result_lcg;
    var result_esri;
    var geocoder_lcg = L.Control.Geocoder.nominatim();
    /*var control = L.Control.geocoder({
                        position: 'topleft',
                        placeholder: 'Search               ',
                        geocoder: geocoder_lcg
                    }).addTo(map);*/
    var esriSearchControl = new L.esri.Geocoding.geosearch().addTo(map);
    var geocoder_esri = L.esri.Geocoding.geocodeService();
    var rej_result = { name: "", html: "", address: { Match_addr: "" } };

    function get_icon(color) {
        var icon = L.AwesomeMarkers.icon(
                        {"extraClasses": "fa-rotate-0", "icon": "check",
                         "iconColor": "white", "markerColor": color, "prefix": "glyphicon"});
        return icon;
    }

    function remove_html_tags(s) {
        return s.toString().replace( /(<([^>]+)>)/ig, "");
    }

    map.on('click', function(e) {

        var lat = e.latlng.lat.toFixed(4), lng = e.latlng.lng.toFixed(4);
        var latlng = lat + ", " + lng;
        var new_marker = L.marker().setLatLng(e.latlng);
        var marker_popup  = L.DomUtil.create('div');
        var marker_title  = L.DomUtil.create('div', 'marker_title', marker_popup);
        var esri_address  = L.DomUtil.create('div', 'esri_address', marker_popup);
        var lcg_address   = L.DomUtil.create('div', 'lcg_address', marker_popup);
        var loc_latlng = L.DomUtil.create('div', 'loc_latlng', marker_popup);
        loc_latlng.innerHTML = "<font color=blue>Lat, Lng:</font>&nbsp;" + latlng;
        var del_marker = L.DomUtil.create('div', 'del_marker', marker_popup);
        del_marker.innerHTML = '<div align=right><input class="del_marker" type="button" value="Delete"/></div>'
        var srflag;

        if (!sender_marker || !receiver_marker) {

            var rlcg = result_lcg_address();

            rlcg
                .then( (success) => { lcg_address.innerHTML = success.name; } )
                .catch( (reason) => { console.log("lcg reason", reason); } )
                .finally();

            var resri = result_esri_address();

            resri
                .then( (success) => { esri_address.innerHTML = success.address.Match_addr;
                                      result_esri = success;
                                    } )
                .catch( (reason) => { console.log("esri reason", reason); } )
                .finally( () => {
                    if (srflag) {
                        parentWindow.document.getElementById("sender_info-address").value = result_esri.address.Match_addr;
                    } else {
                        parentWindow.document.getElementById("receiver_info-address").value = result_esri.address.Match_addr;
                    }
                });

            function result_lcg_address()
            {
                return new Promise(function (resolve, reject) {
                    geocoder_lcg.reverse(e.latlng, map.options.crs.scale(map.getZoom()), function(result) {
                        if (result[0]) {
                            resolve(result[0]);
                        } else {
                            reject(rej_result);
                        }
                    });
                });
            }

            function result_esri_address()
            {
                return new Promise(function (resolve, reject) {
                    geocoder_esri.reverse().latlng(e.latlng).run(function(error, result) {
                        if (result) {
                            resolve(result);
                        } else {
                            reject(rej_result);
                        }
                    });
                });
            }
        }

        if (!sender_marker) {
            srflag = true;
            sender_marker = new_marker.setIcon(get_icon('green')).addTo(map);
            marker_title.innerHTML  = "<b style='color:green;'>Sender Location</b>";
            sender_marker.bindPopup(marker_popup);

            setTimeout( function() {
                parentWindow.document.getElementById("sender_info-location").value = latlng;
                sender_lat = lat; sender_lng = lng;
            }, 2000);

            sender_marker.on("popupopen", function (e) {
                $('.del_marker').click(function() {
                    map.removeLayer(e.target);
                    parentWindow.document.getElementById("sender_info-location").value = "";
                    parentWindow.document.getElementById("sender_info-address").value = "";
                    sender_marker = false;
                    if(routingControl) {
                        map.removeControl(routingControl);
                        routingControl = null;
                    }
                });
            });
        }
        else if (!receiver_marker) {
            srflag = false;
            receiver_marker = new_marker.setIcon(get_icon('red')).addTo(map);
            marker_title.innerHTML  = "<b style='color:red;'>Receiver Location</b>";
            receiver_marker.bindPopup(marker_popup);

            setTimeout( function() {
                parentWindow.document.getElementById("receiver_info-location").value = latlng;
                receiver_lat = lat; receiver_lng = lng;
            }, 2000);

            receiver_marker.on("popupopen", function (e) {
                $('.del_marker').click(function() {
                    map.removeLayer(e.target);
                    parentWindow.document.getElementById("receiver_info-location").value = "";
                    parentWindow.document.getElementById("receiver_info-address").value = "";
                    receiver_marker = false;
                    if(routingControl) {
                        map.removeControl(routingControl);
                        routingControl = null;
                    }
                });
            });
        }
        else {

            if(!routingControl) {

                /*
                L.Routing.control({ waypoints: [L.latLng(sender_lat, sender_lng),
                                                L.latLng(receiver_lat, receiver_lng)],
                                    routeWhileDragging: true,
                                    collapsible: true,
                                    show: false
                                }).addTo(map);
                */

                var waypoints = [{ lat: sender_lat,
                                    lng: sender_lng
                                },
                                { lat: receiver_lat,
                                    lng: receiver_lng
                                }];
                routingControl = L.Routing.control({
                    // router: new L.Routing.OSRMv1({
                    //   serviceUrl: ROUTER_SERVICE_URL
                    // }),
                    plan: new L.Routing.plan([], {
                        addWaypoints: false,
                        draggableWaypoints: false,
                        createMarker: () => undefined
                    }),
                    lineOptions: {
                        addWaypoints: false
                    },
                    collapsible: true,
                    show: false,
                    scrollbar: true
                    });

                    map.addControl(routingControl);

                    routingControl.setWaypoints(waypoints);

                }
            }
    });

{% endmacro %}""")


style_override = jinja2.Template("""

{% macro header(this, kwargs) %}

<style>
        #export {
            position: absolute;
            top: 5px;
            right: 10px;
            z-index: 999;
            background: white;
            color: black;
            padding: 6px;
            border-radius: 4px;
            font-family: 'Helvetica Neue';
            cursor: pointer;
            font-size: 12px;
            text-decoration: none;
            top: 110px;
         }

        .leaflet-control-search .search-button {
            display: block;
            float: left;
            width: 26px;
            height: 26px;
            background: url("https://cdn.jsdelivr.net/npm/leaflet-search@2.9.7/images/search-icon.png") no-repeat 2px 2px #fff;
            border-radius: 4px;
            text-align: center;
         }
         <!--> .ClassToOverrideBorders .ClassWithBorders { border: 0;} -->
         .leaflet-container .leaflet-control-search { margin-left: 8px; }
</style>

{% endmacro %}

{% macro html(this, kwargs) %}

<a href='#' id='export'>Export</a>

{% endmacro %}

""")


draw_control = jinja2.Template("""

{% macro header(this, kwargs) %}

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.css"/>

{% endmacro %}

{% macro script(this, kwargs) %}

var options = { position: "topleft",
                draw: {},
                edit: {},
               }

// FeatureGroup is to store editable layers.

var drawnItems = new L.featureGroup().addTo({{this._parent.get_name()}});

options.edit.featureGroup = drawnItems;

var draw_control = new L.Control.Draw(options).addTo({{this._parent.get_name()}});

{{this._parent.get_name()}}.on(L.Draw.Event.CREATED, function(e) {
    var layer = e.layer,
    type = e.layerType;

    //var coords = JSON.stringify(layer.toGeoJSON());

    //layer.on('click', function() {
    //      alert(coords);
    //      console.log(coords);
    //  });

    drawnItems.addLayer(layer);
});

{{this._parent.get_name()}}.on('draw:created', function(e) {
    var layer = e.layer,
    feature = layer.feature = layer.feature || {};
    feature.type = feature.type || "Feature";
    var props = feature.properties = feature.properties || {};
    props.shape_name = null;
    props.shape_desc = null;
    drawnItems.addLayer(layer);
    add_shape_popup(layer);

    //drawnItems.addLayer(e.layer);
});

document.getElementById('export').onclick = function(e) {
    var data = drawnItems.toGeoJSON();
    var convertedData = 'text/json;charset=utf-8,'
                        + encodeURIComponent(JSON.stringify(data));
    document.getElementById('export').setAttribute(
        'href', 'data:' + convertedData
    );
    document.getElementById('export').setAttribute(
        'download', "data.geojson"
    );
}

{% endmacro %}

""")


call_last = jinja2.Template("""

{% macro script(this, kwargs) %}

//For Search Control
function getGlobalProperties(prefix) {
  var keyValues = [], global = window; // window for browser environments
  for (var prop in global) {
    if (prop.indexOf(prefix) == 0) // check the prefix
      if (!prop.endsWith("searchControl"))
        keyValues.push(prop);
  }
  return keyValues[0] // build the string
}

if (!window["feature_group"])
    var feature_group = getGlobalProperties("feature_group"); //comment this while using "search_control"
    // Shape Name, Description and Edit-Save-Cancle Button for added GeoJSON
    var fg = window[feature_group];
    if (Object.keys(fg._layers).length) {
        fg.getLayers().forEach( function(layer) {
            layer.getLayers().forEach( function(layer) {
                add_shape_popup(layer, "edit"); //by_geojson = true or "edit" 
            });
        });
    }

{% endmacro %}

""")


drawn_element = jinja2.Template("""

{% macro script(this, kwargs) %}

/*
//Comment this while using "draw_control"
//"draw_control" has already added this feature
//Only for plugins.Draw + "drawn_element"
{{this._parent.get_name()}}.on('draw:created', function (event) {
    var layer = event.layer,
    feature = layer.feature = layer.feature || {}; // Intialize layer.feature

    feature.type = feature.type || "Feature"; // Intialize feature.type
    var props = feature.properties = feature.properties || {}; // Intialize feature.properties
    props.shape_name = null;
    props.shape_desc = null;
    drawnItems.addLayer(layer);
    add_shape_popup(layer);
});
*/

function make_content_html(layer, by_geojson) {
    var l = layer.toGeoJSON();
    var name = "Shape Name";
    var desc = "Shape Description";
    if (l.geometry.type == "LineString") {
        name = "Path Name";
        desc = "Path Description";
    }
    if (l.geometry.type == "Point") {
        name = "Point Name";
        desc = "Point Description";
    }
    if (layer._radius || l.geometry.type == "Polygon") {
        name = "Area Name";
        desc = "Area Descritption";
    }

    var content_html = `<span><b>${name}</b></span><br/>`+
                       '<input class="shape_name" type="text" size="25" /><br/><br/>'+
                       `<span><b>${desc}<b/></span><br/>`+
                       '<textarea class="shape_desc" cols="25" rows="5" style="resize:none;" ></textarea><br/><br/>'
    var drawn_by_drawing = '<div><input class="edit_name_desc" type="button" value="Edit" style="display:none;" />'+
                           '<input class="save_name_desc" type="button" value="Save" />&nbsp'+
                           '<input class="cancel_name_desc" type="button" value="Cancel" style="display:none;" /></div>'
    var drawn_by_geojson = '<div><input class="edit_name_desc" type="button" value="Edit" />'+
                           '<input class="save_name_desc" type="button" value="Save" style="display:none;" />&nbsp'+
                           '<input class="cancel_name_desc" type="button" value="Cancel" style="display:none;" /></div>'
    var BUTTON_STATES = drawn_by_drawing;
    if (by_geojson) {
       var BUTTON_STATES = drawn_by_geojson;
       if (by_geojson=="edit")
           return content_html+BUTTON_STATES;
       return content_html;
    }
    return content_html+BUTTON_STATES;
}

function add_shape_popup(layer, by_geojson=false) {

    layer.on("popupopen", function () {
        //content.focus();
        $('.shape_name').val(layer.feature.properties.shape_name);
        $('.shape_desc').val(layer.feature.properties.shape_desc);
        content.focus()
        if (by_geojson) {
            $('.shape_name').attr('readonly', true);
            $('.shape_desc').attr('readonly', true);
            /* Make Comment
            if (typeof feature_group != "string")
                feature_group.addLayer(layer); //use while using "search_control", comment while using "draw_control"
            if (typeof feature_group != "object")
                //window[feature_group]._layers = drawnItems._layers; //For Search Control, comment while using "search_control"
                window[feature_group].addLayer(layer);
            */
        }

        $('.edit_name_desc').click(function() {
            $('.shape_name').attr('readonly', false);
            $('.shape_desc').attr('readonly', false);
            $(this).hide().siblings('.save_name_desc, .cancel_name_desc').show();
        });
        $('.cancel_name_desc').click(function() {
            $('.shape_name').val(layer.feature.properties.shape_name);
            $('.shape_desc').val(layer.feature.properties.shape_desc);
            $('.shape_name').attr('readonly', true);
            $('.shape_desc').attr('readonly', true);
            $(this).siblings('.edit_name_desc').show();
            $(this).siblings('.save_name_desc').hide();
            $(this).hide();
            layer.closePopup();
        });
        $('.save_name_desc').click(function() {
            //save_shape_name_desc(layer);
            layer.feature.properties.shape_name = $('.shape_name').val();
            layer.feature.properties.shape_desc = $('.shape_desc').val();
            $(this).siblings('.edit_name_desc').show();
            $(this).siblings('.cancel_name_desc').hide();
            $(this).hide();
            $('.shape_name').attr('readonly', true);
            $('.shape_desc').attr('readonly', true);
            if(!by_geojson) {
            if (typeof feature_group != "string")
                feature_group.addLayer(layer); //use while using "search_control", comment while using "draw_control"
            if (typeof feature_group != "object")
                //window[feature_group]._layers = drawnItems._layers; //For Search Control, comment while using "search_control"
                window[feature_group].addLayer(layer);
            }
            layer.closePopup();
        });
    });

    var content_html = make_content_html(layer, by_geojson);
    var content = L.DomUtil.create("div"); //document.createElement("div");
    content.innerHTML = content_html;
    if(!by_geojson) {
        layer.bindPopup(content).openPopup();
    } else {
        layer.bindPopup(content);
    }

    //document.getElementById("okBtn").addEventListener("click", function() {
    //    save_shape_name_desc(layer);
    //}, false);
}

/* Make Comment because of Using Class instead of Id
function save_shape_name_desc(layer) {
     layer.feature.properties.shape_name = document.getElementById("shape_name").value;
     layer.feature.properties.shape_desc = document.getElementById("shape_desc").value;
     document.getElementById("shape_name").readOnly = "true";
     document.getElementById("shape_desc").readOnly = "true";
     layer.closePopup();
     //console.log(layer.toGeoJSON());
}
*/

{% endmacro %}""")


search_control = jinja2.Template("""

{% macro header(this, kwargs) %}

<script src="https://cdn.jsdelivr.net/npm/leaflet-search@2.9.7/dist/leaflet-search.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet-search@2.9.7/dist/leaflet-search.min.css"/>

{% endmacro %}

{% macro script(this, kwargs) %}

var feature_group = L.featureGroup(
    {}
).addTo({{this._parent.get_name()}});

var feature_group_searchControl = new L.Control.Search({
    layer: feature_group,
    propertyName: 'shape_name',
    collapsed: true,
    textPlaceholder: 'Search          ',
    position:'topleft',
    initial: false,
    hideMarkerOnCollapse: true
});

feature_group_searchControl.on('search:locationfound', function(e) {
    feature_group.setStyle(function(feature ){
        return feature.properties.style
    })

    if(e.layer._popup)
        e.layer.openPopup();
})

feature_group_searchControl.on('search:collapsed', function(e) {
    feature_group.setStyle(function(feature) {
        return feature.properties.style
    });
});

{{this._parent.get_name()}}.addControl(feature_group_searchControl);

{% endmacro %}

""")


geocoder_control = jinja2.Template("""

{% macro header(this, kwargs) %}

<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
<link rel="stylesheet" type="text/css" href="https://unpkg.com/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.css" />

{% endmacro %}

{% macro script(this, kwargs) %}

//L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {
//    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
//}).addTo({{this._parent.get_name()}});

/*
var lgc = L.Control.geocoder(
           { geocoder: L.Control.Geocoder.nominatim({
                 geocodingQueryParams: {countrycodes: "mm"}
             })
           }
          ).addTo({{this._parent.get_name()}})

lgc.on('markgeocode', function(e) {
    console.log(e);
});
*/

//DEMO
map = {{this._parent.get_name()}}

var geocoder = L.Control.Geocoder.nominatim();

    if (URLSearchParams && location.search) {
        console.log(URLSearchParams, location.search); //mine

        // parse /?geocoder=nominatim from URL
        var params = new URLSearchParams(location.search);
        var geocoderString = params.get('geocoder');

        if (geocoderString && L.Control.Geocoder[geocoderString]) {
            console.log('Using geocoder', geocoderString);
            geocoder = L.Control.Geocoder[geocoderString]();
        } else if (geocoderString) {
              console.warn('Unsupported geocoder', geocoderString);
        }
    }

var control = L.Control.geocoder({
                  query: 'Moon',
                  placeholder: 'Search here...',
                  geocoder: geocoder
              }).addTo(map);
var marker;

setTimeout(function() {
    control.setQuery('Earth');
}, 12000);

map.on('click', function(e) {
    geocoder.reverse(e.latlng, map.options.crs.scale(map.getZoom()), function(results) {
        var r = results[0];

        if (r) {
            if (marker) {
                marker.setLatLng(r.center)
                      .setPopupContent(r.html || r.name)
                      .openPopup();
            } else {
                  marker = L.marker(r.center)
                            .bindPopup(r.name)
                            .addTo(map)
                            .openPopup();
            }
        }
    });
});

{% endmacro %}

""")


esri_control = jinja2.Template("""

{% macro header(this, kwargs) %}

<!-- Load Esri Leaflet from CDN -->
<!-- <script src="https://unpkg.com/esri-leaflet@2.5.0/dist/esri-leaflet.js"
    integrity="sha512-ucw7Grpc+iEQZa711gcjgMBnmd9qju1CICsRaryvX7HJklK0pGl/prxKvtHwpgm5ZHdvAil7YPxI1oWPOWK3UQ=="
    crossorigin=""></script> -->

<!-- Load Esri Leaflet Geocoder from CDN -->
<!-- <link rel="stylesheet" href="https://unpkg.com/esri-leaflet-geocoder@2.3.3/dist/esri-leaflet-geocoder.css"
    integrity="sha512-IM3Hs+feyi40yZhDH6kV8vQMg4Fh20s9OzInIIAc4nx7aMYMfo+IenRUekoYsHZqGkREUgx0VvlEsgm7nCDW9g=="
    crossorigin=""> -->
<!-- <script src="https://unpkg.com/esri-leaflet-geocoder@2.3.3/dist/esri-leaflet-geocoder.js"
    integrity="sha512-HrFUyCEtIpxZloTgEKKMq4RFYhxjJkCiF5sDxuAokklOeZ68U2NPfh4MFtyIVWlsKtVbK5GD2/JzFyAfvT5ejA=="
    crossorigin=""></script> -->


<script src="https://unpkg.com/esri-leaflet/dist/esri-leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/esri-leaflet-geocoder@2.3.3/dist/esri-leaflet-geocoder.css">
<script src="https://unpkg.com/esri-leaflet-geocoder/dist/esri-leaflet-geocoder.js"></script>

{% endmacro %}

{% macro script(this, kwargs) %}

map = {{this._parent.get_name()}};

var esriSearchControl = new L.esri.Geocoding.geosearch().addTo(map);

var results = new L.LayerGroup().addTo(map);

esriSearchControl.on('results', function(data){
    results.clearLayers();
    for (var i = data.results.length - 1; i >= 0; i--) {
        results.addLayer( L.marker(data.results[i].latlng)
                           .bindPopup(data.results[i].text) //bindPopup(data.text)
                           .addTo(map)
                        );
    }
  });

{% endmacro %}

""")


elements = dict( set_latlng_locate=set_latlng_locate,
                 set_express_locations=set_express_locations,
                 draw_control=draw_control,
                 drawn_element=drawn_element,
                 search_control=search_control,
                 geocoder_control=geocoder_control,
                 esri_control=esri_control,
                 style_override=style_override,
                 call_last=call_last,
               )
