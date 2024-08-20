import spotipy
from pprint import pprint
import numpy as np
import json
import matplotlib.pyplot as plt
from spotipy.oauth2 import SpotifyOAuth

def main():

    # with open('victorTop50.json') as f:
    #     data = json.load(f)

    with open('evaTop10_features.json') as f:
        data = json.load(f)

    all_features = ["acousticness", "danceability","duration_ms","energy","id","instrumentalness","liveness","loudness",
                    "speechiness", "tempo", "valence"]

    # Delete features we are not interested in 
    for i, j in enumerate(data):
        for k in j.copy():
            if k not in all_features:
                del data[i][k]

    # song ID of songs I don't like but spotify thinks are in my top tracks
    bad_songs = ['03eJ2DclFWXYU8GWgANdmZ', '1Gp3vNi64EY7sEStAZ51en'] 
    
    attribute_name = ["danceability","energy","speechiness","acousticness","instrumentalness","liveness","valence"]

    # Generate list of top 10 songs
    top10 = []
    count = 0

    while len(top10)<10: 
        if data[count]['id'] in bad_songs:
            count+=1
        else: 
            top10.append(data[count])
            count+=1

    top10_song_id = []

    for i in top10: 
        top10_song_id.append(i['id'])

    avg_attributes = avg_attributes_top50(data, attribute_name)

    # This generates data to be fed into R
    heatmap()
    genre_frequency()

    kwargs_list = generate_features(attribute_name, top10)

    #recommendations = find_recommendations(kwargs_list, attribute_name, top10_song_id)

    return avg_attributes


def generate_features(attribute_name, top10):

    # Generate keyword arguments that will be used to generate song recommendations
    kwargs = {}
    kwargs_list = []
    interval = 0.2

    for i in attribute_name:
        max_feature = "max_" + i
        min_feature = "min_" + i
        kwargs[max_feature] = None
        kwargs[min_feature] = None

    for i, top10track in enumerate(top10):
        kwargs_list.append(kwargs.copy())
        for key, val in top10track.items(): 
            if key in attribute_name:

                min_attr_name = 'min_' + key
                max_attr_name = 'max_' + key

                if val < interval:
                    kwargs_list[i][min_attr_name] = 0
                    kwargs_list[i][max_attr_name] = 2 * interval

                elif val > 1 - interval:
                    kwargs_list[i][min_attr_name] = 1 - 2 * interval
                    kwargs_list[i][max_attr_name] = 1

                else: 
                    kwargs_list[i][min_attr_name] = val - interval
                    kwargs_list[i][max_attr_name] = val + interval

    return kwargs_list

def avg_attributes_top50(data, attribute_name):

    avg_attributes = [0] * len(attribute_name)

    allFeatures = []
    variance_arr  = []

    for track in data:

        # Some tracks, such as podcasts, do not have audio features, so we skip
        if len(track)==0: 
            continue

        trackValues = list(track.values())
        attribute_val = [0]*len(track)

        for i in range(len(track)):
            
            j = trackValues[i]

            if ((isinstance(j, float)) or (isinstance(j, int))) and ((j>=0) & (j<=1)):
                attribute_val[i]+=j

            else: 
                attribute_val[i]=None

        attribute_val = [k for k in attribute_val if k is not None] # lambda function

        for l,m in enumerate(attribute_val):
            avg_attributes[l] += m
        allFeatures.append(attribute_val)

    avg_attributes = np.asarray(avg_attributes)/len(data)

    allFeaturesCol = len(attribute_name)
    allFeaturesRow = len(allFeatures)

    allFeatures = np.asmatrix(allFeatures).reshape(allFeaturesRow,allFeaturesCol)

    # variance calculation
    for i in range(allFeaturesCol):
        variance_arr.append(np.var(allFeatures[:, i]))

    spotify_green = "#1DB954" # Test color "#9030FF"

    plt.bar(range(len(attribute_val)), avg_attributes, tick_label=attribute_name, color=spotify_green)
    plt.errorbar(range(len(attribute_val)), avg_attributes, yerr=variance_arr,capsize=5,capthick=1.5, fmt = "none", ecolor ="black")
    plt.gcf().set_size_inches(11.5, 7)
    plt.title('Audio Features of Victor\'s Top 50 Tracks on Spotify')
    #plt.ion()
    plt.show()

    return avg_attributes

def find_recommendations(kwargs_list, attribute_name, top10_song_id):

    # Victor's cid and secret
    cid = 'b35b560eb62a4c92ae570e8077a6e649'
    secret = 'e4f24ed5a8414af1b0c603ed34154a1c'

    # # Eva's cid and secret
    # cid = '06d3531cbf704d1088e213d542f81c3c'
    # secret = 'a7c95cc4963f427ab9ee9845db6d0fbc'

    scope = "user-top-read" # read user's to items

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri="https://open.spotify.com/" ,scope=scope))

    full_attr_list = kwargs_list.copy()[1].keys()
    revised_kwargs_list = [[] for _ in range(len(kwargs_list))]
    rec_list = [[] for _ in range(len(kwargs_list))]

    for attr in attribute_name:
        for song_index in range(len(kwargs_list)): 
            kwargs_copy = kwargs_list[song_index].copy()
            for j in full_attr_list:
                if attr in j:
                    pop_val = kwargs_copy.pop(j)
            revised_kwargs_list[song_index].append(kwargs_copy)

    top10_genres = find_genres(top10_song_id)
    #pprint(top10_genres)

    for i, track_features in enumerate(revised_kwargs_list):

        for kwargs in track_features: 

            genres = top10_genres[i]
            song_id = top10_song_id[i]

            print('a')
            print(song_id)
            #recommendation = sp.recommendations(seed_genres=genres,limit = 1, **kwargs)
            recommendation = sp.recommendations(seed_tracks=[song_id],limit = 1, **kwargs)
            print('b')
            #pprint(recommendation)
            if len(recommendation['tracks'])>0:
                print('c')
                #processed_rec = [recommendation['tracks'][0]]
                #pprint(processed_rec)
                rec_song_name = str(recommendation['tracks'][0]['name'])
                rec_artist_name = str(recommendation['tracks'][0]['artists'][0]['name'])
                processed_rec = rec_song_name + '-' + rec_artist_name
                print(processed_rec)
                rec_list[i].append(processed_rec)
            else: 
                print('not c')
                rec_list[i].append('NULL RECOMMENDATION')

    pprint(rec_list)

    return rec_list

def find_genres(top10_song_id):
    # Mine
    cid = 'b35b560eb62a4c92ae570e8077a6e649'
    secret = 'e4f24ed5a8414af1b0c603ed34154a1c'

    # Eva
    # cid = '06d3531cbf704d1088e213d542f81c3c'
    # secret = 'a7c95cc4963f427ab9ee9845db6d0fbc'

    scope = "user-top-read" # read top artists

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri="https://open.spotify.com/" ,scope=scope))

    tracks = sp.tracks(top10_song_id)

    artist_id_list = []

    for i, track in enumerate(tracks['tracks']): 
        artist_id = tracks['tracks'][i]['artists'][0]['id']
        print(tracks['tracks'][i]['artists'][0]['name'])
        artist_id_list.append(artist_id)

    artists_info = sp.artists(artist_id_list)

    top_genre_list = []
    
    for artist in artists_info['artists']:

        # The genres extracted from top artists doesn't match one-to-one with the genres we're allowed to call
        # recommendations for. These are hard-coded

        if artist['id'] == '4vGrte8FDu062Ntj0RsPiZ': # Polyphia
            artist['genres'] = ['jazz', 'guitar', 'hip-hop', 'metal', 'rock']
        elif artist['id'] == '7voEy17zvlQojgmQYUlKDK': # Arekun
            artist['genres'] = ['j-pop']
        elif artist['id'] == '70NcAr4ZtA3FAqU16iQZSb': # Dhruv
            artist['genres'] = ['romance', 'indie pop', 'british', 'indian', 'singer-songwriter']
        elif artist['id'] == '5069JTmv5ZDyPeZaCCXiCg': # wave to earth
            artist['genres'] = ['chill', 'k-pop', 'indie pop'] 
        elif artist['id'] == '6fHEaFnFgMxMAtDt7mFoQ3': # tsubi club
            artist['genres'] = ['alternative', 'emo', 'pop', 'punk']

        # In addition, some artists don't have associated genres. 
        # We will hard-code these values.
        if len(artist['genres']) == 0:

            if artist['id'] == '7EJYadnOoXsnXbvULN7YCR': # Tom Frane
                artist['genres'] = ['indie pop', 'pop', 'chill r&b']

            elif artist['id'] == '52N3KGrTWDRhdQJrgBTofE': # Good Neighbours
                artist['genres'] = ['indie pop', 'pop', 'alternative pop rock']

            else: 
                artist['genres'] = ['pop']

        top_genre_list.append(artist['genres'])

    return top_genre_list

def heatmap():
    top50_genres = [['candy pop', 'modern rock', 'pixie', 'pop', 'pop emo', 'pop punk', 'rock'],['complextro', 'edm', 'electro house', 'pop dance', 'progressive electro house'],['alternative pop rock', 'pov: indie'],['chicago rap', 'hip hop', 'rap'],['instrumental rock'],['pop'],['japanese teen pop']
    ,['chill r&b'],['classic oklahoma country'],['conscious hip hop', 'hip hop', 'rap', 'west coast rap'],['singer-songwriter pop'],['escape room', 'hyper-rock', 'japanese electropop'],['modern rock', 'pop', 'pov: indie', 'rock'],['pop'],['bedroom pop', 'oakland indie', 'pov: indie'],['pop']
    ,['k-pop'],['bedroom pop', 'bubblegrunge', 'indie pop', 'pov: indie'],['anime', 'j-pop'],['bitpop', 'chiptune', 'indie game soundtrack', 'nintendocore'],['uk alternative pop'],['japanese teen pop'],['art pop', 'pop'],['hyperpop'],['pov: indie'],['j-pop', 'japanese teen pop'],['pop', 'viral pop']
    ,['australian pop', 'pop', 'viral pop'],['alternative hip hop', 'experimental hip hop', 'industrial hip hop', 'underground hip hop'],['k-pop', 'k-pop boy group', 'pop'],['complextro', 'edm', 'electro house', 'electropop', 'filter house', 'nantes indie', 'pop dance']
    ,['modern alternative rock', 'modern rock', 'pop', 'pov: indie', 'rock'],['electro', 'filter house', 'rock'],['australian indie rock'],['emo rap', 'miami hip hop', 'rap'],['j-rock', 'japanese indie pop'],['hyper-rock'],['indie pop rap'],['hip hop', 'rap'],['j-pop'],['indie game soundtrack', 'otacore', 'pixel']
    ,['art pop', 'electropop', 'escape room', 'indie pop'],['alt z', 'electropop', 'pop'],['nyc pop'],['pop', 'r&b', 'rap'],['motown', 'soul'],['east coast hip hop', 'gangster rap', 'hip hop', 'pop rap', 'rap'],['rap', 'slap house'],['pop']
    ,['dark trap', 'drill', 'hip hop', 'miami hip hop', 'pop rap', 'rap', 'trap', 'underground hip hop']]

    genres_buckets = ['pop', 'hip hop','rap','trap', 'house', 'r&b', 'rock', 'indie', 'game', 'anime']
    genres_buckets.sort()

    g2 = {}

    for bucket3 in genres_buckets:
        g2[bucket3] = 0

    g3 = g2.copy()

    for bucket4, bucket5 in g2.items():
        g2[bucket4] = g3.copy()
        
    for bucket1 in genres_buckets:
        for bucket2 in genres_buckets:

            if bucket1==bucket2: 
                continue

            for genre_list in top50_genres:
                for genre in genre_list:
                    if bucket1 in genre:
                        for genre2 in genre_list:
                            if bucket2 in genre2:
                                g2[bucket1][bucket2]+=1
                                break
                        # Multiple pop types in one genre_list so shouldn't count, so we break after the first instance
                        break

    x = []
    y = []
    z = []
    for i, j in g2.items():
        for k,val in j.items():
            x.append(i)
            y.append(k)
            z.append(val)


def genre_frequency():

    top50_genres = [['candy pop', 'modern rock', 'pixie', 'pop', 'pop emo', 'pop punk', 'rock'],['complextro', 'edm', 'electro house', 'pop dance', 'progressive electro house'],['alternative pop rock', 'pov: indie'],['chicago rap', 'hip hop', 'rap'],['instrumental rock'],['pop'],['japanese teen pop']
    ,['chill r&b'],['classic oklahoma country'],['conscious hip hop', 'hip hop', 'rap', 'west coast rap'],['singer-songwriter pop'],['escape room', 'hyper-rock', 'japanese electropop'],['modern rock', 'pop', 'pov: indie', 'rock'],['pop'],['bedroom pop', 'oakland indie', 'pov: indie'],['pop']
    ,['k-pop'],['bedroom pop', 'bubblegrunge', 'indie pop', 'pov: indie'],['anime', 'j-pop'],['bitpop', 'chiptune', 'indie game soundtrack', 'nintendocore'],['uk alternative pop'],['japanese teen pop'],['art pop', 'pop'],['hyperpop'],['pov: indie'],['j-pop', 'japanese teen pop'],['pop', 'viral pop']
    ,['australian pop', 'pop', 'viral pop'],['alternative hip hop', 'experimental hip hop', 'industrial hip hop', 'underground hip hop'],['k-pop', 'k-pop boy group', 'pop'],['complextro', 'edm', 'electro house', 'electropop', 'filter house', 'nantes indie', 'pop dance']
    ,['modern alternative rock', 'modern rock', 'pop', 'pov: indie', 'rock'],['electro', 'filter house', 'rock'],['australian indie rock'],['emo rap', 'miami hip hop', 'rap'],['j-rock', 'japanese indie pop'],['hyper-rock'],['indie pop rap'],['hip hop', 'rap'],['j-pop'],['indie game soundtrack', 'otacore', 'pixel']
    ,['art pop', 'electropop', 'escape room', 'indie pop'],['alt z', 'electropop', 'pop'],['nyc pop'],['pop', 'r&b', 'rap'],['motown', 'soul'],['east coast hip hop', 'gangster rap', 'hip hop', 'pop rap', 'rap'],['rap', 'slap house'],['pop']
    ,['dark trap', 'drill', 'hip hop', 'miami hip hop', 'pop rap', 'rap', 'trap', 'underground hip hop']]

    genres_buckets = ['pop', 'hip hop','rap','trap', 'electronic', 'r&b', 'rock', 'indie', 'game', 'anime', 'soul', 'country']
    genres_dict = {}

    genres_buckets.sort()

    for i in genres_buckets:
        genres_dict[i] = 0

    for bucket in genres_buckets:
        for genres_list in top50_genres:
            for genre in genres_list:
                if bucket in genre:
                    genres_dict[bucket]+=1

                    break
                elif bucket == 'electronic':
                    if 'house' in genre or 'edm' in genre or 'electro' in genre:
                        genres_dict[bucket]+=1

                        break

    spotify_green = '#1DB954'

    pprint(list(genres_dict.values()))
    plt.bar(range(len(genres_buckets)), list(genres_dict.values()), tick_label=genres_buckets, color=spotify_green)
    
    plt.gcf().set_size_inches(11.5, 7)
    plt.title('Victor\'s Genre Count of Top 50 Artists')
    plt.show()

# def generate_top10(possum):

#     # Victor
#     cid = 'b35b560eb62a4c92ae570e8077a6e649'
#     secret = 'e4f24ed5a8414af1b0c603ed34154a1c'

#     # Eva's cid
#     # cid = '06d3531cbf704d1088e213d542f81c3c'
#     # secret = 'a7c95cc4963f427ab9ee9845db6d0fbc'

#     scope = "user-top-read" # read top artists

#     sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri="https://open.spotify.com/" ,scope=scope))

#     #tracks = sp.tracks(top10_song_id)

#     # top10 = sp.current_user_top_tracks(limit=10, offset=0, time_range='medium_term')
#     # print(top10)
#     current = sp.audio_features(possum)
#     #print(current)
#     return current

#generate_top10()

#heatmap()
# def goofy():

#     with open('evaTop10.json') as f:
#         data2 = json.load(f)
#     #pprint(data2["items"][0])
#     pprint(data2["items"][0]['id'])

#     top10_song_id = []

#     for i in range(len(data2["items"])):
#         print(data2["items"][i]["name"])
#         print(data2["items"][i]["id"])

#         song_id = data2["items"][i]["id"]
#         top10_song_id.append(song_id)

#     return top10_song_id

# possum = goofy()

# gray = generate_top10(possum)
# pprint(gray)

#avg_attributes = main(possum)
avg_attributes = main()

#genre_frequency()