from UsefulMethods import distance, random_points_within
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import sys
from scipy import optimize

import warnings
warnings.filterwarnings("ignore")

LONGLATTOM = 111000

# read the shape file of Victoria suburb
plt.rcdefaults() 
victoria_map = gpd.read_file('./ll_gda94/sde_shape/whole/VIC/VMLITE/layer/vmlite_postcode_polygon.shp')
victoria_map = victoria_map.to_crs({'init': 'epsg:4326'})

# read the car number dataset
population_dict = pd.read_csv("populationPerPostcode.csv").set_index('Postcode').to_dict()
# function to get car for a postcode
def getPopulation(postcode):
    try:
        temp = population_dict['Population'][int(postcode)]
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


# calculate log average distance to a stop
def avgDistanceLogToStopAnySurb(polygon):
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
        return np.log(totalDistance * LONGLATTOM/len(samplesPoint))
    else:
        point = polygon.centroid
        tempDistance = distance(allpoint[0].x, allpoint[0].y, point.x, point.y)
        for stop in allpoint:
            temp = distance(stop.x, stop.y, point.x, point.y)
            if temp < tempDistance:
                tempDistance = temp
        return np.log(tempDistance * LONGLATTOM)

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
victoria_map['avgDis'] = victoria_map['geometry'].apply(avgDistanceLogToStopAnySurb)
victoria_map['population'] = victoria_map['POSTCODE'].apply(getPopulation)
victoria_map["area"] = victoria_map['geometry'].area*110*110
victoria_map["populationDensity"] = victoria_map["population"]/victoria_map["area"]
# Plot the data and save figure
listCluster = []
xlist = []
ylist = []
for index, row in victoria_map.iterrows():
    if (not np.isnan(row["populationDensity"])) and (not np.isnan(row["avgDis"])):
        listCluster.append([row["populationDensity"], row["avgDis"]])
        xlist.append(row["populationDensity"])
        ylist.append(row["avgDis"])

for x,y in listCluster:
    plt.scatter(x, y, c ='b')

plotting = optimize.curve_fit(lambda t,a,b,c: c + a/(t+b),  xlist,  ylist)
x1 = np.linspace(victoria_map["populationDensity"].min(),victoria_map["populationDensity"].max(),100)
y1 =plotting[0][2] + plotting[0][0]/(plotting[0][1]+x1)

plt.plot(x1,y1)
plt.title("Plot of population density with distance to a " + sys.argv[1] + " stop (in log scale)")
plt.xlabel("Density of population (people/km2)")
plt.ylabel("Average distance to a stop (log scale of m)")

plt.savefig('./output/' + sys.argv[2], dpi=1200)
print("Fit line: log(avg distance to " + sys.argv[1] + " stops) = "+ str(plotting[0][2]) + " + " + str(plotting[0][0]) + "/(population density + " + str(plotting[0][1]) + ")")