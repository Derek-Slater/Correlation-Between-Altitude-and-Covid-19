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
    df = df.loc[:, df.columns.isin(["location", "num_sequences", "variant"])].reset_index()
    df = df.dropna() #removes any rows with NaNs in them since they give errors

    #data is from various different dates, so merge all the sequence counts together to get cumulative counts
    df = df.groupby(["location","variant"], as_index=False).agg({"num_sequences":"sum"})

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
    #df = filterOutVariant(df, "Beta")

    mapPlot = px.scatter_geo(df, locations='location', locationmode="country names", size="num_sequences", projection="natural earth", color="variant", opacity=0.8)
    mapPlot.show()