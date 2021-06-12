from UsefulMethods import distance, random_points_within
import numpy as np
import pandas as pd
import numpy as np
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

# read the income number dataset
income_dict = pd.read_csv("weeklyIncome.csv").set_index('Postcode').to_dict()
# read the income number dataset
def getIncome(postcode):
    try:
        temp = income_dict['Weekly Income'][int(postcode)]
    except:
        temp = np.NaN
    return temp

# take the position of bus stops since we limited our region
transport_pd = pd.read_csv('material/metro_bus.csv', encoding = 'ISO-8859-1')
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


# calculate the average distance to a stop in a suburb
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
victoria_map['income'] = victoria_map['POSTCODE'].apply(getIncome)

# Plot the data and save figure
fig, ax = plt.subplots(1)
color = 'Blues'
vmin, vmax = victoria_map["income"].min(), victoria_map["income"].max()
sm = plt.cm.ScalarMappable(cmap=color, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbar = fig.colorbar(sm,fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=8)
victoria_map.plot('income', cmap=color, ax=ax, edgecolor='0.8')


plt.title("Average weekly income")
ax.axis('off')
plt.savefig('./output/' + sys.argv[1], dpi=1200)