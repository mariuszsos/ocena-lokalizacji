import numpy as np
from math import sin, cos, sqrt, atan2, radians

#liczy dlugosc odcinka pomiedzy dwoma punktami określonymi wspolrzednymi geograficznymi - w km
def distance_to_km():
    R = 6373.0

    lat1 = radians(52.0)
    lon1 = radians(21.0)
    lat2 = radians(52.0)
    lon2 = radians(21.001)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

#tworzy plik : numer przystanku, odjazdy w dzien, odjazdy w nocy
def dep_extraction():
    dep_path = 'include/data/przystanki_odjazdy.csv'
    day_dep = 0
    night_dep = 0

    write_file = open("include/data/departures.txt", "w")

    with open(dep_path) as f:
        for row in f:
            tmp = row.strip().split("\t")
            for ind, dep_time in enumerate(tmp):
                if ind == 0:
                    continue
                if dep_time[0:2] != "<<":
                    if int(dep_time[0:2]) > 23:
                        tmp1 = str(int(dep_time[0:2]) - 24)
                        if len(tmp1) == 1:
                            tmp1 = "0" + tmp1
                        dep_time = tmp1 + dep_time[2:5]
                    if int(dep_time[0:2]) >= 5 and int(dep_time[0:2]) <= 23:
                        day_dep = day_dep + 1
                    if int(dep_time[0:2]) >= 0 and int(dep_time[0:2]) <= 4:
                        night_dep = night_dep + 1
            if len(row.strip().split("\t")) == 1:
                continue
            write_file.write("{0},{1},{2}\n".format(tmp[0], day_dep, night_dep))
            day_dep = 0
            night_dep = 0

    write_file.close()


#Z oficjalnego pliku ZTM wyciąga numer przystanku (grupy) oraz jego współrzędne geograficzne
def cords_extraction():
    read_next_flag = 0
    stop_number = ""
    Y = []
    X = []

    read_file = open("dane.txt", "r", encoding="cp1250")
    write_file = open("include/data/coordinates.txt", "w")

    for row in read_file:
        if row.find("*PR") != -1:
            read_next_flag = 1
        if read_next_flag == 1 and row.find("Y= ") != -1:
            tmp = row.split()
            stop_number = tmp[0][0:4]
            X.append(tmp[tmp.index("Y=")+1])
            Y.append(tmp[tmp.index("X=")+1])
        if row.find("#PR") != -1 and len(Y) != 0:
            write_file.writelines('{0},{1},{2}\n'.format(stop_number,
                                                np.round(np.average(np.array(Y).astype(np.float)), 6),
                                                np.round(np.average(np.array(X).astype(np.float)), 6)
                                                        ))
            Y = []
            X = []
            read_next_flag = 0

    write_file.close()

#liczy dystans w metrach po wspolrzednych
def distance_meters(x1, y1, x2, y2):
    R = 6378.137
    dLat = (x2 * np.pi / 180) - (x1 * np.pi / 180)
    dLon = (y2 * np.pi / 180) - (y1 * np.pi / 180)
    a = (np.sin(dLat / 2) * np.sin(dLat / 2)) + \
        (np.cos(x1 * np.pi / 180) * np.cos(x2 * np.pi / 180) * np.sin(dLon / 2) * np.sin(dLon / 2))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = R * c
    return d * 1000


#licz ile odjazdow w dzien i w nocy w danej okolicy i promieniu 
def calculate_tranport(x, y, distance):
    departure_count = []
    coords = []
    stops_in_area = []
    day_sum = 0
    night_sum = 0
    x = float(x)
    y = float(y)
    

    file_dep = open("include/data/departures.txt", "r")
    file_coords = open("include/data/coordinates.txt", "r")

    for row in file_dep:
        departure_count.append(row.split('\n')[0].split(','))

    for row in file_coords:
        coords.append(row)
        
    for c in coords:
        tmp = c.split(',')
        if distance_meters(x, y, float(tmp[2].split('\n')[0]), float(tmp[1])) <= distance:
            stops_in_area.append(tmp[0])

    print(stops_in_area)

    for s in stops_in_area:
        if s in np.array(departure_count)[:, 0]:
            if len(np.argwhere(np.array(departure_count)[:, 0] == s)) != 0:
                day_sum = day_sum + int(np.array(departure_count)[np.where(np.array(departure_count)[:, 0] == s)][0, 1])
                night_sum = night_sum + int(
                    np.array(departure_count)[np.where(np.array(departure_count)[:, 0] == s)][0, 2])

    return day_sum, night_sum

#liczy punkt w ktorym jest najwiecej odjazdow o promieniu 400m
def max_departures():
    #52.183502, 20.931941 - dolny lewy rog obszaru
    Xp = 52.183502
    Yp = 20.931941

    #52.323338, 21.068537 - gorny prawy róg obszaru
    Xk = 52.323338
    Yk = 21.068537

    write_file = open("include/data/max_departures.txt", "w")

    step = 0.001
    distance = 400

    for x in np.arange(Xp, Xk, step):
        for y in np.arange(Yp, Yk, step):
            write_file.writelines('{},{},{},{}\n'.format(
                                                        x,y,
                                                        calculate_tranport(x,y,distance)[0],
                                                        calculate_tranport(x,y,distance)[1])
            )

    write_file.close()