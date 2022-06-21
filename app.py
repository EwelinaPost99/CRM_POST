import requests
from flask import Flask, render_template, redirect, url_for, request, session, g
import config
import json
from pyairtable import Api, Base, Table
from pyairtable.formulas import match



app = Flask(__name__)
app.config.from_object(config.config['development'])
headers = {'authorization': 'Bearer {}'.format(app.config['AIRTABLE_KEY']), 'content-type': 'application/json'}

api = Api('keyacSDzFPmDJAy3f')

class User:
    def __init__(self, id, name, username, teamid, password):
        self.id = id
        self.username = username
        self.name = name
        self.password = password
        self.teamid = teamid

    def __repr__(self):
        return f'<User: {self.username}>'

class Admin:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<Admin: {self.username}>'

url3 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/PRACOWNICY'
r3 = requests.get(url3, headers=headers)
result3 = json.loads(r3.text)

url_szanse = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/SZANSE'
r_szanse = requests.get(url_szanse, headers=headers)
result_szanse = json.loads(r_szanse.text)

url_firmy = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/FIRMY'
r_firmy = requests.get(url_firmy, headers=headers)
result_firmy = json.loads(r_firmy.text)


users = []

for x in range(len(result3['records'])):
    users.append(User(id=x, username=result3['records'][x]['fields']['EMAIL'], password=result3['records'][x]['fields']['HASLO'],
                      name=result3['records'][x]['fields']['IMIE']+ " " + result3['records'][x]['fields']['NAZWISKO'], teamid=result3['records'][x]['fields']['TEAM_ID']))

admins = []

admins.append(Admin(id="1", username="Admin", password="Admin"))

app.secret_key = 'somesecretkeythatonlyishouldknow'

table = Table('keyacSDzFPmDJAy3f', 'appQpPkjiYg5zo4kc', 'tblgjWST85f7OIW5A')
table_szanse = Table('keyacSDzFPmDJAy3f', 'appQpPkjiYg5zo4kc', 'tblrlz3CEhS5C02v7')
table_kontakty = Table('keyacSDzFPmDJAy3f', 'appQpPkjiYg5zo4kc', 'tblJXBc70FT9TGQE3')
table_firmy = Table('keyacSDzFPmDJAy3f', 'appQpPkjiYg5zo4kc', 'tblxWO62cU9AyuuRm')
table_zadania = Table('keyacSDzFPmDJAy3f', 'appQpPkjiYg5zo4kc', 'tblC0Q9CKgfQGl64i')

@app.route('/adminPanel')
def adminPanel():
    if not g.admin:
        return redirect(url_for('loginadmin'))

    url1 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/PRACOWNICY'
    r1 = requests.get(url1, headers=headers)
    result1 = json.loads(r1.text)

    return render_template('users.html', **locals())

@app.route('/index')
def index():
    if not g.user:
        return redirect(url_for('login'))
    site_name = "Strona główna"

    formula = match({"WLASCICIEL": g.user.teamid})
    formula2 = match({"WYKONAWCA": g.user.teamid})

    wlasciciel = table_szanse.all(formula=formula)
    ilosc_szans=0
    zrealizowane_szanse=0
    wartosc_szans=0
    for i in range(len(wlasciciel)):
        wlasciciel=wlasciciel[i]
        #szanse_user = (wlasciciel['fields']['FIRMA'])
        if(wlasciciel['fields']['STATUS'] == 'Podpisano umowę' or wlasciciel['fields']['STATUS'] == 'Przyjęto płatność'):
            wartosc_szans = wartosc_szans + float(wlasciciel['fields']['WARTOSC'])
            ilosc_szans = ilosc_szans +1
            zrealizowane_szanse = zrealizowane_szanse+1
        else:
            ilosc_szans = ilosc_szans +1


        #szanse_user = (result_szanse['records'][g.user.id]['fields']['FIRMA'])
        #szanse_usera.append(api.get(base_id='appQpPkjiYg5zo4kc', table_name='FIRMY', record_id=szanse_user[0]))
        #nazwa_firmy.append(szanse_usera['fields']['NAZWA'])
        #szanse_usera_data.append(wlasciciel['fields']['DATA_FINALIZACJI'])
        #zrodlo_szansy.append(wlasciciel['fields']['ZRODLO'])
        #nazwy_produktow.append(wlasciciel['fields']['NAZWY_PRODUKTOW'])

    termin_wykonania_t=[]
    wlasciciel2 = table_zadania.all(formula=formula2)
    for i in range(len(wlasciciel2)):
        wlasciciel2=wlasciciel2[i]
        #nazwa_zadania = wlasciciel2['fields']['NAZWA']
        if('ZREALIZOWANO' not in wlasciciel2['fields']):
            termin_wykonania_t.append(wlasciciel2['fields']['TERMIN_WYKONANIA'])
        #notatki = wlasciciel2['fields']['NOTATKI']
        #zrealizowano = wlasciciel2['fields']['ZREALIZOWANO']

    if(len(termin_wykonania_t)>0):
        min_value = min(termin_wykonania_t)
        min_index = termin_wykonania_t.index(min_value)


        wlasciciel2 = table_zadania.all(formula=formula2)
        wlasciciel2=wlasciciel2[0]
        id_zadania = wlasciciel2['id']
        nazwa_zadania = wlasciciel2['fields']['NAZWA']
        termin_wykonania = wlasciciel2['fields']['TERMIN_WYKONANIA']
        if('NOTATKI' in wlasciciel2['fields']):
                notatki = wlasciciel2['fields']['NOTATKI']
        #zrealizowano = wlasciciel2['fields']['ZREALIZOWANO']
        #@app.route('/wykonane')
        #def wykonane():
        #    table_zadania.update(wlasciciel2['id'], {"ZREALIZOWANO": True}, replace=True)
        #    return redirect(url_for('index'))

    else:
        nazwa_zadania = 'Nie masz aktualnie oczekujących zadań'

    return render_template('index.html', **locals())

@app.route('/companies')
def companies():
    if not g.user:
        return redirect(url_for('login'))
    site_name = "Firmy"
    url_co = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/FIRMY'
    r_co = requests.get(url_co, headers=headers)
    result_co = json.loads(r_co.text)

    tabela_ch=[]
    tabela_n=[]

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['SZANSE'])
        record = api.get('appQpPkjiYg5zo4kc', 'SZANSE', tabela_ch[i][0])
        tabela_n.append(record['fields']['NAZWY_PRODUKTOW'])
        result_co['records'][i]['fields']['SZANSE'] = tabela_n[i]

    tabela_ch = []
    tabela_n = []

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['OSOBY_KONTAKTOWE'])
        record = api.get('appQpPkjiYg5zo4kc', 'KONTAKTY', tabela_ch[i][0])
        tabela_n.append(record['fields']['EMAIL'])
        result_co['records'][i]['fields']['OSOBY_KONTAKTOWE'] = tabela_n[i]




    #formula4 = match({"ID_rekordu": 'recf2KD3E8czN9w1b'})
    #wlasciciel19 = table_szanse.all(formula=formula4)
    #record = api.match('keyacSDzFPmDJAy3f', 'table_name', 'Employee Id', 'recf2KD3E8czN9w1b')
    #print(record)
    #print(result_co['records']['fields']['SZANSE'])
    #'keyacSDzFPmDJAy3f', 'appQpPkjiYg5zo4kc', 'tblrlz3CEhS5C02v7'
    return render_template('companies.html', **locals())

@app.route('/contacts')
def contacts():
    if not g.user:
        return redirect(url_for('login'))
    site_name="Osoby kontaktowe"
    url_co = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/KONTAKTY'
    r_co = requests.get(url_co, headers=headers)
    result_co = json.loads(r_co.text)

    tabela_ch = []
    tabela_n = []

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['SZANSE'])
        record = api.get('appQpPkjiYg5zo4kc', 'SZANSE', tabela_ch[i][0])
        tabela_n.append(record['fields']['NAZWY_PRODUKTOW'])
        result_co['records'][i]['fields']['SZANSE'] = tabela_n[i]

    tabela_ch = []
    tabela_n = []

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['FIRMA'])
        record = api.get('appQpPkjiYg5zo4kc', 'FIRMY', tabela_ch[i][0])
        tabela_n.append(record['fields']['NAZWA'])
        result_co['records'][i]['fields']['FIRMA'] = tabela_n[i]

    return render_template('contacts.html', **locals())

@app.route('/chances')
def chances():
    if not g.user:
        return redirect(url_for('login'))
    site_name = "Szanse"
    url_co = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/SZANSE'
    r_co = requests.get(url_co, headers=headers)
    result_co = json.loads(r_co.text)

    tabela_ch = []
    tabela_n = []

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['WLASCICIEL'])
        record = api.get('appQpPkjiYg5zo4kc', 'PRACOWNICY', tabela_ch[i][0])
        tabela_n.append(record['fields']['EMAIL'])
        result_co['records'][i]['fields']['WLASCICIEL'] = tabela_n[i]

    tabela_ch = []
    tabela_n = []

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['FIRMA'])
        record = api.get('appQpPkjiYg5zo4kc', 'FIRMY', tabela_ch[i][0])
        tabela_n.append(record['fields']['NAZWA'])
        result_co['records'][i]['fields']['FIRMA'] = tabela_n[i]

    tabela_ch = []
    tabela_n = []

    for i in range(len(result_co['records'])):
        tabela_ch.append(result_co['records'][i]['fields']['OSOBA_KONTAKTOWA'])
        record = api.get('appQpPkjiYg5zo4kc', 'KONTAKTY', tabela_ch[i][0])
        tabela_n.append(record['fields']['EMAIL'])
        result_co['records'][i]['fields']['OSOBA_KONTAKTOWA'] = tabela_n[i]

    return render_template('chances.html', **locals())


@app.route('/addUser', methods=["GET", "POST"])
def addUser():
    if not g.admin:
        return redirect(url_for('loginadmin'))
    url2 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/PRACOWNICY'
    r2 = requests.get(url2, headers=headers)
    result2 = json.loads(r2.text)

    if request.method == 'POST':
        payload = {
                    "records": [
                        {
                            "fields": {
                                "TEAM_ID": request.form['TEAM_ID'],
                                "IMIE": request.form['IMIE'],
                                "NAZWISKO": request.form['NAZWISKO'],
                                "STANOWISKO": request.form['STANOWISKO'],
                                "EMAIL": request.form['EMAIL'],
                                "TELEFON": request.form['TELEFON'],
                                "HASLO": request.form['HASLO']
                            }
                        }
            ]
        }
        requests.post("https://api.airtable.com/v0/appQpPkjiYg5zo4kc/PRACOWNICY", json=payload, headers=headers)
        return redirect(url_for('index'))

    return render_template('addUser.html', **locals())

@app.route('/addChance', methods=["GET", "POST"])
def addChance():
    if not g.user:
        return redirect(url_for('login'))
    url2 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/SZANSE'
    r2 = requests.get(url2, headers=headers)
    result2 = json.loads(r2.text)

    if request.method == 'POST':
        payload = {
                    "records": [
                        {
                            "fields": {
                                "ID_SZANSY": request.form['ID_SZANSY'],
                                "NAZWA": request.form['NAZWA'],
                                "WLASCICIEL": request.form['WLASCICIEL'],
                                "FIRMA": request.form['FIRMA'],
                                "OSOBA_KONTAKTOWA": request.form['OSOBA_KONTAKTOWA'],
                                "DATA_FINALIZACJI": request.form['DATA_FINALIZACJI'],
                                "ZRODLO": request.form['ZRODLO'],
                                "NAZWY_PRODUKTOW": request.form['NAZWY_PRODUKTOW'],
                                "WARTOSC": request.form['WARTOSC'],
                                "STATUS": request.form['STATUS']
                            }
                        }
            ]
        }
        requests.post("https://api.airtable.com/v0/appQpPkjiYg5zo4kc/SZANSE", json=payload, headers=headers)
        return redirect(url_for('chances'))

    return render_template('addChance.html', **locals())

@app.route('/addTask', methods=["GET", "POST"])
def addTask():
    if not g.user:
        return redirect(url_for('login'))
    url2 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/ZADANIA'
    r2 = requests.get(url2, headers=headers)
    result2 = json.loads(r2.text)

    if request.method == 'POST':
        payload = {
                    "records": [
                        {
                            "fields": {
                                "ID_ZADANIA": request.form['ID_ZADANIA'],
                                "NAZWA": request.form['NAZWA'],
                                "TERMIN_WYKONANIA": request.form['TERMIN_WYKONANIA'],
                                "NOTATKI": request.form['NOTATKI'],
                                "ZREALIZOWANO": request.form['ZREALIZOWANO'],
                                "WYKONAWCA": request.form['WYKONAWCA'],
                            }
                        }
            ]
        }
        requests.post("https://api.airtable.com/v0/appQpPkjiYg5zo4kc/SZANSE", json=payload, headers=headers)
        return redirect(url_for('chances'))

    return render_template('addTask.html', **locals())

@app.route('/deleteUser', methods=["GET", "POST", "DELETE"])
def deleteUser():
    if not g.admin:
        return redirect(url_for('loginadmin'))
    url2 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/PRACOWNICY'
    r2 = requests.get(url2, headers=headers)
    result2 = json.loads(r2.text)

    if request.method == 'POST':
        table.delete(request.form['RECORD_ID'])

        return redirect(url_for('index'))

    return render_template('deleteUser.html', **locals())

@app.route('/deleteChance', methods=["GET", "POST", "DELETE"])
def deleteChance():
    if not g.user:
        return redirect(url_for('login'))
    url2 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/SZANSE'
    r2 = requests.get(url2, headers=headers)
    result2 = json.loads(r2.text)

    if request.method == 'POST':
        table.delete(request.form['RECORD_ID'])

        return redirect(url_for('chances'))

    return render_template('deleteChance.html', **locals())

@app.route('/deleteTask', methods=["GET", "POST", "DELETE"])
def deleteTask():
    if not g.user:
        return redirect(url_for('login'))
    url2 = 'https://api.airtable.com/v0/appQpPkjiYg5zo4kc/ZADANIA'
    r2 = requests.get(url2, headers=headers)
    result2 = json.loads(r2.text)

    if request.method == 'POST':
        table.delete(request.form['RECORD_ID'])

        return redirect(url_for('chances'))

    return render_template('deleteTask.html', **locals())


@app.before_request
def before_request():
    g.user = None
    g.admin = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
    if 'admin_id' in session:
         admin = [x for x in admins if x.id == session['admin_id']][0]
         g.admin = admin


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('admin_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/loginadmin', methods=['GET', 'POST'])
def loginadmin():
    if request.method == 'POST':
        session.pop('admin_id', None)
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        admin = [x for x in admins if x.username == username][0]
        if admin and admin.password == password:
            session['admin_id'] = admin.id
            return redirect(url_for('adminPanel'))

        return redirect(url_for('loginadmin'))

    return render_template('loginadmin.html')

@app.route('/logout')
def logout():
    if g.admin:
        session.pop('admin_id', None)
        return redirect(url_for('loginadmin'))

    if g.user:
        session.pop('user_id', None)
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
