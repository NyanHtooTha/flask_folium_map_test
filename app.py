from flask import Flask, session, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form, FormField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
import folium
from folium import plugins
from leafletjs_elements import elements
from calculate import get_mid_point
import jinja2



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
    el._template = elements["set_latlng_locate"]
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
    el._template = elements["set_express_locations"]
    map_tem.save('templates/map.html')
    return render_template('express.html', form=form)


@app.route('/map')
def route_map():
    return render_template("map.html")


@app.route('/test')
def test():
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14, control_scale=True)
    #Search Control
    fg = folium.FeatureGroup("Drawn Layer").add_to(map_tem)
    plugins.Search(fg, search_label="shape_name", collapsed=True, placeholder='Search'+' '*10).add_to(map_tem)
    #el2 = folium.MacroElement().add_to(map_tem)
    #el2._template = elements["search_control"] #elements["geocoder_control"]
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
                    zoom_level_offset= -5, minimized=True).add_to(map_tem)
    el = folium.MacroElement().add_to(map_tem)
    el._template = elements["drawn_element"]
    map_tem.save('templates/map.html')
    return render_template("test.html")



if __name__ == '__main__':
    app.run(debug=True)
