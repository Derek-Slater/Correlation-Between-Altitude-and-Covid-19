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
from seaborn import clustermap  #pip install seaborn

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

    return df

def filterOutVariant(df, variantName):
    '''
    Filters out specific variants from the dataframe passed into it
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

    sizeData = "num_sequences"
    graphByPercent = True
    if graphByPercent:
        sizeData = "perc_sequences"
    else :
        df["raised_count"] = df["num_sequences"]**0.65 #enhance differences if going by count

    mapPlot = px.scatter_geo(df, locations='location', locationmode="country names", animation_frame="date", animation_group="location",
                                size=sizeData, projection="natural earth", color="variant", 
                                hover_data=["num_sequences", "location", "variant", "perc_sequences"])
    mapPlot.show()