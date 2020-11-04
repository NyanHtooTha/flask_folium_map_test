import folium 



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
#basemaps['Google Maps'].add_to(map_tem)
#basemaps['Google Satellite'].add_to(map_tem)
#basemaps['Google Satellite Hybrid'].add_to(map_tem)
#basemaps['Google Terrain'].add_to(map_tem)
#basemaps['Esri Satellite'].add_to(map_tem)
