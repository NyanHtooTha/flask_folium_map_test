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


@app.route('/', methods=["GET", "POST"])
def index():
    form = TestForm()
    start_coords = (16.79631, 96.16469)
    map = folium.Map(location=start_coords, zoom_start=14)
    el = folium.MacroElement().add_to(map)
    el._template = latlngPop
    map.save('templates/map.html')
    session["mapid"] = "map_"+map._id
    if form.validate_on_submit():
        session["name"] = form.name.data
        session["latlng"] = form.latlng.data
        return redirect(url_for("index", mapid=session.get("mapid")))
    return render_template('index.html', form=form,
                            mapid=session.get("mapid"),
                            name = session.get("name"),
                            latlng = session.get("latlng") )


@app.route('/map')
def map():
    return render_template("map.html")



if __name__ == '__main__':
    app.run(debug=True)
