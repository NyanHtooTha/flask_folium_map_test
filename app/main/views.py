from flask import session, redirect, url_for, render_template
import folium
from folium import plugins
from .leafletjs_elements import elements
from .calculate import get_mid_point
from .tile_layers import basemaps
from . import main
from .forms import TestForm, Info, ExpressForm



@main.route('/', methods=["GET", "POST"])
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
    map_tem.save("app/static/map.html")
    if form.validate_on_submit():
        session["name"] = form.name.data
        session["latlng"] = form.latlng.data
        session["locate"] = form.locate.data
        return redirect(url_for(".index"))
    return render_template('index.html', form=form,
                            name = session.get("name"),
                            latlng = session.get("latlng") )


@main.route('/express')
def express():
    form = ExpressForm()
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14)
    plugins.Fullscreen().add_to(map_tem)
    for k in basemaps:
        basemaps[k].add_to(map_tem)
    folium.LayerControl().add_to(map_tem)
    el = folium.MacroElement().add_to(map_tem)
    el._template = elements["set_express_locations"]
    map_tem.save("app/static/map.html")
    return render_template('express.html', form=form)


#@main.route('/map')
#def route_map():
#    return render_template("map.html")


@main.route('/test')
def test():
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14, control_scale=True)
    #Search Control
    #fg = folium.FeatureGroup("Drawn Layer").add_to(map_tem) #comment this if written under Drawing Feature
    #plugins.Search(fg, search_label="shape_name", collapsed=True, placeholder='Search'+' '*10).add_to(map_tem)
    #sc = folium.MacroElement().add_to(map_tem)
    #sc._template = elements["search_control"] #not apper "Drawn Layer" on layer control
    #Full Screen
    plugins.Fullscreen().add_to(map_tem)
    #Locate Control
    plugins.LocateControl().add_to(map_tem)
    #Add the draw
    fg = folium.FeatureGroup("Drawn Layer").add_to(map_tem) #uncomment if Search Control is written under Drawing Feature
    plugins.Search(fg, search_label="shape_name", collapsed=True, placeholder='Search'+' '*10).add_to(map_tem)
    #plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=None, edit_options=None).add_to(map_tem)
    dc = folium.MacroElement().add_to(map_tem)
    de = folium.MacroElement().add_to(map_tem)
    dc._template = elements["draw_control"]
    de._template = elements["drawn_element"]

    #fg = folium.FeatureGroup("Drawn Layer").add_to(map_tem) #comment this if written under Drawing Feature
    #plugins.Search(fg, search_label="shape_name", collapsed=True, placeholder='Search'+' '*10).add_to(map_tem)
    #sc = folium.MacroElement().add_to(map_tem)
    #sc._template = elements["search_control"] #not appear "Drawn Layer" on layer control
    #de = folium.MacroElement().add_to(map_tem)
    #de._template = elements["drawn_element"]

    #Mouse position
    fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    plugins.MousePosition(position='topright', separator=' | ', prefix="Mouse:", \
                          lat_formatter=fmtr, lng_formatter=fmtr).add_to(map_tem)
    #Add measure tool
    plugins.MeasureControl(position='bottomleft', primary_length_unit='meters', secondary_length_unit='miles',\
                           primary_area_unit='sqmeters', secondary_area_unit='acres').add_to(map_tem)

    # Add custom basemaps
    for k in basemaps:
        basemaps[k].add_to(map_tem)

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
    gc = folium.MacroElement().add_to(map_tem)
    gc._template = elements["geocoder_control"]
    esri = folium.MacroElement().add_to(map_tem)
    esri._template = elements["esri_control"]

    #Style Override and Call Last must be on Last Line before Return
    style_override = folium.MacroElement().add_to(map_tem)
    style_override._template = elements["style_override"]
    call_last = folium.MacroElement().add_to(map_tem)
    call_last._template = elements["call_last"]

    #Test with GeoJSON
    a = folium.GeoJson(
        {"type":"FeatureCollection","features":[{"type":"Feature","properties":{"shape_name":"A","shape_desc":"This is AAA"},"geometry":{"type":"Polygon","coordinates":[[[96.152344,16.789258],[96.152344,16.802076],[96.177149,16.802076],[96.177149,16.789258],[96.152344,16.789258]]]}}]})
    b = folium.GeoJson(
        {"type":"FeatureCollection","features":[{"type":"Feature","properties":{"shape_name":"B","shape_desc":"This is BBB"},"geometry":{"type":"Polygon","coordinates":[[[96.128998,16.821302],[96.128998,16.856463],[96.160583,16.856463],[96.160583,16.821302],[96.128998,16.821302]]]}}]})
    #folium.features.GeoJsonPopup(fields=['shape_name', 'shape_desc'], labels=False).add_to(a)
    fg.add_child(a)
    fg.add_child(b)

    map_tem.save("app/static/map.html")
    return render_template("test.html")
