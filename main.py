'''
I'm using a standard python, 
so I'm unsure how many of these will need to be 
imported for the Anaconda Python installation, 
but I included the command to install each individual one just in case
- Derek
'''

import numpy as np              #pip install numpy
import pandas as pd             #pip install pandas
import plotly.express as px     #pip install plotly
import pycountry                #pip install pycountry
from seaborn import clustermap  #pip install seaborn

# def fuzzySearch(country):
#     return pycountry.countries.search_fuzzy(country)[0].alpha_3

def filterDataframe(df):
    '''
    Filters the dataframe to the most useful data, as well as a country code conversion
    to be able to properly plot it on a geographical scatterplot
    '''
    #get specific columns
    df = df.loc[:, df.columns.isin(["location", "num_sequences", "variant", "date", "perc_sequences"])].reset_index()
    
    #remove negative percents
    condition  = (df['perc_sequences'] < 0 )
    df.loc[condition, 'perc_sequences'] = 0
    
    df = df.dropna() #removes any rows with NaNs in them since they give errors

    df = df.sort_values(by='date')

    #data is from various different dates, so merge all the sequence counts together to get cumulative counts
    #df = df.groupby(["location","variant"], as_index=False).agg({"num_sequences":"sum"})

    #get a dictionary of the countries in the dataset that will need to get converted, and then do the conversion
    #isoMapping = {country: fuzzySearch(country) for country in df["location"].unique()} 
    #df["location"] = df["location"].map(isoMapping)

    return df

def filterOutVariant(df, variantName):
    '''
    Although you can select individual variants on the visual geographical scatterplot,
    this is another way to filter out specific variants
    '''
    filt = df["variant"].isin([variantName])
    return df[filt]

def getTotalsForEachVariant(df):
    '''
    Returns a dictionary of {variant: totalCount}
    Might be useful if we ever need these totals
    '''
    return {variant: filterOutVariant(df, variant)["num_sequences"].sum() for variant in df["variant"].unique()}


if __name__ == "__main__":
    df = pd.read_csv("covid-variants.csv")
    df = filterDataframe(df)

    df["raised_count"] = df["num_sequences"]**0.65 #enhance differences if going by count
    
    sizeData = "num_sequences"
    graphByPercent = True
    if graphByPercent:
        sizeData = "perc_sequences"
    mapPlot = px.scatter_geo(df, locations='location', locationmode="country names", animation_frame="date", animation_group="location",
                                size=sizeData, projection="natural earth", color="variant", 
                                hover_data=["num_sequences", "location", "variant", "perc_sequences"])
    mapPlot.show()