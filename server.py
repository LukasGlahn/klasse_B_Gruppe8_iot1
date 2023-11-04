from socket import *
import datetime
import mysql.connector

##variabler til brug i resten af koden
decoded_message_list = []
last_decoded_message_list = []
elapsed_minutter = 0
elapsed_sekunder = 0
aktiv_kamp = 0
online_bruger = {}
komando_liste = ['tackling','aflevering','mål','headed_til_bold','hjørnespark','indkast','skud_på_mål','fik_frispark','lavede_frispark','står_stille','stoppede_mål','offside','gult_kort','rødt_kort','andet']
komando_liste_1 = ['tackling','aflevering']
komando_liste_2 = ['mål','headed_til_bold','hjørnespark','indkast','skud_på_mål','fik_frispark','lavede_frispark','står_stille','stoppede_mål','offside','gult_kort','rødt_kort','andet']
display_liste = ['',]
activ_pause = 0
pause_tid = 0

server_port = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('',server_port))
ehh = 'serveren har modtaget din besked'

db = mysql.connector.connect(
    host='10.0.0.5',
    user='root',
    passwd='',
    database='iot1'
)

mycursor = db.cursor()

## definitions
def time_elapsed():
    global elapsed_minutter
    global elapsed_sekunder
    stamp_time = datetime.datetime.now()
    hh = stamp_time.hour - start_time.hour
    mm = stamp_time.minute - start_time.minute
    ss = stamp_time.second - start_time.second

    elapsed_minutter = (hh * 60) + int(((mm*60)+(ss-pause_tid))/60)
    elapsed_sekunder = int((((hh*60+mm)*60)+(ss-pause_tid))%60)

print()
print('-----------------------------')
print('server er klar til at modtage')
print('-----------------------------')
print()

while True:
    message, client = server_socket.recvfrom(2048)
    decoded_message = message.decode()
    #print(decoded_message)
    #man komando chek
    if ',' in decoded_message:
        decoded_message_list = decoded_message.split(',')
        if decoded_message_list[0] == 'navn':
            online_bruger[str(client[0])] = decoded_message_list[1]
            server_socket.sendto('forbundet'.encode("utf-8"), client)
            #print(online_bruger)
        if decoded_message_list[0] in komando_liste_2 and aktiv_kamp == 1:
            time_elapsed()
            navn = online_bruger[str(client[0])]
            display_liste = [decoded_message_list[0],elapsed_minutter,elapsed_sekunder,navn,decoded_message_list[1],'null']
            server_socket.sendto(ehh.encode("utf-8"), client)
        if decoded_message_list[0] in komando_liste_1 and aktiv_kamp == 1:
            time_elapsed()
            navn = online_bruger[str(client[0])]
            display_liste = [decoded_message_list[0],elapsed_minutter,elapsed_sekunder,navn,decoded_message_list[1],decoded_message_list[2]]
            server_socket.sendto(ehh.encode("utf-8"), client)
        if decoded_message_list[0] in komando_liste and aktiv_kamp != 1:
            server_socket.sendto('Kampen er ikke i gang lige nu!'.encode("utf-8"), client)
    #sekonder komando chek
    if decoded_message == 'start' and aktiv_kamp == 0:
        start_time = datetime.datetime.now()
        aktiv_kamp = 1
        server_socket.sendto('kampen er begyndt'.encode("utf-8"), client)
        dato = f'{start_time.day}/{start_time.month}/{start_time.year}'
        kamp_start_klokken = f'{start_time.hour}:{start_time.minute}'
        mycursor.execute('INSERT INTO Kamp (dato, start_tid) VALUES (%s, %s)',(dato, kamp_start_klokken))
        kamp_id = mycursor.lastrowid
        db.commit()
    elif decoded_message == 'start' and aktiv_kamp == 1:
        server_socket.sendto('kampen er i gang'.encode("utf-8"), client)
    elif decoded_message == 'start_pause' and aktiv_kamp == 1:
        pause_start = datetime.datetime.now()
        aktiv_kamp = 2
        server_socket.sendto('pausen er started'.encode("utf-8"), client)
    elif decoded_message == 'slut_pause' and aktiv_kamp == 2:
        aktiv_kamp = 1
        stamp_time = datetime.datetime.now()
        hh = stamp_time.hour - pause_start.hour
        mm = stamp_time.minute - pause_start.minute
        ss = stamp_time.second - pause_start.second
        pause_tid = pause_tid + int(((hh*60+mm)*60)+ss)
        server_socket.sendto('pausen er sluttet'.encode("utf-8"), client)
    elif decoded_message == 'slut' and aktiv_kamp == 1:
        aktiv_kamp = 0
        stop_time = datetime.datetime.now()
        server_socket.sendto('kampen er sluttet'.encode("utf-8"), client)
        kamp_slut_klokken = f'{stop_time.hour}:{stop_time.minute}'
        mycursor.execute("UPDATE Kamp SET slut_tid = %s WHERE id = %s",(kamp_slut_klokken, kamp_id))
        db.commit()
        print(f'\n Slut på kampen kl {kamp_slut_klokken}')
    
    #visuelle del
    if decoded_message_list[0] in komando_liste and aktiv_kamp == 1 and len(display_liste) > 5:
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
        response_print = komando_response[display_liste[0]]
        print(f'{response_print}\ntid i minutter:   {display_liste[1]}:{"{:02d}".format(display_liste[2])}    Observeret af: {display_liste[3]}\n')
        tid_i_kamp = f'{display_liste[1]}:{"{:02d}".format(display_liste[2])}'
        if display_liste[0] in komando_liste_1:
            mycursor.execute('INSERT INTO Observationer (kommando, tid_i_kamp, observant, spiller_1, spiller_2, kamp_id) VALUES (%s, %s, %s, %s, %s, %s)',(display_liste[0], tid_i_kamp, display_liste[3], display_liste[4],display_liste[5],kamp_id))
        elif display_liste[0] in komando_liste_2 and display_liste[0] != 'andet':
            mycursor.execute('INSERT INTO Observationer (kommando, tid_i_kamp, observant, spiller_1, kamp_id) VALUES (%s, %s, %s, %s, %s)',(display_liste[0], tid_i_kamp, display_liste[3], display_liste[4], kamp_id))
        elif display_liste[0] == 'andet':
            mycursor.execute('INSERT INTO Observationer (kommando, tid_i_kamp, observant, andet, kamp_id) VALUES (%s, %s, %s, %s, %s)',(display_liste[0], tid_i_kamp, display_liste[3], display_liste[4], kamp_id))
        db.commit()