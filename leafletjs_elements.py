import jinja2



set_latlng_locate = jinja2.Template("""

{% macro script(this, kwargs) %}

parentWindow = window.parent;
var former_marker;

function remove_marker() { if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); } }

{{this._parent.get_name()}}.on('click', function(e) {
    
    if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); }
    
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

{% macro script(this, kwargs) %}

    parentWindow = window.parent;
    var sender_marker=false, receiver_marker=false;

    {{this._parent.get_name()}}.on('click', function(e) {
        function get_icon(color) {
            var icon = L.AwesomeMarkers.icon(
                           {"extraClasses": "fa-rotate-0", "icon": "check",
                            "iconColor": "white", "markerColor": color, "prefix": "glyphicon"});
                            return icon;
        }

    var lat = e.latlng.lat.toFixed(4), lng = e.latlng.lng.toFixed(4);
    var data = lat + ", " + lng;
    if (!sender_marker) {
        var icon = get_icon('green');
        var sender_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
        sender_marker.bindPopup("Latitude: " + lat + "<br>Longitude: " + lng );

        setTimeout( function() {
            parentWindow.document.getElementById("sender_info-location").value = data;
        }, 2000);

        sender_marker.on('dblclick', function(e) {
            {{this._parent.get_name()}}.removeLayer(e.target);
            parentWindow.document.getElementById("sender_info-location").value = "";
            sender_marker = false;
        });
    }
    else if (!receiver_marker) {
        var icon = get_icon('red');
        receiver_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
        receiver_marker.bindPopup("Latitude: " + lat + "<br>Longitude: " + lng );

        setTimeout( function() {
            parentWindow.document.getElementById("receiver_info-location").value = data;
        }, 2000);

        receiver_marker.on('dblclick', function(e) {
            {{this._parent.get_name()}}.removeLayer(e.target);
            parentWindow.document.getElementById("receiver_info-location").value = "";
            receiver_marker = false;
        });
    }
    else {}
});

{% endmacro %}""")


drawn_element = jinja2.Template("""

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

var feature_group = getGlobalProperties("feature_group"); //comment this while using "search_control"

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

function make_content_html(layer) {
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
                       '<input id="shape_name" type="text" size="25" /><br/><br/>'+
                       `<span><b>${desc}<b/></span><br/>`+
                       '<textarea id="shape_desc" cols="25" rows="5" style="resize:none;" ></textarea><br/><br/>'+
                       '<div><input class="edit" type="button" value="Edit" style="display:none;" />'+
                       '<input id="okBtn" class="save" type="button" value="Save" />'+
                       '<input class="cancel" type="button" value="Cancel" style="display:none;" /></div>'
    return content_html;
}

function add_shape_popup(layer) {
     var content_html = make_content_html(layer);
     var content = document.createElement("div");
     content.innerHTML = content_html;
     layer.bindPopup(content).openPopup();

    $('.edit').click(function() {
        $('#shape_name').attr('readonly', false);
        $('#shape_desc').attr('readonly', false);
        $(this).hide().siblings('.save, .cancel').show();
    });
    $('.cancel').click(function() {
        $('#shape_name').val(layer.feature.properties.shape_name);
        $('#shape_desc').val(layer.feature.properties.shape_desc);
        $('#shape_name').attr('readonly', true);
        $('#shape_desc').attr('readonly', true);
        $(this).siblings('.edit').show();
        $(this).siblings('.save').hide();
        $(this).hide();
        //layer.closePopup();
    });
    $('.save').click(function() {
        save_shape_name_desc(layer);
        //feature_group.addLayer(layer); //use while using "search_control"
        window[feature_group]._layers = drawnItems._layers; //For Search Control
        $(this).siblings('.edit').show();
        $(this).siblings('.cancel').hide();
        $(this).hide();
    });

    //document.getElementById("okBtn").addEventListener("click", function() {
    //    save_shape_name_desc(layer);
    //}, false);

    layer.on("popupopen", function () {
        $('#shape_name').val(layer.feature.properties.shape_name);
        $('#shape_desc').val(layer.feature.properties.shape_desc);
        content.focus()
    });
}

function save_shape_name_desc(layer) {
     layer.feature.properties.shape_name = document.getElementById("shape_name").value;
     layer.feature.properties.shape_desc = document.getElementById("shape_desc").value;
     document.getElementById("shape_name").readOnly = "true";
     document.getElementById("shape_desc").readOnly = "true";
     //layer.closePopup();
     //console.log(layer.toGeoJSON());
}

{% endmacro %}""")

geocoder_control = jinja2.Template("""

{% macro header(this, kwargs) %}

<script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
<link rel="stylesheet" type="text/css" href="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css" />

{% endmacro %}

{% macro script(this, kwargs) %}

L.Control.geocoder(position="topleft").addTo({{this._parent.get_name()}})

{% endmacro %}

""")

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


elements = dict( set_latlng_locate=set_latlng_locate,
                 set_express_locations=set_express_locations,
                 drawn_element=drawn_element,
                 geocoder_control=geocoder_control,
                 search_control=search_control,
               )
