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
    var content = document.createElement("textarea");

    content.addEventListener("keyup", function () {
        layer.feature.properties.area_name = content.value;
    });

    layer.on("popupopen", function () {
        content.value = layer.feature.properties.area_name;
        content.focus();
    });

    layer.bindPopup(content).openPopup();
}

{% endmacro %}""")


@app.route('/test')
def test():
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14)
    draw = plugins.Draw(export=True)
    draw.add_to(map_tem)
    el = folium.MacroElement().add_to(map_tem)
    el._template = drawn_element
    map_tem.save('templates/map.html')
    return render_template("test.html")



if __name__ == '__main__':
    app.run(debug=True)
