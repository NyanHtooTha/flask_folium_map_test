from flask import Flask, session, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import folium
import jinja2



app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'this is secret string'


class TestForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    latlng = StringField('Clicked location:')
    submit = SubmitField('Submit')


set_latlng_by_onclick = jinja2.Template("""

                   {% macro script(this, kwargs) %}

                      parentWindow = window.parent;
                      {{this._parent.get_name()}}.on('click', function(e) {
                          data = e.latlng.lat.toFixed(4) + ", " + e.latlng.lng.toFixed(4);
                          parentWindow.document.getElementById("latlng").value = data;
                          }
                      );

                   {% endmacro %}""")


@app.route('/', methods=["GET", "POST"])
def index():
    form = TestForm()
    start_coords = (16.79631, 96.16469)
    map_tem = folium.Map(location=start_coords, zoom_start=14)
    map_tem.add_child(folium.LatLngPopup())
    el = folium.MacroElement().add_to(map_tem)
    el._template = set_latlng_by_onclick
    if session.get("name") and session.get("latlng"):
        mark_place = list(map(float, session.get("latlng").split(",")))
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
    map_tem.save('templates/map.html')
    if form.validate_on_submit():
        session["name"] = form.name.data
        session["latlng"] = form.latlng.data
        return redirect(url_for("index"))
    return render_template('index.html', form=form,
                            name = session.get("name"),
                            latlng = session.get("latlng") )


@app.route('/map')
def route_map():
    return render_template("map.html")



if __name__ == '__main__':
    app.run(debug=True)
