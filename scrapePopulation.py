from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import geopandas as gpd
import requests

data = gpd.read_file('./ll_gda94/sde_shape/whole/VIC/VMLITE/layer/vmlite_postcode_polygon.shp')
postcode = {}

for i in list(data["POSTCODE"]):
    u = 'https://quickstats.censusdata.abs.gov.au/census_services/getproduct/census/2016/quickstat/POA' + \
        str(i) + '?opendocument'
    page = requests.get(u)
    soup = BeautifulSoup(page.text, 'html.parser')
    section = soup.find(id="summaryTableAP")
    if section and len(section.find_all('table')) >= 3:
        results = section.findNext('table')
        final = results.findNext("tr")
        stats = final.find_all("td")
        population = unicodedata.normalize("NFKD", stats[0].text.strip())
        population = ''.join(e for e in population if e.isalnum())
        postcode[i] = int(population)
        print("Population", population, "in suburb postcode", i)


result = pd.DataFrame(postcode.items(), columns=["Postcode", "Population"])
result.to_csv("populationPerPostcode.csv", index="Postcode")
