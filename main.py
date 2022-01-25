from tkinter import *
import numpy as np
import json
import requests

def distance_meters(x1, y1, x2, y2):
    R = 6378.137
    dLat = (x2 * np.pi / 180) - (x1 * np.pi / 180)
    dLon = (y2 * np.pi / 180) - (y1 * np.pi / 180)
    a = (np.sin(dLat / 2) * np.sin(dLat / 2)) + \
        (np.cos(x1 * np.pi / 180) * np.cos(x2 * np.pi / 180) * np.sin(dLon / 2) * np.sin(dLon / 2))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = R * c
    return d * 1000

def check_places(x,y):
    x = float(x)
    y = float(y)
    places = [] 
    found = []    

    #print(x,y)
    objects = open("include/data/places.txt", "r")
    for row in objects:
        places.append(row.split('\n')[0].split(','))

    #print(places)
    for place in places:
        if(x >= float(place[1]) and x <= float(place[3]) and y >= float(place[2]) and y <= float(place[4])):
            found.append(place[0])

    #print(found)
    return found

def get_location_by_name(name):  
    url = "https://eu1.locationiq.com/v1/search.php"

    data = {
        'key': 'pk.87e924fafcf6a1e889481d0981023d7b',
        'q': name,
        'format': 'json'
    }


    #print(data)
    response = requests.get(url, params=data)
    #print(response.text)

    api_data = json.loads(response.text)
    x = api_data[0]["lat"]
    y = api_data[0]["lon"]
    name = api_data[0]["display_name"]
    
    return x,y,name

def grade_category(grade):
    result = 'Błąd'
    if (grade == -1):
        result = 'Ocena 5/5 - świetnie skomunikowana okolica,\n' \
                 'niedaleko znajduje się węzeł komunikacyjny - '
    if (grade == 0):
        result = 'Ocena 0/5 - brak odjazdów w okolicy'
    if (grade == 1):
        result = 'Ocena 1/5 - źle skomunikowana okolica'
    if (grade == 2):
        result = 'Ocena 2/5 - słabo skomunikowana okolica'
    if (grade == 3):
        result = 'Ocena 3/5 - średnio skomunikowana okolica'
    if (grade == 4):
        result = 'Ocena 4/5 - bardzo dobrze skomunikowana okolica'
    if (grade == 5):
        result = 'Ocena 5/5 - świetnie skomunikowana okolica'
    return result

def calculate_grade(dd, dn):
    #maxDay = 14600
    gradeDay = 0

    gradeNight = 0
    maxNight = 453
    gradeNightRatio = dn/maxNight

    if (dd > 0 and dd <= 619):
        gradeDay = 1
    if (dd > 619 and dd <= 1312):
        gradeDay = 2
    if (dd > 1312 and dd <= 2038):
        gradeDay = 3
    if (dd > 2038 and dd <= 3076):
        gradeDay = 4
    if (dd > 3076):
        gradeDay = 5

    if (gradeNightRatio > 0 and gradeNightRatio <= 0.2):
        gradeNight = 1
    if (gradeNightRatio > 0.2 and gradeNightRatio <= 0.4):
        gradeNight = 2
    if (gradeNightRatio > 0.4 and gradeNightRatio <= 0.6):
        gradeNight = 3
    if (gradeNightRatio > 0.6 and gradeNightRatio <= 0.8):
        gradeNight = 4
    if (gradeNightRatio > 0.8 and gradeNightRatio <= 1):
        gradeNight = 5

    return gradeDay, gradeNight

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

def cleanLabels():
    LblDay.config(text='')
    LblNrDay.config(text='')
    LblNight.config(text='')
    LblNrNight.config(text='')
    LblResultNight.config(text='')
    LblResultDay.config(text='')

def clickButton():
    cleanLabels()
    adress = adres.get()

    try:
        dane1 = get_location_by_name(adress)
        x = dane1[0]
        y = dane1[1]

        dane2 = calculate_tranport(float(x), float(y), 400)
        obiekty = check_places(float(x),float(y))

        grade = calculate_grade(dane2[0], dane2[1])
        if obiekty:
            catgradeDay = grade_category(-1) + check_places(float(x),float(y))[0]
            catgradeNight = grade_category(grade[1])
        else:
            catgradeDay = grade_category(grade[0])
            catgradeNight = grade_category(grade[1])

        LblDay.config(text='Odjazdy w dzień:')
        LblNrDay.config(text=dane2[0])

        LblNight.config(text='Odjazdy w nocy:')
        LblNrNight.config(text=dane2[1])

        LblResultDay.config(text=catgradeDay)
        LblResultNight.config(text=catgradeNight)

    except:
        LblDay.config(text='Wystąpił błąd')


window = Tk()
window.geometry('375x480')
window.resizable(0,0)
window.title('Jak dobrze jesteś skomunikowany?')
window.configure(background='white')

adres = StringVar()

image1 = PhotoImage(file='include/img/bus.png')
Label(window, image=image1, bg='white').grid(row=0, column=0, sticky=W)

Label(window, text='Sprawdź, czy dana lokalizacja jest dobrze skomunikowana w Warszawie', bg='white', fg='black', font='none 11 bold', wraplength=369, justify="center").grid(
    row=1,
    column=0,
    sticky=N,
    padx=5
)

#Wpisz adres - row2
Label(window, text='Wpisz adres', bg='white', fg='black').grid(
    row=2,
    column=0,
    sticky=NW,
    padx=(10, 0)
)

#Input wpisz_adres - row2
Entry(window, width=25, bg='white', highlightbackground='white', textvariable=adres).grid(
    row=2,
    column=0,
    sticky=E,
    padx=(0, 10)
)

#Send button - row4
CheckBtn = Button(window, text='Sprawdź', width=10, highlightbackground='white', command=clickButton)
CheckBtn.grid(
    row=4,
    column=0,
    sticky=N,
    pady=(5, 0)
)

#<hr> w pythonie - row5
Frame(window,height=1,width=350,bg="#333333").grid(
    row=5,
    column=0,
    sticky=N,
    pady=10
)

#Odjazdy w ciągu dnia - row6
LblDay = Label(window, text='Odjazdy w ciągu dnia:', bg='white', fg='black')
LblDay.grid(
    row=6,
    column=0,
    sticky=NW,
    padx=(10, 0)
)

# nr odjazdow dzien - row6
LblNrDay = Label(window, text='1523', bg='white', fg='black')
LblNrDay.grid(
    row=6,
    column=0,
    sticky=N
)

#Informacja o kategorii 1-5 zaludnienia - row9
LblResultDay = Label(window, text='', bg='white', fg='black', font='none 11 bold', wraplength=369, justify="center")
LblResultDay.grid(
    row=7,
    column=0,
    sticky=N,
    pady=(0, 10),
    padx=10
)


#Odjazdy w ciągu nocy - row7
LblNight = Label(window, text='Odjazdy w nocy:', bg='white', fg='black')
LblNight.grid(
    row=8,
    column=0,
    sticky=NW,
    padx=(10, 0)
)
#nr odjazdow noc - row7
LblNrNight = Label(window, text='22', bg='white', fg='black')
LblNrNight.grid(
    row=8,
    column=0,
    sticky=N,
    padx=10
)


#Informacja o kategorii 1-5 zaludnienia - row10
LblResultNight = Label(window, text='', bg='white', fg='black', font='none 11 bold', wraplength=369, justify="center")
LblResultNight.grid(
    row=9,
    column=0,
    sticky=N
)

#Clean button - row11
CleanBtn = Button(window, text='Wyczyść', width=10, highlightbackground='white', command=cleanLabels)
CleanBtn.grid(
    row=10,
    column=0,
    sticky=W,
    padx=10
)

#footer
Label(window, text='Projekt systemy eksperckie | WZIM SGGW', bg='white', fg='black', font='none 8', wraplength=369, justify="center").grid(
    row=10,
    column=0,
    sticky=SE,
    padx=(0, 10)
)

#wyczysc na poczatku apki
cleanLabels()
window.mainloop()