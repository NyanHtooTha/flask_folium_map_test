from flask import Flask, session, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
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


set_latlng_locate = jinja2.Template("""

                   {% macro script(this, kwargs) %}

                      parentWindow = window.parent;
                      var former_marker;
                      {{this._parent.get_name()}}.on('click', function(e) {
                          if (former_marker){ {{this._parent.get_name()}}.removeLayer(former_marker); }
                          icon = L.AwesomeMarkers.icon(
                                     {"extraClasses": "fa-rotate-0", "icon": "check",
                                      "iconColor": "white", "markerColor": "red", "prefix": "glyphicon"});
                          var new_marker = L.marker().setLatLng(e.latlng).setIcon(icon).addTo({{this._parent.get_name()}});
                          new_marker.on('dblclick', function(e){ {{this._parent.get_name()}}.removeLayer(e.target) });
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


@app.route('/map')
def route_map():
    return render_template("map.html")



if __name__ == '__main__':
    app.run(debug=True)
