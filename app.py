from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import jinja2
import folium



app = Flask(__name__)
bootstrap = Bootstrap(app)


latlngPop = jinja2.Template("""

                   {% macro script(this, kwargs) %}

                      var {{this.get_name()}} = L.popup();
                      function latlngPop(e) {
                      data = e.latlng.lat.toFixed(6) + ", " + e.latlng.lng.toFixed(6);
                             {{this.get_name()}}.setLatLng(e.latlng)
                                                .setContent( "<br/> "+data+" <br/><a href="+data+">Click Here</a>")
                                                .openOn({{this._parent.get_name()}})
                             }
                      {{this._parent.get_name()}}.on('click', latlngPop);

                   {% endmacro %}""")


@app.route('/')
def index():
    start_coords = (16.79631, 96.16469)
    map = folium.Map(location=start_coords, zoom_start=14)
    el = folium.MacroElement().add_to(map)
    el._template = latlngPop
    map.save('templates/map.html')
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
