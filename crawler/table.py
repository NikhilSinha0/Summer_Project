import os
from datetime import datetime
from math import sin, cos, radians, atan2, sqrt
from stadiums import stadiums

class game_table:
    def __init__(self):
        self.home = ''
        self.away = ''

        self.home_last_game = ''
        self.home_days_rest = ''
        self.home_last_game_location = ''
        self.home_dist_travelled = ''
        self.home_last_3_rest = ''
        self.home_last_3_dist = ''
        self.home_result = ''

        self.away_last_game = ''
        self.away_days_rest = ''
        self.away_last_game_location = ''
        self.away_dist_travelled = ''
        self.away_last_3_rest = ''
        self.away_last_3_dist = ''
        self.away_result = ''

        self.date = ''

        self.home_scores = {}
        self.away_scores = {}

        self.add_to_home = False
        self.remove_MP = True

    def add_name(self, name):
        if(self.away):
            self.home = name.split('(')[0].strip()
        else:
            self.away = name.split('(')[0].strip()

    def sync_last_game_info(self, season):
        if(not(self.home_days_rest and self.home_days_rest)):
            season.remove_team(self.home)
        else:
            season.add_game(self.home, self.home_dist_travelled, self.home_days_rest)
        if(not(self.away_days_rest and self.away_days_rest)):
            season.remove_team(self.away)
        else:
            season.add_game(self.away, self.away_dist_travelled, self.away_days_rest)
        home_last_3_games = season.get_last_three(self.home)
        self.home_last_3_rest = '['+','.join([x.rest for x in home_last_3_games])+']'
        self.home_last_3_dist = str(sum([float(x.distance) for x in home_last_3_games]))
        away_last_3_games = season.get_last_three(self.away)
        self.away_last_3_rest = '['+','.join([x.rest for x in away_last_3_games])+']'
        self.away_last_3_dist = str(sum([float(x.distance) for x in away_last_3_games]))

    def set_win_loss(self):
        index = self.away_scores["Name"].index("PTS")
        away_score = int(self.away_scores["Team Totals"][index])
        home_score = int(self.home_scores["Team Totals"][index])
        self.away_result = '1' if away_score > home_score else '0'
        self.home_result = '0' if away_score > home_score else '1'

    def add_last_game_info(self, prevs):
        for prev_game in prevs:
            if(self.away==prev_game[0]):
                self.away_last_game_location = prev_game[1]
                self.away_dist_travelled = str(self.get_dist_between_stadiums(self.home, self.away_last_game_location))
                self.away_last_game = "/".join([prev_game[2][:4], prev_game[2][4:6], prev_game[2][6:]])
                away_last = datetime.strptime(self.away_last_game, "%Y/%m/%d")
                today = datetime.strptime(self.date, "%Y/%m/%d")
                self.away_days_rest = str((today - away_last).days-1)
            else:
                self.home_last_game_location = prev_game[1]
                self.home_dist_travelled = str(self.get_dist_between_stadiums(self.home, self.home_last_game_location))
                self.home_last_game = "/".join([prev_game[2][:4], prev_game[2][4:6], prev_game[2][6:]])
                home_last = datetime.strptime(self.home_last_game, "%Y/%m/%d")
                today = datetime.strptime(self.date, "%Y/%m/%d")
                self.home_days_rest = str((today - home_last).days-1) #Playing a game on next day = 0 days rest

    def add_to_home_scores(self, row):
        if(self.home_scores.get(row[0])):
            if(len(row)==2):
                return
            if(self.remove_MP):
                self.home_scores.get(row[0]).extend(row[2:])    
            else:
                self.home_scores.get(row[0]).extend(row[1:])
        else:
            self.home_scores[row[0]] = row[1:]

    def add_to_away_scores(self, row):
        if(self.away_scores.get(row[0])):
            if(len(row)==2):
                return
            if(self.remove_MP):
                self.away_scores.get(row[0]).extend(row[2:])    
            else:
                self.away_scores.get(row[0]).extend(row[1:])
        else:
            self.away_scores[row[0]] = row[1:]

    def add_data_row(self, row):
        if(self.add_to_home):
            self.add_to_home_scores(row)
        else:
            self.add_to_away_scores(row)

    def add_row(self, row):
        if(not row[0]):
            self.remove_MP = not self.remove_MP
            if(self.away_scores and 'Basic' in row[1]):
                self.add_to_home = True
        elif(row[0]=='Starters'):
            row[0]='Name'
            self.add_data_row(row)
        elif(row[0]=='Reserves'):
            pass
        else:
            self.add_data_row(row)

    def print_table(self):
        print('Away: ' + self.away)
        print(self.away_scores)
        print('Home: ' + self.home)
        print(self.home_scores)

    def table_to_csv(self):
        result = 'Date: '+self.date+'\n'
        result += 'Away: ' + self.away + '\n'
        result += 'Last Game Date: '+self.away_last_game+'\n'
        result += 'Last Game Location: '+self.away_last_game_location+'\n'
        result += 'Win: '+self.away_result+'\n'
        result += 'Days Rest: '+self.away_days_rest+'\n'
        result += 'Distance Travelled: '+self.away_dist_travelled+'\n'
        result += 'Last 3 Games Rest: ,'+self.away_last_3_rest[1:-1]+'\n'
        result += 'Last 3 Games Distance Travelled: '+self.away_last_3_dist+'\n'
        for name, stats in self.away_scores.items():
            result += name + ',' + ','.join(stats)
            result += '\n'
        result += 'Home: ' + self.home + '\n'
        result += 'Last Game Date: '+self.home_last_game+'\n'
        result += 'Last Game Location: '+self.home_last_game_location+'\n'
        result += 'Win: '+self.home_result+'\n'
        result += 'Days Rest: '+self.home_days_rest+'\n'
        result += 'Distance Travelled: '+self.home_dist_travelled+'\n'
        result += 'Last 3 Games Rest: ,'+self.home_last_3_rest[1:-1]+'\n'
        result += 'Last 3 Games Distance Travelled: '+self.home_last_3_dist+'\n'
        for name, stats in self.home_scores.items():
            result += name + ',' + ','.join(stats)
            result += '\n'
        path = './game_csvs'
        fname = ("_".join(self.date.split("/")))+"_"+self.away.split(' ')[-1]+'At'+self.home.split(' ')[-1]
        if not os.path.exists(path):
            os.makedirs(path)
            print('Created path ' + path)
        f = open(os.path.join(path, fname+".csv"),"w+")
        f.write(result)
        f.close()
        print('Created file ' + fname+".csv")

    def table_to_json(self):
        player_folder_path = './player_jsons'
        if not os.path.exists(player_folder_path):
            os.makedirs(player_folder_path)
            print('Created path ' + player_folder_path)
        result = "{\n"
        result += '\"Date\": \"'+self.date+'\",\n'
        result += '\"Away\": {\n'
        result += '\"Name\": \"' + self.away + '\",\n'
        result += '\"Last Game\": {\n'
        result += '\"Date\": \"' + self.away_last_game + '\",\n'
        result += '\"Location\": \"' + self.away_last_game_location + '\"\n'
        result += '},\n'
        result += '\"Win\": ' + self.away_result + ',\n'
        result += '\"Days Rest\": ' + (self.away_days_rest if self.away_days_rest!="" else 'null') + ',\n'
        result += '\"Distance Travelled\": ' + (self.away_dist_travelled if self.away_dist_travelled!="" else 'null') + ',\n'
        result += '\"Last 3 Games Rest\": ' + self.away_last_3_rest + ',\n'
        result += '\"Last 3 Games Distance Travelled\": ' + self.away_last_3_dist + ',\n'
        result += '\"Players\": [\n'
        items = []
        for key in self.away_scores.keys():
            val = self.away_scores.get(key)[:]
            val.insert(0, key)
            items.append(val)
        header = items[0]
        players = items[1:-1]
        totals = items[-1]
        for i in range(len(players)):
            result += (',\n' if i!=0 else '')
            result += '{'
            player_result = "{"
            player_result += '\"Date\": \"'+self.date+'\",'
            player_name = ''
            for j in range(len(players[i])):
                player_result += "\n"
                if(self.is_number(players[i][j])):
                    if(players[i][j][0]=='.'):
                        result += (',\"' if j!=0 else '\"') + header[j] + '\": 0' + players[i][j]
                        player_result += (',\"' if j!=0 else '\"') + header[j] + '\": 0' + players[i][j]
                    elif(players[i][j][0]=='+'):
                        result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j][1:]
                        player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j][1:]
                    else:
                        result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j]
                        player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j]
                elif(':' in players[i][j]):
                    result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + self.time_to_float(players[i][j])
                    player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + self.time_to_float(players[i][j])
                elif(players[i][j]==''):
                    result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + 'null'
                    player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + 'null'
                else:
                    if(header[j]=='Name'):
                        player_name = '_'.join(players[i][j].split(' '))
                    result += (',\"' if j!=0 else '\"') + header[j] + '\": \"' + players[i][j] + '\"'
                    player_result += (',\"' if j!=0 else '\"') + header[j] + '\": \"' + players[i][j] + '\"'
            result += "}"
            player_result += "}"
            player_path = './player_jsons/' + player_name
            player_fname = (player_name + '-' + "_".join(self.date.split("/")))+"_"+self.away.split(' ')[-1]+'At'+self.home.split(' ')[-1]
            if not os.path.exists(player_path):
                os.makedirs(player_path)
                print('Created path ' + player_path)
            player_f = open(os.path.join(player_path, player_fname+".json"),"w+")
            player_f.write(player_result)
            player_f.close()
        result += '\n],\n'
        for i in range(len(totals)):
            if(i==0):
                result += '\"' + totals[0] +'\": {'
            else:
                if(self.is_number(totals[i])):
                    if(totals[i][0]=='.'):
                        result += (',\"' if i!=1 else '\"') + header[i] + '\": 0' + totals[i]
                    elif(totals[i][0]=='+'):
                        result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + totals[i][1:]
                    else:
                        result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + totals[i]
                elif(':' in totals[i]):
                    result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + self.time_to_float(totals[i])
                elif(totals[i]==''):
                    result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + 'null'
                else:
                    result += (',\"' if i!=1 else '\"') + header[i] + '\": \"' + totals[i] + '\"'
        result += "}\n"
        result += "},\n"
        result += '\"Home\": {\n'
        result += '\"Name\": \"' + self.home + '\",\n'
        result += '\"Last Game\": {\n'
        result += '\"Date\": \"' + self.home_last_game + '\",\n'
        result += '\"Location\": \"' + self.home_last_game_location + '\"\n'
        result += '},\n'
        result += '\"Win\": ' + self.home_result + ',\n'
        result += '\"Days Rest\": ' + (self.home_days_rest if self.home_days_rest!="" else 'null') + ',\n'
        result += '\"Distance Travelled\": ' + (self.home_dist_travelled if self.home_dist_travelled!="" else 'null') + ',\n'
        result += '\"Last 3 Games Rest\": ' + self.home_last_3_rest + ',\n'
        result += '\"Last 3 Games Distance Travelled\": ' + self.home_last_3_dist + ',\n'
        result += '\"Players\": [\n'
        items = []
        for key in self.home_scores.keys():
            val = self.home_scores.get(key)[:]
            val.insert(0, key)
            items.append(val)
        header = items[0]
        players = items[1:-1]
        totals = items[-1]
        for i in range(len(players)):
            result += (',\n' if i!=0 else '')
            result += '{'
            player_result = "{"
            player_result += '\"Date\": \"'+self.date+'\",'
            player_name = ''
            for j in range(len(players[i])):
                if(self.is_number(players[i][j])):
                    if(players[i][j][0]=='.'):
                        result += (',\"' if j!=0 else '\"') + header[j] + '\": 0' + players[i][j]
                        player_result += (',\"' if j!=0 else '\"') + header[j] + '\": 0' + players[i][j]
                    elif(players[i][j][0]=='+'):
                        result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j][1:]
                        player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j][1:]
                    else:
                        result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j]
                        player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + players[i][j]
                elif(':' in players[i][j]):
                    result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + self.time_to_float(players[i][j])
                    player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + self.time_to_float(players[i][j])
                elif(players[i][j]==''):
                    result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + 'null'
                    player_result += (',\"' if j!=0 else '\"') + header[j] + '\": ' + 'null'
                else:
                    if(header[j]=='Name'):
                        player_name = '_'.join(players[i][j].split(' '))
                    result += (',\"' if j!=0 else '\"') + header[j] + '\": \"' + players[i][j] + '\"'
                    player_result += (',\"' if j!=0 else '\"') + header[j] + '\": \"' + players[i][j] + '\"'
            result += "}"
            player_result += "}"
            player_path = './player_jsons/' + player_name
            player_fname = (player_name + '-' + "_".join(self.date.split("/")))+"_"+self.away.split(' ')[-1]+'At'+self.home.split(' ')[-1]
            if not os.path.exists(player_path):
                os.makedirs(player_path)
                print('Created path ' + player_path)
            player_f = open(os.path.join(player_path, player_fname+".json"),"w+")
            player_f.write(player_result)
            player_f.close()
        result += '\n],\n'
        for i in range(len(totals)):
            if(i==0):
                result += '\"' + totals[0] +'\": {'
            else:
                if(self.is_number(totals[i])):
                    if(totals[i][0]=='.'):
                        result += (',\"' if i!=1 else '\"') + header[i] + '\": 0' + totals[i]
                    elif(totals[i][0]=='+'):
                        result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + totals[i][1:]
                    else:
                        result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + totals[i]
                elif(':' in totals[i]):
                    result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + self.time_to_float(totals[i])
                elif(totals[i]==''):
                    result += (',\"' if i!=1 else '\"') + header[i] + '\": ' + 'null'
                else:
                    result += (',\"' if i!=1 else '\"') + header[i] + '\": \"' + totals[i] + '\"'
        result += "}\n"
        result += "}\n"
        result += "}"
        path = './game_jsons'
        fname = ("_".join(self.date.split("/")))+"_"+self.away.split(' ')[-1]+'At'+self.home.split(' ')[-1]
        if not os.path.exists(path):
            os.makedirs(path)
            print('Created path ' + path)
        f = open(os.path.join(path, fname+".json"),"w+")
        f.write(result)
        f.close()
        print('Created file ' + fname+".json")

    def set_date(self, date):
        mm, dd, yy = date.split('/')
        if(len(mm)<2):
            mm = '0' + mm
        if(len(dd)<2):
            dd = '0' + dd
        self.date = "/".join([yy, mm, dd])

    def get_dist_between_stadiums(self, name1, name2):
        latlon1 = stadiums.get(name1)
        latlon2 = stadiums.get(name2)
        if(latlon1 is None):
            print(name1 + " not found in stadiums dictionary")
        if(latlon2 is None):
            print(name2 + " not found in stadiums dictionary")
        lat1, lon1 = [radians(x) for x in latlon1]
        lat2, lon2 = [radians(x) for x in latlon2]
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2 
        c = 2 * atan2( sqrt(a), sqrt(1-a) ) 
        d = 3963.1676 * c #radius in miles so distance calculated is in miles
        return (int(d*10000)/10000) #convert to 4 decimal places

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def time_to_float(self, s):
        parts = s.split(':')
        secs = int((100*int(parts[1]))/60)
        return parts[0]+'.'+str(secs)

