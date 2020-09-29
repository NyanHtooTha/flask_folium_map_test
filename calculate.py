import math



def get_mid_point(point_one, point_two):
    lat1, lon1 = point_one
    lat2, lon2 = point_two
    dLon = math.radians(lon2 - lon1)

    lat1 = math.radians(lat1);
    lat2 = math.radians(lat2);
    lon1 = math.radians(lon1);

    Bx = math.cos(lat2) * math.cos(dLon);
    By = math.cos(lat2) * math.sin(dLon);
    lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), math.sqrt((math.cos(lat1) + Bx) * (math.cos(lat1) + Bx) + By * By)); 
    lon3 = lon1 + math.atan2(By, math.cos(lat1) + Bx);

    return round(math.degrees(lat3),5), round(math.degrees(lon3),5)


def get_distance(point_one, point_two, unit="km"): 
    lat1, lon1 = point_one
    lat2, lon2 = point_two
    radius = 6371 #km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
    d = round(radius * c, 5) #km
    d_mi = round(d * 0.621371, 5) #mile

    return d if unit=="km" else d_mi
