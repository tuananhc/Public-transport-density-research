from UsefulMethods import distance, random_points_within
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import sys

import warnings
warnings.filterwarnings("ignore")

LONGLATTOKM = 111

# read the shape file of Victoria suburb
plt.rcdefaults() 
victoria_map = gpd.read_file('./ll_gda94/sde_shape/whole/VIC/VMLITE/layer/vmlite_postcode_polygon.shp')
victoria_map = victoria_map.to_crs({'init': 'epsg:4326'})
def distance(x1,y1,x2,y2):
    return np.sqrt((x1-x2)**2+(y1-y2)**2)

# read the car number dataset
car_dict = pd.read_csv("carNumber.csv").set_index('Postcode').to_dict()
# function to get car for a postcode
def getCar(postcode):
    try:
        temp = car_dict['Number of Car'][int(postcode)]
    except:
        temp = np.NaN
    return temp

# take the position of bus stops since we limited our region
transport_pd = pd.read_csv('material/metro_' + sys.argv[1]  + '.csv', encoding = 'ISO-8859-1')
allpoint = []
for index, row in transport_pd.iterrows():
    allpoint.append(Point(row[" LONGITUDE"], row[" LATITUDE"]))

# count the number of stops in polygon
def counter(polygon):
    total = 0
    for point in allpoint:
        if point.within(polygon):
            total += 1
    return total

# take the stops within a polygon
def takeInnerStop(polygon, allpoint):
    inner = []
    for point in allpoint:
        if point.within(polygon):
            inner.append(point)
    return inner

# take the centroid of Melbourne CBD
melbournePolygon = victoria_map.loc[victoria_map['POSTCODE']=='3000'].set_index('POSTCODE')
melbournePolygon = melbournePolygon.loc['3000', 'geometry']
melbourneCentroid = melbournePolygon.centroid
# calculate distance to the centroid
def distanceToCentroid(polygon):
    return distance(polygon.centroid.x, polygon.centroid.y, melbourneCentroid.x, melbourneCentroid.y)

# calculate average distance to a stop
def avgDistanceToStopAnySurb(polygon):
    inner = takeInnerStop(polygon, allpoint)
    if inner:
        samplesPoint = random_points_within(polygon, 100)
        totalDistance = 0
        for point in samplesPoint:
            tempDistance = distance(inner[0].x, inner[0].y, point.x, point.y)
            for stop in inner:
                temp = distance(stop.x, stop.y, point.x, point.y)
                if temp < tempDistance:
                    tempDistance = temp
            totalDistance += tempDistance
        return (totalDistance * LONGLATTOKM/len(samplesPoint))
    else:
        point = polygon.centroid
        tempDistance = distance(allpoint[0].x, allpoint[0].y, point.x, point.y)
        for stop in allpoint:
            temp = distance(stop.x, stop.y, point.x, point.y)
            if temp < tempDistance:
                tempDistance = temp
        return (tempDistance * LONGLATTOKM)

# limit our region
victoria_map['counter'] = victoria_map['geometry'].apply(counter)
victoria_map['distanceToCentroid'] = victoria_map['geometry'].apply(distanceToCentroid)
temp = victoria_map[victoria_map['counter'] > 0]['distanceToCentroid'].max()
victoria_map = victoria_map[victoria_map['distanceToCentroid']<=temp]
victoria_map['centroidX'] = victoria_map['geometry'].centroid.x
victoria_map['centroidY'] = victoria_map['geometry'].centroid.y
xMax = victoria_map[victoria_map['counter'] > 0]['centroidX'].max()
xMin = victoria_map[victoria_map['counter'] > 0]['centroidX'].min()
yMax = victoria_map[victoria_map['counter'] > 0]['centroidY'].max()
yMin = victoria_map[victoria_map['counter'] > 0]['centroidY'].min()
victoria_map = victoria_map[victoria_map['centroidX']<=xMax]
victoria_map = victoria_map[victoria_map['centroidX']>=xMin]
victoria_map = victoria_map[victoria_map['centroidY']<=yMax]
victoria_map = victoria_map[victoria_map['centroidY']>=yMin]

# Calculate the data for plotting
victoria_map['avgDis'] = victoria_map['geometry'].apply(avgDistanceToStopAnySurb)
victoria_map['car'] = victoria_map['POSTCODE'].apply(getCar)
victoria_map["area"] = victoria_map['geometry'].area*110*110

# Plot the data and save figure
listCluster = []
xlist = []
ylist = []
for index, row in victoria_map.iterrows():
    if (not np.isnan(row["car"])) and (not np.isnan(row["avgDis"])):
        listCluster.append([row["car"], row["avgDis"]])
        xlist.append(row["car"])
        ylist.append(row["avgDis"])

for x,y in listCluster:
    plt.scatter(x, y, c ='b')


plt.title("Plot of household cars with distance to a " + sys.argv[1] + " stop")
plt.xlabel("Average household number of cars")
plt.ylabel("Average distance to a stop (km)")

plt.savefig('./output/' + sys.argv[2], dpi=1200)