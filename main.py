import numpy
import pandas as pd
import plotly.express as px
import country_converter as coco
from seaborn import clustermap

def filterDataframe(df):
    df = df.loc[:, df.columns.isin(["location", "num_sequences", "variant"])]
    df = df.replace(0, numpy.nan)
    df = df.dropna()
    df["num_sequences"] = df["num_sequences"].astype(int)
    df = df.reset_index()
    df = df.groupby(["location","variant"], as_index=False).agg({"num_sequences":"sum"})
    df['location'] = df['location'].apply(lambda x: coco.convert(names=x, to='ISO3', not_found=None))
    return df

def filterOutVariant(df, variantName):
    filt = df["variant"].isin([variantName])
    return df[filt]

if __name__ == "__main__":
    df = pd.read_csv("covid-variants.csv")
    df = filterDataframe(df)
    df = filterOutVariant(df, "Beta")

    mapPlot = px.scatter_geo(df, locations='location', size="num_sequences", color="variant", projection='orthographic', opacity=0.8)
    mapPlot.show()