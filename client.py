from socket import *
from os import system, name

kommando_liste = ['start','start_pause','slut_pause','slut','tackling','aflevering','mål','headed_til_bold','hjørnespark','indkast','skud_på_mål','fik_frispark','lavede_frispark','står_stille','stoppede_mål','offside','gult_kort','rødt_kort','andet']
tal = 0
komando_liste_1 = ['tackling','aflevering']
komando_liste_2 = ['mål','headed_til_bold','hjørnespark','indkast','skud_på_mål','fik_frispark','lavede_frispark','står_stille','stoppede_mål','offside','gult_kort','rødt_kort','andet']
kommando_liste_3 = ['start','slut','start_pause','slut_pause']
observation = ''

def clear():
   # for windows
   if name == 'nt':
      _ = system('cls')

   # for mac and linux
   else:
    _ = system('clear')


kommando_response = {
    'start' : 'START', 
    'start_pause' : 'Start pause',
    'slut_pause' : 'Slut pause',
    'slut' : 'SLUT',
    'tackling' : ['Hvilket trøjenummer tackler: ','Hvilet trøjenummer bliver tacklet: '],
    'aflevering' : ['Hvilket trøjenummer afleverede bolden: ', 'Hvilket trøjenummer tæmmede bolden: '],
    'mål' : 'Hvilket trøjenummer scorede mål?: ',
    'headed_til_bold' : 'Hvilket trøjenummer headed til bolden?: ',
    'hjørnespark' : 'Hvilket trøjenummer sparker hjørnespark?: ',
    'indkast' : 'Hvilket trøjenummer kastede et indkast?: ',
    'skud_på_mål' : 'Hvilket trøjenummer skyder på mål?: ',
    'fik_frispark' : 'Hvilket trøjenummer vandt et frispark?: ',
    'lavede_frispark' : 'Hvilket trøjenummer begik et frispark?: ',
    'står_stille' : 'Hvilket trøjenummer står stille?: ',
    'stoppede_mål' : 'Hvilket trøjenummer stoppede bolden for at gå ind?: ',
    'offside' : 'Hvilket trøjenummer står offside?: ',
    'gult_kort' : 'Hvilket trøjenummer fik et gult kort?: ',
    'rødt_kort' : 'Hvilket trøjenummer fik et rødt kort?: ',
    'andet' : 'Skriv din observation: ',

}


serverName = '10.0.0.5'
serverPort = 12000
clintSocket = socket(AF_INET, SOCK_DGRAM)

print()
print('---------------------------')
print('Klient er klar til at sende')
print('---------------------------')
print()

klient_navn = input("Navn:")
navn_message = f"navn,{klient_navn}"
clintSocket.sendto(navn_message.encode("utf-8"), (serverName, serverPort))
response, server_address = clintSocket.recvfrom(2048)
while True:
    clear()
    for komandoer in kommando_liste:
        print(tal,komandoer)
        tal = tal + 1
    print (response.decode())
    while True:
        val = int(input('Vælg tallet på den kommando du vil bruge: '))
        if val+1 > len(kommando_liste) or val < 0:
            print('Prøv igen tallet er ikke en komando!')
        else:
            break


    if kommando_liste[val] in komando_liste_1:
        val_liste = kommando_response[kommando_liste[val]]
        spiller_1 = input(val_liste[0])
        spiller_2 = input(val_liste[1])
        observation = f'{kommando_liste[val]},{spiller_1},{spiller_2}' 

    if kommando_liste[val] in komando_liste_2:
        val_liste = kommando_response[kommando_liste[val]]
        spiller_1 = input(val_liste)
        observation = f'{kommando_liste[val]},{spiller_1}'

    if kommando_liste[val] in kommando_liste_3:
        val_liste = kommando_response[kommando_liste[val]]
        spiller_1 = input(val_liste)
        observation = f'{kommando_liste[val]}'
    clintSocket.sendto(observation.encode("utf-8"), (serverName, serverPort))
    response, server_address = clintSocket.recvfrom(2048)
    
    tal = 0
    