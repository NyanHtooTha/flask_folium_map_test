from flask import Flask, render_template
import folium



app = Flask(__name__)


@app.route('/')
def index():
    start_coords = (16.79631, 96.16469)
    map = folium.Map(location=start_coords, zoom_start=14)
    map.save('templates/map.html')
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
