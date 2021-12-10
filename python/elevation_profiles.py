
import urllib.request
import json
import math
import matplotlib.pyplot as plt
import pandas as pd 

df = pd.read_csv("filename.csv")

def generate_elevation_plots(df):

  for i in range(len(df)):

    # Get city names.
    L1 = df['Location'][i]
    L2 = df['Location'][i+1]

    # Define the starting and ending point.
    P1 = [df['Longitude'][i], df['Latitude'][i]]
    P2 = [df['Longitude'][i+1], df['Latitude'][i+1]]

    # Select an arbitrary number of points.
    s = 100
    interval_lat = (P2[0] - P1[0]) / s #interval for latitude
    interval_lon = (P2[1] - P1[1]) / s #interval for longitude

    # Set a new variable for the starting point.
    lat0 = P1[0]
    lon0 = P1[1]

    # Create the initial lat/long list.
    lat_list = [lat0]
    lon_list = [lon0]

    # Generate points between the two lat/long pairs.
    for i in range(s):
        lat_step = lat0 + interval_lat
        lon_step= lon0 + interval_lon
        lon0 = lon_step
        lat0 = lat_step
        lat_list.append(lat_step)
        lon_list.append(lon_step)

    # Implement the Haversine function.
    def haversine(lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon1_rad = math.radians(lon1)
        lon2_rad = math.radians(lon2)

        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad

        a = math.sqrt((math.sin(delta_lat/2))**2+math.cos(lat1_rad)*math.cos(lat2_rad)*(math.sin(delta_lon/2))**2)
        d = 2 * 6371000 * math.asin(a)
        
        return d

    # Calculate the distance, using the Haversine function.
    d_list = []
    for j in range(len(lat_list)):
        lat_p = lat_list[j]
        lon_p = lon_list[j]
        dp = haversine(lat0, lon0, lat_p, lon_p) / 1000 
        d_list.append(dp)
    d_list_rev = d_list[::-1] #reverse list

    # Construct JSON.
    d_ar = [{}] * len(lat_list)
    
    for i in range(len(lat_list)):
        d_ar[i] = {"latitude":lat_list[i], "longitude":lon_list[i]}
    
    location = {"locations":d_ar}
    json_data = json.dumps(location, skipkeys=int).encode('utf8')

    # Send request to the Open Elevation service. 
    url = "https://api.open-elevation.com/api/v1/lookup"
    response = urllib.request.Request(url, json_data, headers={'Content-Type': 'application/json'})
    fp = urllib.request.urlopen(response)

    # Process the response.
    res_byte = fp.read()
    res_str = res_byte.decode("utf8")
    js_str = json.loads(res_str)
    fp.close()

    # Obtain the elevation.
    response_len = len(js_str['results'])
    elev_list = []
    for j in range(response_len):
        elev_list.append(js_str['results'][j]['elevation'])

    # Calculate statistics for the elevation profiles.
    mean_elev = round((sum(elev_list) / len(elev_list)), 3)
    min_elev = min(elev_list)
    max_elev = max(elev_list)
    distance = d_list_rev[-1]

    # Plot the elevation profiles.
    base_reg = 0
    plt.figure(figsize = (10,4))
    plt.plot(d_list_rev, elev_list)
    plt.plot([0, distance], [min_elev,min_elev], '--g', label='min: '+str(min_elev) + ' m')
    plt.plot([0, distance],[max_elev,max_elev], '--r', label='max: ' + str(max_elev) + ' m')
    plt.plot([0, distance], [mean_elev,mean_elev], '--y', label='ave: ' + str(mean_elev) + ' m')
    plt.fill_between(d_list_rev, elev_list, base_reg, alpha=0.1)
    plt.text(d_list_rev[0], elev_list[0], "P1")
    plt.text(d_list_rev[-1], elev_list[-1], "P2")
    plt.xlabel("Distance(km)")
    plt.ylabel("Elevation(m)")
    plt.title("Elevation Change: " + L1 + " to " + L2)
    plt.grid()
    plt.legend(fontsize = 'small')
    plt.savefig("plots/" + L1.split(",")[0] + "_to_" + L2.split(",")[0] + ".jpg")

generate_elevation_plots(df)