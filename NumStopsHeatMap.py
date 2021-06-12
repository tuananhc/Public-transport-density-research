from UsefulMethods import distance
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import sys

import warnings
warnings.filterwarnings("ignore")

LONGLATTOKM = 111

# read the shape file of Victoria suburb
victoria_map = gpd.read_file('./ll_gda94/sde_shape/whole/VIC/VMLITE/layer/vmlite_postcode_polygon.shp')
victoria_map = victoria_map.to_crs(epsg=4326)

# take the position of stops since we limited our region
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

# Plot the data and save figure
fig, ax = plt.subplots(1)
color = 'Blues'
vmin, vmax = victoria_map['counter'].min(), victoria_map['counter'].max()
sm = plt.cm.ScalarMappable(cmap=color, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbar = fig.colorbar(sm,fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=8)
victoria_map.plot('counter', cmap=color, ax=ax, edgecolor='0.8')
for index, row in transport_pd.iterrows():
    ax.scatter(row[" LONGITUDE"], row[" LATITUDE"], s=int(sys.argv[3]), lw = 0, color="red", alpha=0.3)

plt.title("Number of " + sys.argv[1] + " stops for each suburb")
ax.axis('off')
plt.savefig('./output/' + sys.argv[2], dpi=1200)