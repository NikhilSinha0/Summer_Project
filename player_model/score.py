import sys
import time
from datetime import timedelta
from sklearn.preprocessing import minmax_scale
import hashlib
import numpy as np
sys.path.append('..') #unfortunately I can't find a better way to get stuff from sibling folders

from data_loader.loader import get_player_on_date, get_players_collection, get_partial_batch, get_distinct_test_names, get_partial_test, get_distinct_train_names

def get_score_from_json(player_json):
    return player_json["PTS"] + 0.4 * player_json["FG"] - 0.7 * player_json["FGA"] - 0.4*(player_json["FTA"] - player_json["FT"]) + 0.7 * player_json["ORB"] + 0.3 * player_json["DRB"] + player_json["STL"] + 0.7 * player_json["AST"] + 0.7 * player_json["BLK"] - 0.4 * player_json["PF"] - player_json["TOV"]

def get_score_from_date(collection, player_name, date):
    in_json = list(get_player_on_date(collection, player_name, date))
    return get_score_from_json(in_json[0])

def get_game_array_from_date(collection, player_name, date):
    in_json = list(get_player_on_date(collection, player_name, date))
    return list(in_json[0].values())

def get_batch(collection, pnames):
    indices = []
    data = []
    labels = []
    pad_arr = [0]*get_data_size(collection)
    for name in pnames:
        phash = int(hashlib.md5(name.encode('utf-8')).hexdigest()[:8], 16)%10000
        player = get_partial_batch(collection, name)
        if(len(player)==0):
            continue
        truncated_data = [[x if x!=None else 0 for x in list(p.values())[3:]] for p in player]
        #truncated_data = minmax_scale(truncated_data)
        indices.extend([phash]*len(player))
        player_data = []
        for k in range(len(truncated_data)):
            if k < 5:
                arr = [np.array(pad_arr)]*(5-k)
                arr.extend(truncated_data[0:k])
            else:
                arr = truncated_data[k-5:k]
            player_data.append(arr)
        data.extend(player_data)
        labels.extend([[get_score_from_json(game)] for game in player])
    return indices, data, labels

def get_test(collection):
    indices = []
    data = []
    labels = []
    pad_arr = [0]*get_data_size(collection)
    pnames = get_distinct_test_names(collection)
    for name in pnames:
        phash = int(hashlib.md5(name.encode('utf-8')).hexdigest()[:8], 16)%10000
        player = get_partial_test(collection, name)
        if(len(player)==0):
            continue
        truncated_data = [[x if x!=None else 0 for x in list(p.values())[3:]] for p in player]
        #truncated_data = minmax_scale(truncated_data)
        indices.extend([phash]*len(player))
        player_data = []
        for k in range(len(truncated_data)):
            if k < 5:
                arr = [np.array(pad_arr)]*(5-k)
                arr.extend(truncated_data[0:k])
            else:
                arr = truncated_data[k-5:k]
            player_data.append(arr)
        data.extend(player_data)
        labels.extend([[get_score_from_json(game)] for game in player])
    return indices, data, labels

def get_data_size(collection):
    recs = collection.find().limit(1)
    record = list(recs)[0]
    return len(record.keys())-3

def main():
    players = get_players_collection()
    score = get_score_from_date(players, "LeBron James", "2017/10/17")
    print(score)
    names = get_distinct_train_names(players)
    k = 32
    print(names[10*k:10*(k+1)])
    start = time.time()
    i, d, l = get_batch(players, names[10*k:10*(k+1)])
    end = time.time()
    print(len(i), len(d), len(l))
    print(i[1])
    print(d[1])
    print(l[1])
    print("Done. Time elapsed: " + str(timedelta(seconds = int(end - start))))

if __name__ == '__main__':
    main()