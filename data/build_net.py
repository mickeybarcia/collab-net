import pandas as pd 
import ast
import pprint
import json

## build artist net
'''
artist net structure:
{
    cardi: {
        collabs: {
            megan: 1,
            nicki: 2
        },
        features: {
            doja: 1
        }
    }
}
'''
artist_net = {}
charts_df = pd.read_csv("charts.csv", converters={2:ast.literal_eval}, delimiter='\t')
for index, row in charts_df.iterrows():
    artists = row["artists"]["artists"]
    has_features = "featuring" in row["artists"]
    should_add_song_name = len(artists) != 1 or has_features
    for artist in artists:
        if artist not in artist_net:
            artist_net[artist] = {}
            artist_net[artist]["collabs"] = {}
            artist_net[artist]["songs"] = []
        if should_add_song_name:
            artist_net[artist]["songs"].append(row["title_full"])
        for collab_artist in artists:
            if collab_artist != artist and collab_artist not in artist_net[artist]["collabs"]:
                artist_net[artist]["collabs"][collab_artist] = 1
            elif collab_artist != artist:
                artist_net[artist]["collabs"][collab_artist] += 1
    if has_features:
        if "features" not in artist_net[artist]:
            artist_net[artist]["features"] = {}
        features = row["artists"]["featuring"]
        for feature in features:
            if feature not in artist_net[artist]["features"]:
                artist_net[artist]["features"][feature] = 1
            else:
                artist_net[artist]["features"][feature] += 1
            if feature not in artist_net:
                artist_net[feature] = {}
                artist_net[feature]["collabs"] = {}
                artist_net[feature]["songs"] = []
            artist_net[feature]["songs"].append(row["title_full"])

## include collaborating artist
final_net = {}
for artist in artist_net.keys():
    if len(artist_net[artist]["collabs"].keys()) > 0:
        final_net[artist] = artist_net[artist]

## make chart format data
data = []
for artist in final_net.keys():
    data_row = { 
        "name": artist, 
        "linkWith": list(artist_net[artist]["collabs"].keys()), 
        "value": sum(artist_net[artist]["collabs"].values()) * 3,
        "songs": artist_net[artist]["songs"]
    }
    if "features" in artist_net[artist]:
        features = []
        for feature in artist_net[artist]["features"].keys():
            if feature not in final_net:
                features.append({ 
                    "name": feature, 
                    "value": artist_net[artist]["features"][feature]
                })
        data_row["children"] = features
        data_row["value"] += sum(artist_net[artist]["features"].values())
    data.append(data_row)

## save data
with open('./public/net.json', 'w') as f:
    json.dump(data, f)     