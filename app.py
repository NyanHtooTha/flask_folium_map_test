from flask import Flask, session, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form, FormField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
import folium
from folium import plugins
import jinja2
from calculate import get_mid_point



app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'this is secret string'


class TestForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    latlng = StringField('Clicked location:', default="")
    locate = StringField('Current location:', default="")
    submit = SubmitField('Submit')


class Info(Form):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone Number')
    location = StringField('Location')
    address = StringField('Address', widget=TextArea())


class ExpressForm(FlaskForm):
    sender_info = FormField(Info)
    receiver_info = FormField(Info)
    submit = SubmitField('Submit')


set_latlng_locate = jinja2.Template("""

                   {% macro script(this, kwargs) %}

                      parentWindow = window.parent;
                      var former_marker;

                      function remove_marker() { if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); } }

                      {{this._parent.get_name()}}.on('click', function(e) {
                          if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); }
                          icon = L.AwesomeMarkers.icon(
                                     {"extraClasses": "fa-rotate-0", "icon": "check",
                                      "iconColor": "white", "markerColor": "red", "prefix": "glyphicon"});
                          var new_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
                          new_marker.on('dblclick', function(e){
                              {{this._parent.get_name()}}.removeLayer(e.target)
                              parentWindow.document.getElementById("latlng").value = "";
                          });
                          var lat = e.latlng.lat.toFixed(4), lng = e.latlng.lng.toFixed(4);
                          new_marker.bindPopup("Latitude: " + lat + "<br>Longitude: " + lng );
                          former_marker = new_marker;

                          parentWindow.document.getElementById("latlng").value = "";
                          data = lat + ", " + lng;
                          setTimeout( function() {
                          parentWindow.document.getElementById("latlng").value = data;
                          }, 2000);
                      });

                      {{this._parent.get_name()}}.on('locationfound', function (e) {
                          data = e.latlng.lat.toFixed(4) + ", " + e.latlng.lng.toFixed(4);
                          setTimeout( function() {
                          parentWindow.document.getElementById("locate").value = data;
                          }, 2000);

                          var marker  = L.marker([e.latlng.lat, e.latlng.lng],
                                                 {}
                                                 ).addTo({{this._parent.get_name()}});
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
                              icon = L.AwesomeMarkers.icon(
                                         {"extraClasses": "fa-rotate-0", "icon": "check",
                                          "iconColor": "white", "markerColor": color, "prefix": "glyphicon"});
                               return icon;
                          }

                          var lat = e.latlng.lat.toFixed(4), lng = e.latlng.lng.toFixed(4);
                          var data = lat + ", " + lng;
                          if (!sender_marker) {
                              icon = get_icon('green');
                              sender_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
                              sender_marker.bindPopup("Latitude: " + lat + "<br>Longitude: " + lng );
                              setTimeout( function() {
                                  parentWindow.document.getElementById("sender_info-location").value = data;
                              }, 2000);
                              sender_marker.on('dblclick', function(e){
                                  {{this._parent.get_name()}}.removeLayer(e.target);
                                  parentWindow.document.getElementById("sender_info-location").value = "";
                                  sender_marker = false;
                              });
                          } else if (!receiver_marker) {
                              icon = get_icon('red');
                              receiver_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
                              receiver_marker.bindPopup("Latitude: " + lat + "<br>Longitude: " + lng );
                              setTimeout( function() {
                                  parentWindow.document.getElementById("receiver_info-location").value = data;
                              }, 2000);
                              receiver_marker.on('dblclick', function(e){
                                  {{this._parent.get_name()}}.removeLayer(e.target);
                                  parentWindow.document.getElementById("receiver_info-location").value = "";
                                  receiver_marker = false;
                              });
                          } else {}
                      });

                   {% endmacro %}""")


@app.route('/', methods=["GET", "POST"])
def index():
    form = TestForm()
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14)
    if session.get("name") and session.get("latlng"):
        mark_place = list(map(float, session.get("latlng").split(",")))
        map_tem = folium.Map(location=mark_place, zoom_start=16)
        if session.get("locate"):
            cur_locate = list(map(float, session.get("locate").split(",")))
            mid_point = get_mid_point(cur_locate, mark_place)
            #To play zoom_start level here later
            map_tem = folium.Map(location=mid_point, zoom_start=12)
        msg_html = '''<b>Clicked Location</b>
                      <p>Latitude: {} <br/> Longitude: {}</p>
                   '''.format(*mark_place)
        message = folium.Html(msg_html, script=True)
        folium.Marker(
               mark_place,
               popup=folium.Popup(message, max_width=300, min_width=200),
               tooltip="Hello",
               icon=folium.Icon(color='red'),
               ).add_to(map_tem)
    #map_tem.add_child(folium.LatLngPopup())
    #map_tem.add_child(folium.ClickForMarker())
    map_tem.add_child(plugins.LocateControl())
    el = folium.MacroElement().add_to(map_tem)
    el._template = set_latlng_locate
    map_tem.save('templates/map.html')
    if form.validate_on_submit():
        session["name"] = form.name.data
        session["latlng"] = form.latlng.data
        session["locate"] = form.locate.data
        return redirect(url_for("index"))
    return render_template('index.html', form=form,
                            name = session.get("name"),
                            latlng = session.get("latlng") )


@app.route('/express')
def express():
    form = ExpressForm()
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14)
    el = folium.MacroElement().add_to(map_tem)
    el._template = set_express_locations
    map_tem.save('templates/map.html')
    return render_template('express.html', form=form)


@app.route('/map')
def route_map():
    return render_template("map.html")


drawn_element = jinja2.Template("""

{% macro script(this, kwargs) %}

{{this._parent.get_name()}}.on('draw:created', function (event) {
    var layer = event.layer,
    feature = layer.feature = layer.feature || {}; // Intialize layer.feature

    feature.type = feature.type || "Feature"; // Intialize feature.type
    var props = feature.properties = feature.properties || {}; // Intialize feature.properties
    props.area_name = null;
    props.area_desc = null;
    drawnItems.addLayer(layer);
    add_area_popup(layer);
});

function add_area_popup(layer) {
    var content_html = '<span><b>Area Name</b></span><br/>'+
                       '<input id="area_name" type="text" size="25" /><br/><br/>'+
                       '<span><b>Area Description<b/></span><br/>'+
                       '<textarea id="area_desc" cols="25" rows="5" style="resize:none;" ></textarea><br/><br/>'+
                       '<div><input class="edit" type="button" value="Edit" style="display:none;" />'+
                       '<input id="okBtn" class="save" type="button" value="Save" />'+
                       '<input class="cancel" type="button" value="Cancel" style="display:none;" /></div>'
     var content = document.createElement("div");
     content.innerHTML = content_html;
     layer.bindPopup(content).openPopup();

    $('.edit').click(function() {
        $('#area_name').attr('readonly', false);
        $('#area_desc').attr('readonly', false);
        $(this).hide().siblings('.save, .cancel').show();
    });
    $('.cancel').click(function() {
        $('#area_name').val(layer.feature.properties.area_name);
        $('#area_desc').val(layer.feature.properties.area_desc);
        $('#area_name').attr('readonly', true);
        $('#area_desc').attr('readonly', true);
        $(this).siblings('.edit').show();
        $(this).siblings('.save').hide();
        $(this).hide();
        //layer.closePopup();
    });
    $('.save').click(function() {
        save_area_name_desc(layer);
        $(this).siblings('.edit').show();
        $(this).siblings('.cancel').hide();
        $(this).hide();
    });

    //document.getElementById("okBtn").addEventListener("click", function() {
    //    save_area_name_desc(layer);
    //}, false);

    layer.on("popupopen", function () {
        $('#area_name').val(layer.feature.properties.area_name);
        $('#area_desc').val(layer.feature.properties.area_desc);
        content.focus()
    });
}

function save_area_name_desc(layer) {
     layer.feature.properties.area_name = document.getElementById("area_name").value;
     layer.feature.properties.area_desc = document.getElementById("area_desc").value;
     document.getElementById("area_name").readOnly = "true";
     document.getElementById("area_desc").readOnly = "true";
     //layer.closePopup();
}

{% endmacro %}""")


@app.route('/test')
def test():
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14, control_scale=True)
    plugins.Fullscreen().add_to(map_tem)
    plugins.LocateControl().add_to(map_tem)
    #Mouse position
    fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    plugins.MousePosition(position='topright', separator=' | ', prefix="Mouse:", \
                          lat_formatter=fmtr, lng_formatter=fmtr).add_to(map_tem)
    #Add measure tool
    plugins.MeasureControl(position='bottomleft', primary_length_unit='meters', secondary_length_unit='miles',\
                           primary_area_unit='sqmeters', secondary_area_unit='acres').add_to(map_tem)
    #Add the draw
    plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=None, edit_options=None).add_to(map_tem)
    #draw = plugins.Draw(export=True)
    #draw.add_to(map_tem)

    basemaps = {
    'Google Maps': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr = 'Google Maps',
        name = 'Google Maps',
        overlay = True,
        control = True,
        show = False
    ),
    'Google Satellite': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr = 'Google Satellite',
        name = 'Google Satellite',
        overlay = True,
        control = True,
        show = False,
    ),
    'Google Terrain': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr = 'Google Terrain',
        name = 'Google Terrain',
        overlay = True,
        control = True,
        show = False
    ),
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google Satellite Hybrid',
        name = 'Google Satellite Hybrid',
        overlay = True,
        control = True,
        show = False
    ),
    'Esri Satellite': folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = True,
        control = True,
        show = False
    )
    }
    # Add custom basemaps
    basemaps['Google Maps'].add_to(map_tem)
    basemaps['Google Satellite'].add_to(map_tem)
    basemaps['Google Satellite Hybrid'].add_to(map_tem)
    basemaps['Google Terrain'].add_to(map_tem)
    basemaps['Esri Satellite'].add_to(map_tem)
    #for k in basemaps:
    #    basemaps[k].add_to(map_tem)

    #folium.raster_layers.TileLayer('Open Street Map').add_to(map_tem)
    #folium.TileLayer('Stamen Terrain', show=False).add_to(map_tem)
    #folium.TileLayer('Stamen Toner', overlay=True, show=False).add_to(map_tem)
    #folium.TileLayer('Stamen Watercolor', overlay=True, show=False).add_to(map_tem)
    #folium.TileLayer('CartoDB Positron', overlay=True, show=False).add_to(map_tem)
    #folium.TileLayer('CartoDB Dark_Matter', overlay=True, show=False).add_to(map_tem)

    # Add a layer control panel to the map
    map_tem.add_child(folium.LayerControl()) #this code must be here
    #folium.LayerControl().add_to(map_tem) #same with map_tem.add_child(folium.LayerControl())
    #Add minimap
    plugins.MiniMap(tile_layer=basemaps['Google Satellite'], toggle_display=True, width=300, height=300, \
                    zoom_level_offset= -5).add_to(map_tem)
    el = folium.MacroElement().add_to(map_tem)
    el._template = drawn_element
    map_tem.save('templates/map.html')
    return render_template("test.html")



if __name__ == '__main__':
    app.run(debug=True)
