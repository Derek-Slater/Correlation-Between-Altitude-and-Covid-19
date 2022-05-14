import numpy as np              #pip install numpy
import pandas as pd             #pip install pandas
import plotly.express as px     #pip install plotly
from seaborn import clustermap  #pip install seaborn

def filterDataframe(df):
    '''
    Filters the dataframe to the most useful data, 
    including getting rid of any negative/NaN values and sorting by time.
    Returns the new dataframe.
    '''
    #get specific columns
    df = df.loc[:, df.columns.isin(["location", "num_sequences", "variant", "date", "perc_sequences", "altitude"])]
    
    #remove negative percents
    condition  = (df['perc_sequences'] < 0 )
    df.loc[condition, 'perc_sequences'] = 0
    
    df = df.dropna() #removes any rows with NaNs in them since they give errors
    df = df.sort_values(by='date') #sort by date

    return df.reset_index()

def mapCountriesToAltitudes(df):
    ''' 
    First creates a mapping of {countries: altitudes} from a csv file,
    then uses that to map countries from "df" to their associated altitudes,
    after which, a column of altitudes is returned.
    '''
    altitudeMapping = pd.read_csv("countryAltitudes.csv")
    for i in range(len(altitudeMapping)): #parse out first number of each elevation value
        altitudeMapping.iloc[i].Elevation = altitudeMapping.iloc[i].Elevation[:altitudeMapping.iloc[i].Elevation.find(" ") - 2]
        altitudeMapping.iloc[i].Elevation = altitudeMapping.iloc[i].Elevation.replace(",", "")
    altitudeMapping = altitudeMapping.set_index('Country').to_dict()['Elevation'] #create dictionary/map
    
    #do the mapping
    df["altitude"] = pd.to_numeric(df["location"].map(altitudeMapping))
    return df["altitude"]

def createScatterplot(df):
    '''
    Creates and returns a 2D scatterplot, 
    with the x-axis as altitude and y-axis as number of cases.
    '''
    df = df.drop('date', axis=1)
    df = df.groupby(["variant", "location", "altitude"], as_index=False).agg({"num_sequences":"sum"})
    scatterPlot = px.scatter(df, x="altitude", y="num_sequences", color="variant", hover_data=["location"])
    scatterPlot.update_yaxes(categoryorder="total descending")
    return scatterPlot

def createGeoScatterplot(df, graphByPercent=False):
    '''
    Creates and returns a geographic scatterplot, 
    with points placed according to location, point size from num_sequences, and color from the variant.
    If graphByPercent is "True", it graphs by perc_sequences instead.
    '''
    sizeData = "num_sequences"
    graphByPercent = False
    if graphByPercent:
        sizeData = "perc_sequences"
    else :
        df["raised_count"] = df["num_sequences"]**0.65 #makes smaller values easier to see if going by count

    mapPlot = px.scatter_geo(df, locations='location', locationmode="country names",
                                animation_frame="date", animation_group="location",
                                size=sizeData, projection="natural earth", color="variant", 
                                hover_data=["num_sequences", "location", "variant", "perc_sequences", "altitude"])
    return mapPlot

if __name__ == "__main__":
    df = pd.read_csv("covid-variants.csv")
    df["altitude"] = mapCountriesToAltitudes(df)
    df = filterDataframe(df)

    mapPlot = createGeoScatterplot(df)
    scatterPlot = createScatterplot(df)
    
    scatterPlot.show()
    mapPlot.show()