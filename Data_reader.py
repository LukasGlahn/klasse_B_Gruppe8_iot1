import mysql.connector
from os import system, name

def clear():
   # for windows
   if name == 'nt':
      _ = system('cls')

   # for mac and linux
   else:
    _ = system('clear')

db = mysql.connector.connect(
    host='10.0.0.5',
    user='root',
    passwd='',
    database='iot1'
)


mycursor = db.cursor()
kamp_id = 0
komando_liste = ['tackling','aflevering','mål','headed_til_bold','hjørnespark','indkast','skud_på_mål','fik_frispark','lavede_frispark','står_stille','stoppede_mål','offside','gult_kort','rødt_kort']
komando_nr_display = 0
komando = ''
spiller = -1
resultater = 0

while True:
    svar = input('Ved du hvilket kamp id du vil kigge på?(Y/N): ')
    if svar.upper() in ('Y','YES','JA'):
        kamp_id = input("Hvad er id'et til kampen: ")
        break
    elif svar.upper() in ('N','NO','NEJ'):
        svar = input('Ved du hvilken dag kampen blev spillet?(Y/N): ')
        if svar.upper() in ('Y','YES','JA'):
            svar = input('Hvilken dag var kampen?put ikke 0 foran dag og måned(dd/mm/yyyy): ')
            mycursor.execute(f"SELECT * FROM Kamp WHERE dato LIKE '{svar}'")
            for i in mycursor:
              print(i)
            kamp_id = input('Hvilket id er det?: ')
            break
        if svar.upper() in ('N','NO','NEJ'):
            mycursor.execute('SELECT * FROM Kamp')
            for i in mycursor:
              print(i)
            kamp_id = input('Hvilket id vil du kigge på?: ')
            break

mycursor.execute(f"SELECT start_tid, slut_tid FROM Kamp WHERE id = {kamp_id};")

for i in mycursor:
   kamp_info = i

while True:
    svar = input('er der en bestemt spiller du vil kigge på?(Y/N): ')
    if svar.upper() in ('Y','YES','JA'):
       spiller = int(input('Hvilket trøjenummer har spilleren?: '))
    else:
       spiller = -1

    svar = input('er der en bestemt kommando du vil kigge efter?(Y/N): ')
    if svar.upper() in ('Y','YES','JA'):
        for komandoer in komando_liste:
            print(komando_nr_display,komandoer)
            komando_nr_display = komando_nr_display + 1
        komando_nr = int(input('Skriv nummeret på den kommando som du vil se på?: '))
        komando = komando_liste[komando_nr]
    else:
       komando = ''

    if spiller < 0 and komando not in komando_liste:
        mycursor.execute(f"SELECT * FROM Observationer WHERE kamp_id = {kamp_id};")
    elif spiller >= 0 and komando not in komando_liste:
        mycursor.execute(f"SELECT * FROM Observationer WHERE kamp_id = {kamp_id} AND spiller_1 = {spiller};")
    elif spiller >= 0 and komando in komando_liste:
        mycursor.execute(f"SELECT * FROM Observationer WHERE kamp_id = {kamp_id} AND spiller_1 = {spiller} AND kommando LIKE '{komando}';")
    elif spiller < 0 and komando in komando_liste:
        mycursor.execute(f"SELECT * FROM Observationer WHERE kamp_id = {kamp_id} AND kommando LIKE '{komando}';")

    komando_nr_display = 0

    clear()

    print(f'kampen startede kl {kamp_info[0]}')

    for i in mycursor:
        display_liste = i
        if display_liste[1] in komando_liste:
            komando_response = {
                'tackling' : f'Spiller nr {display_liste[4]} tacklede spiller nr {display_liste[5]}',
                'mål' : f'Spiller nr {display_liste[4]} scorede et mål',
                'aflevering' : f'Spiller {display_liste[4]} afleverede til spiller nr {display_liste[5]}',
                'hjørnespark' : f'Spiller nr {display_liste[4]} lavede et hjørne spark',
                'indkast' : f'Spiller nr {display_liste[4]} lavede et indkast',
                'skud_på_mål' : f'Spiller nr {display_liste[4]} skud på målet',
                'headed_til_bold' : f'Spiller nr {display_liste[4]} headede bolden',
                'fik_frispark' : f'Spiller nr {display_liste[4]} fik frispark',
                'lavede_frispark' : f'Spiller nr {display_liste[4]} lavede et frispark',
                'står_stille' : f'Spiller nr {display_liste[4]} har stået stille i noget tid',
                'stoppede_mål' : f'Spiller nr {display_liste[4]} stoppede bolden fra at gå i mål',
                'offside' : f'Spiller nr {display_liste[4]} er offside',
                'gult_kort' : f'Spiller nr {display_liste[4]} fik et gult kort',
                'rødt_kort' : f'Spiller nr {display_liste[4]} fik et rødt kort',
                'andet' : f'{display_liste[4]}'
            }
            print()
            response_print = komando_response[display_liste[1]]
            print(f'{response_print}\ntid i minutter:   {display_liste[2]}    Observeret af: {display_liste[3]}\n')
        else:
            print(f'{display_liste[6]}\ntid i minutter:   {display_liste[2]}    Observeret af: {display_liste[3]}\n')
        resultater = resultater + 1
    
    print(f'kampen sluttede kl {kamp_info[1]}')
    print(f'der er {resultater} resultat(er)')
    resultater = 0