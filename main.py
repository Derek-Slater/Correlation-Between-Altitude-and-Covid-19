import numpy as np              #pip install numpy
import pandas as pd             #pip install pandas
import plotly.express as px     #pip install plotly, pip intsall statsmodels
import os
import sys

def filterDataframe(df):
    '''
    Filters the dataframe to the most useful data, 
    including getting rid of any negative/NaN values and sorting by time.
    Returns the new dataframe.
    '''
    #get specific columns
    df = df.loc[:, df.columns.isin(["location", "num_sequences", "variant", "date", "perc_sequences", "altitude", "population"])]
    
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
    altitudeMapping = pd.read_csv(os.path.join("input", "countryAltitudes.csv"))
    for i in range(len(altitudeMapping)): #parse out first number of each elevation value
        altitudeMapping.iloc[i].Elevation = altitudeMapping.iloc[i].Elevation[:altitudeMapping.iloc[i].Elevation.find(" ") - 2]
        altitudeMapping.iloc[i].Elevation = altitudeMapping.iloc[i].Elevation.replace(",", "")
    altitudeMapping = altitudeMapping.set_index('Country').to_dict()['Elevation'] #create dictionary/map
    
    #do the mapping
    df["altitude"] = pd.to_numeric(df["location"].map(altitudeMapping))
    return df["altitude"]

def mapCountriesToPopulations(df):
    ''' 
    First creates a mapping of {countries: 2021 population counts} from a csv file,
    then uses that to map countries from "df" to their associated populations,
    after which, a column of populations is returned.
    '''
    populationMapping = pd.read_csv(os.path.join("input", "2021_population.csv"))
    populationMapping['2021_last_updated'] = populationMapping['2021_last_updated'].replace(to_replace = ',', value = '', regex = True)
    populationMapping = populationMapping.set_index('country').to_dict()['2021_last_updated'] #create dictionary/map
    
    #do the mapping
    df["population"] = pd.to_numeric(df["location"].map(populationMapping))
    return df["population"]

def createScatterplot(df, graphVariantsSeparately=True):
    '''
    Creates and returns a 2D scatterplot, 
    with the x-axis as altitude and y-axis as number of cases.
    graphVariantsSeparately, when true, graphs variants without merging them all together (separately)
    '''
    df = df.drop('date', axis=1)

    #create a dataframe containing aggregated (all) variant counts
    if not graphVariantsSeparately:
        df["variant"] = "All Variants"

    df = df.groupby(["variant", "location", "altitude", "population"], as_index=False).agg({"num_sequences":"sum"})
    df["casesPer100000"] = df["num_sequences"] / df["population"] * 100000
    scatterPlot = px.scatter(df, x="altitude", y="casesPer100000", color="variant", hover_data=["location"], trendline="ols")
    scatterPlot.update_yaxes(categoryorder="total descending")
    return scatterPlot

def createGeoScatterplot(df, graphByPercent=False):
    '''
    Creates and returns a geographic scatterplot, 
    with points placed according to location, point size from num_sequences, and color from the variant.
    If graphByPercent is "True", it graphs by perc_sequences instead.
    '''
    sizeData = "casesPer100000"
    if graphByPercent:
        sizeData = "perc_sequences"
    else :
        df["casesPer100000"] = df["num_sequences"] / df["population"] * 100000

    mapPlot = px.scatter_geo(df, locations='location', locationmode="country names",
                                animation_frame="date", animation_group="location",
                                size=sizeData, projection="natural earth", color="variant", 
                                hover_data=["num_sequences", "location", "variant", "perc_sequences", "altitude"])
    return mapPlot

def writeResultsToFile(scatterPlot, filename):
    '''
    Takes in a created scatterplot and writes summaries of each set of results to output/results.txt
    '''
    sys.stdout = open(os.path.join("output", filename), "w")
    for i, item in enumerate(px.get_trendline_results(scatterPlot).px_fit_results):
        print("Variant: ", px.get_trendline_results(scatterPlot)["variant"][i])
        print(item.summary(), "\n")
    sys.stdout.close()

if __name__ == "__main__":
    df = pd.read_csv(os.path.join("input", "covid-variants.csv"))
    df["altitude"] = mapCountriesToAltitudes(df)
    df["population"] = mapCountriesToPopulations(df)
    df = filterDataframe(df)

    mapPlot = createGeoScatterplot(df)
    scatterPlotIndividualVariants = createScatterplot(df)
    scatterPlotAggregatedVariants = createScatterplot(df, False)

    writeResultsToFile(scatterPlotIndividualVariants, "results_individualVariants.txt")
    writeResultsToFile(scatterPlotAggregatedVariants, "results_aggregatedVariants.txt")
    
    scatterPlotIndividualVariants.show()
    scatterPlotAggregatedVariants.show()
    mapPlot.show()
