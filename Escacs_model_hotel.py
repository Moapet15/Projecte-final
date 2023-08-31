from matplotlib.backend_bases import FigureCanvasBase
import mysql.connector
from flask import Flask, Response, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import mpld3
from jinja2 import Template
import random as rnd
import time as t


def connectarBD():
    bd = mysql.connector.connect(
        host="Localhost", user="root", passwd="", database="escacs"
    )
    return bd


def initBD():
    bd = connectarBD()
    cursor = bd.cursor()
    query = "create schema if not exists escacs;\
            use escacs;\
            create table if not exists usuaris (\
            id int primary key auto_increment,\
            name varchar(50) not null,\
            email varchar(50) not null,\
            password varchar(50) not null\
            );\
            create table if not exists partides (\
                id int primary key auto_increment,\
                nº_Victories int not null,\
                nº_Derrotes int not null,\
                foreign key (id) references usuaris(id)\
            );"
    cursor.execute(query)
    bd.close()
    return


def augmentar_victoria(user):
    bd = connectarBD()
    cursor = bd.cursor()
    query = "insert into (nº_Victories) value (%s)"
    val = "1"
    cursor.execute(query, val)
    n = cursor.rowcount
    bd.commit()
    bd.close()
    return n


def crear_jugador(player, mail, password):
    bd = connectarBD()
    cursor = bd.cursor()
    query = "insert into usuaris (name,email,password) VALUE (%s,%s,%s)"
    val = (f"{player}", f"{mail}", f"{password}")
    cursor.execute(query, val)
    query = "insert into partides (nº_Victories,nº_Derrotes) VALUE (%s,%s)"
    val = ("0", "0")
    cursor.execute(query, val)
    n = cursor.rowcount
    bd.commit()
    bd.close()
    return n


def checkUser(user, password):
    bd = connectarBD()
    cursor = bd.cursor()
    query = f"""SELECT id,name,email,password FROM usuaris WHERE name=%s\
        AND password=%s"""

    params = (user, password)
    cursor.execute(query, params)
    userData = cursor.fetchall()
    bd.close()
    if userData == []:
        return False
    else:
        return userData[0]


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    initBD()
    return render_template("login.html")


@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/results", methods=("GET", "POST"))
def results():
    if request.method == "POST":
        formData = request.form
        user = formData["user"]
        password = formData["password"]
        userData = checkUser(user, password)
        if userData == False:
            return render_template("results.html", login=False)
        else:
            return render_template("results.html", login=True, userData=userData)


@app.route("/newUser", methods=("GET", "POST"))
def newUser():
    if request.method == "POST":
        formData = request.form
        # print(formData)
        user = formData["user"]
        email = formData["email"]
        password = formData["password"]
        userData = crear_jugador(user, email, password)
        if userData == True:
            return render_template("home.html")
        else:
            return render_template("home.html")


@app.route("/mostra_taulell", methods=["GET", "POST"])
def mostra_taulell():
    if request.method == "POST":
        origen = request.form["origen"]
        desti = request.form["desti"]
        # print(origen, desti)
        # print(type(origen))
        # print(taulell)
        origen = int(origen)
        desti = int(desti)
        Travis()
        if moviment(origen, desti) == True:
            print("El moviment s'ha completat correctament.")
            # taulell = taulell  # Obté el taulell actualitzat
            # print(taulell)
            missatge = "El moviment s'ha completat correctament."
            executar_moviment()
            borrar_contingut_CSV()
            if comprovar_vicotria() == False:
                print(comprovar_vicotria())
                return render_template("taulell.html", taulell=taulell, missatge=missatge)
            elif comprovar_vicotria() == "Guanyen les negres":
                return render_template("home.html")
            elif comprovar_vicotria() == "Guanyen les blanques":
                return render_template("home.html")
        else:
            missatge = "No s'ha pogut realitzar el moviment."
            return render_template("taulell.html", taulell=taulell, missatge=missatge)
    else:
        missatge = "La partida es pot iniciar"
        return render_template("taulell.html", taulell=taulell, missatge=missatge)


# Comencem la zona de constants
taulell = [
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
    [{}, {}, {}, {}, {}, {}, {}, {}],
]

cementiri_Blanc = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
cementiri_Negre = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]


def enviar_cementiri_Blanc(fitxa):
    for casella in enumerate(cementiri_Blanc):
        casella["color"] = "B"
        casella["fitxa"] = fitxa


def enviar_cementiri_Negre(fitxa):
    for casella in enumerate(cementiri_Negre):
        casella["color"] = "N"
        casella["fitxa"] = fitxa


for posicio_y_inicial, caselles_x in enumerate(taulell):
    for posicio_x_inicial, casella in enumerate(caselles_x):
        casella["posicio"] = (posicio_y_inicial) * 10 + (posicio_x_inicial)
        casella["ocupada"] = False
        casella["color"] = ""
        casella["fitxa"] = ""
        if (posicio_y_inicial + posicio_x_inicial) % 2 == 0:
            casella["fons"] = "Blanc"
        else:
            casella["fons"] = "Negre"


def comprovar_recorregut_vertical(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial
):
    #  Calcular totes les caselles per les que passa
    if posicio_y_final > posicio_y_inicial:
        caselles = []
        posicio = posicio_y_inicial + 1
        # print("Identifiquem que la y final és més gran que la y inicial")
        while posicio < posicio_y_final:
            caselles.append(taulell[posicio][posicio_x_final])
            posicio = posicio + 1
        # print(caselles)
        # Comprovar que totes aquestes caselles son buides
        for casella in caselles:
            if casella["ocupada"] == True:
                # print(casella["ocupada"])
                return False
        return True
    elif posicio_y_final < posicio_y_inicial:
        caselles = []
        posicio = posicio_y_inicial - 1
        # print(posicio)
        while posicio > posicio_y_final:
            caselles.append(taulell[posicio][posicio_x_final])
            posicio = posicio - 1
        # print(caselles)
        # Comprovar que totes aquestes caselles son buides
        for casella in caselles:
            if casella["ocupada"] == True:
                # print(casella["ocupada"])
                return False
        return True


def comprovar_recorregut_horitzontal(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial
):
    #  Calcular totes les caselles per les que passa
    if posicio_x_final > posicio_x_inicial:
        caselles = []
        posicio = posicio_x_inicial + 1
        while posicio < posicio_x_final:
            caselles.append(taulell[posicio_y_final][posicio])
            posicio = posicio + 1
        # print(caselles)
        # Comprovar que totes aquestes caselles son buides
        for casella in caselles:
            if casella["ocupada"] == True:
                # print(casella["ocupada"])
                return False
        return True
    elif posicio_x_final < posicio_x_inicial:
        caselles = []
        posicio = posicio_x_inicial - 1
        while posicio > posicio_x_final:
            caselles.append(taulell[posicio_y_final][posicio])
            posicio = posicio - 1
        # print(caselles)
        # Comprovar que totes aquestes caselles son buides
        for casella in caselles:
            if casella["ocupada"] == True:
                # print(casella["ocupada"])
                return False
        return True


def comprovar_recorregut_en_diagonal(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial
):
    # Comprovació de moviment en diagonal d'esquerra a dreta i de dalt a baix (ambdós valors positius)
    if posicio_y_final > posicio_y_inicial and posicio_x_final > posicio_x_inicial:
        caselles = []
        posicio_amb_y = posicio_y_inicial + 1
        posicio_amb_x = posicio_x_inicial + 1
        while posicio_amb_y < posicio_y_final and posicio_amb_x < posicio_x_final:
            caselles.append(taulell[posicio_amb_y][posicio_amb_x])
            posicio_amb_y = posicio_amb_y + 1
            posicio_amb_x = posicio_amb_x + 1
            for casella in caselles:
                if casella["ocupada"] == True:
                    # print(casella["ocupada"])
                    return False
    # Comprovació de moviment en diagonal de dreta a esquerra i de dalt a baix
    elif posicio_y_final > posicio_y_inicial and posicio_x_final < posicio_x_inicial:
        caselles = []
        posicio_amb_y = posicio_y_inicial + 1
        posicio_amb_x = posicio_x_inicial - 1
        while posicio_amb_y < posicio_y_final and posicio_amb_x > posicio_x_final:
            caselles.append(taulell[posicio_amb_y][posicio_amb_x])
            posicio_amb_y = posicio_amb_y + 1
            posicio_amb_x = posicio_amb_x - 1
            for casella in caselles:
                if casella["ocupada"] == True:
                    # print(casella["ocupada"])
                    return False
    # Comprovació de moviment en diagonal de dreta a esquerra i de dalt a baix
    elif posicio_y_final < posicio_y_inicial and posicio_x_final < posicio_x_inicial:
        caselles = []
        posicio_amb_y = posicio_y_inicial - 1
        posicio_amb_x = posicio_x_inicial - 1
        while posicio_amb_y > posicio_y_final and posicio_amb_x > posicio_x_final:
            caselles.append(taulell[posicio_amb_y][posicio_amb_x])
            posicio_amb_y = posicio_amb_y - 1
            posicio_amb_x = posicio_amb_x - 1
            for casella in caselles:
                if casella["ocupada"] == True:
                    # print(casella["ocupada"])
                    return False
    # Comprovació de moviment en diagonal d'esquerra a dreta i de baix a dalt
    elif posicio_y_final < posicio_y_inicial and posicio_x_final > posicio_x_inicial:
        caselles = []
        posicio_amb_y = posicio_y_inicial - 1
        posicio_amb_x = posicio_x_inicial + 1
        while posicio_amb_y > posicio_y_final and posicio_amb_x < posicio_x_final:
            caselles.append(taulell[posicio_amb_y][posicio_amb_x])
            posicio_amb_y = posicio_amb_y - 1
            posicio_amb_x = posicio_amb_x + 1
            for casella in caselles:
                if casella["ocupada"] == True:
                    # print(casella["ocupada"])
                    return False
    else:
        return True


def plenar_casella(posicio_y_final, posicio_x_final, fitxa, color):
    # print("Aqui escrivim", posicio_y_final, posicio_x_final, fitxa, color)
    casella = taulell[posicio_y_final][posicio_x_final]
    casella["ocupada"] = True
    casella["color"] = color
    casella["fitxa"] = fitxa
    return True


def buidar_casella(posicio_y_inicial, posicio_x_inicial):
    # print("Aqui borrem", posicio_y_inicial, posicio_x_inicial)
    casella = taulell[posicio_y_inicial][posicio_x_inicial]
    casella["ocupada"] = False
    casella["color"] = ""
    casella["fitxa"] = ""
    return True


def moviment_casella(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    # print(
    #     posicio_y_final,
    #     posicio_x_final,
    #     posicio_y_inicial,
    #     posicio_x_inicial,
    #     fitxa,
    #     color,
    # )
    plenar_casella(posicio_y_final, posicio_x_final, fitxa, color)
    buidar_casella(posicio_y_inicial, posicio_x_inicial)
    return True


def moviment(origen, desti):
    # print("Cridem la funcio?")
    origen = int(origen)
    desti = int(desti)
    posicio_y_inicial = origen // 10
    posicio_x_inicial = origen % 10
    posicio_y_final = desti // 10
    posicio_x_final = desti % 10
    # print(taulell[posicio_y_inicial][posicio_x_inicial])
    # print(origen, desti)
    if (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "P"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "N"
    ):
        fitxa = "P"
        color = "N"
        # print(posicio_y_final,
        #     posicio_x_final,
        #     posicio_y_inicial,
        #     posicio_x_inicial,
        #     fitxa,
        #     color)
        if (
            moviment_peo_negre(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "C"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "N"
    ):
        fitxa = "C"
        color = "N"
        if (
            moviment_cavall_negre(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "T"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "N"
    ):
        fitxa = "T"
        color = "N"
        if (
            moviment_torre_negra(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "A"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "N"
    ):
        # print("Identifiquem que és un alfil?")
        fitxa = "A"
        color = "N"
        if (
            moviment_alfil_negre(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "Q"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "N"
    ):
        fitxa = "Q"
        color = "N"
        if (
            moviment_reina_negra(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "K"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "N"
    ):
        fitxa = "K"
        color = "N"
        if (
            moviment_rei_negre(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "P"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "B"
    ):
        fitxa = "P"
        color = "B"
        if (
            moviment_peo_blanc(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "C"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "B"
    ):
        fitxa = "C"
        color = "B"
        if (
            moviment_cavall_blanc(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "T"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "B"
    ):
        fitxa = "T"
        color = "B"
        if (
            moviment_torre_blanca(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "A"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "B"
    ):
        fitxa = "A"
        color = "B"
        if (
            moviment_alfil_blanc(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "Q"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "B"
    ):
        fitxa = "Q"
        color = "B"
        if (
            moviment_reina_blanca(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    elif (
        taulell[posicio_y_inicial][posicio_x_inicial]["fitxa"] == "K"
        and taulell[posicio_y_inicial][posicio_x_inicial]["color"] == "B"
    ):
        fitxa = "K"
        color = "B"
        if (
            moviment_rei_blanc(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            == True
        ):
            return True
    return False


def moviment_peo_negre(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    # print(posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial)
    if (
        posicio_y_final - posicio_y_inicial == 1
        and posicio_x_final == posicio_x_inicial
    ):
        if not taulell[posicio_y_final][posicio_x_final]["ocupada"]:
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            # print(taulell)
            return True
    elif (
        posicio_y_inicial == 1
        and posicio_y_final == posicio_y_inicial + 2
        and posicio_x_final == posicio_x_inicial
    ):
        if not taulell[posicio_y_final][posicio_x_final]["ocupada"]:
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True
    elif (
        posicio_y_final == posicio_y_inicial + 1
        and posicio_x_final == posicio_x_inicial + 1
        or posicio_y_final - posicio_y_inicial == 1
        and posicio_x_final == posicio_x_inicial - 1
    ):
        if (
            taulell[posicio_y_final][posicio_x_final]["ocupada"] == False
            or taulell[posicio_y_final][posicio_x_final]["color"] == "B"
        ):
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True

    return False


def moviment_peo_blanc(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    # print(posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial)
    if (
        posicio_y_final - posicio_y_inicial == -1
        and posicio_x_final == posicio_x_inicial
    ):
        if not taulell[posicio_y_final][posicio_x_final]["ocupada"]:
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            # print(taulell)
            return True
    elif (
        posicio_y_inicial == 6
        and posicio_y_final == posicio_y_inicial - 2
        and posicio_x_final == posicio_x_inicial
    ):
        if not taulell[posicio_y_final][posicio_x_final]["ocupada"]:
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True
    elif (
        posicio_y_final - posicio_y_inicial == -1
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or posicio_y_final - posicio_y_inicial == -1
        and abs(posicio_x_final - posicio_x_inicial) == -1
    ):
        if (
            taulell[posicio_y_final][posicio_x_final]["ocupada"] == True
            and taulell[posicio_y_final][posicio_x_final]["color"] == "N"
        ):
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True

    return False


def moviment_cavall_negre(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (
        abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == -2
        or abs(posicio_y_final - posicio_y_inicial) == -2
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == -2
        and abs(posicio_x_final - posicio_x_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_x_final - posicio_x_inicial) == -2
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "B"
        ):
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True

    return False


def moviment_cavall_blanc(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (
        abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == -2
        or abs(posicio_y_final - posicio_y_inicial) == -2
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == -2
        and abs(posicio_x_final - posicio_x_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_x_final - posicio_x_inicial) == -2
    ):
        # print("Arribem aqui?")
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "N"
        ):
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True

    return False


def moviment_torre_negra(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    # print(
    #     posicio_y_inicial,
    #     posicio_x_inicial,
    #     posicio_y_final,
    #     posicio_x_final,
    #     fitxa,
    #     color,
    # )
    # print(posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial)
    # Aqui ja definim que allà on enviem la torre hi ha d'haver una fitxa blanca o ha d'estar desocupada
    # print("Identifiquem que es la torre")
    if (
        # Moviments de torre de dalt a baix
        abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 3
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 4
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 5
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 6
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 7
        and abs(posicio_x_final - posicio_x_inicial) == 0
        # Moviments de torre de baix a dalt
        or abs(posicio_y_final + posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 2
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 3
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 4
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 5
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 6
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 7
        and abs(posicio_x_final + posicio_x_inicial) == 0
        # Moviments de torre d'esquerra a dreta
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 7
        # Moviments de torre de dreta a esquerra
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 7
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "B"
        ):
            if (
                posicio_y_final > posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
                or posicio_y_final < posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
            ):
                if (
                    comprovar_recorregut_vertical(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                # print("Movem la torre")
                return True
            elif (
                posicio_x_final > posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
                or posicio_x_final < posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
            ):
                if (
                    comprovar_recorregut_horitzontal(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                # print("Movem la torre")
                return True
    else:
        # print("No pot fer aquest moviment, la casella està ocupada!")
        pass


def moviment_torre_blanca(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    # print(
    #     posicio_y_inicial,
    #     posicio_x_inicial,
    #     posicio_y_final,
    #     posicio_x_final,
    #     fitxa,
    #     color,
    # )
    # print(posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial)
    # Aqui ja definim que allà on enviem la torre hi ha d'haver una fitxa blanca o ha d'estar desocupada
    # print("Identifiquem que es la torre")
    if (
        # Moviments de torre de dalt a baix
        abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 3
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 4
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 5
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 6
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 7
        and abs(posicio_x_final - posicio_x_inicial) == 0
        # Moviments de torre de baix a dalt
        or abs(posicio_y_final + posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 2
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 3
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 4
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 5
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 6
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 7
        and abs(posicio_x_final + posicio_x_inicial) == 0
        # Moviments de torre d'esquerra a dreta
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 7
        # Moviments de torre de dreta a esquerra
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 7
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "N"
        ):
            if (
                posicio_y_final > posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
                or posicio_y_final < posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
            ):
                if (
                    comprovar_recorregut_vertical(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                # print("Movem la torre")
                return True
            elif (
                posicio_x_final > posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
                or posicio_x_final < posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
            ):
                if (
                    comprovar_recorregut_horitzontal(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                # print("Movem la torre")
                return True
    else:
        # print("No pot fer aquest moviment, la casella està ocupada!")
        pass


def moviment_alfil_negre(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    # print("Després d'identificar entrem a la funció alfil negre")
    if (  ## E---->D   UP---->DOWN ##
        posicio_y_final - posicio_y_inicial == 1
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   UP---->DOWN ##
        or posicio_y_final - posicio_y_inicial == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_inicial - posicio_x_final == 7
        or posicio_y_inicial - posicio_y_final == 1
        ## E---->D   DOWN---->UP ##
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   DOWN---->DOWN ##
        or posicio_y_inicial - posicio_y_final == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_inicial - posicio_x_final == 7
    ) == True:
        if (
            taulell[posicio_y_final][posicio_x_final]["ocupada"] == False
            or taulell[posicio_y_final][posicio_x_final]["color"] == "B"
        ) == True:
            if (
                comprovar_recorregut_en_diagonal(
                    posicio_y_final,
                    posicio_x_final,
                    posicio_y_inicial,
                    posicio_x_inicial,
                )
            ) == False:
                return False
            else:
                # print("Comprovem que el moviment es pot fer")
                moviment_casella(
                    posicio_y_final,
                    posicio_x_final,
                    posicio_y_inicial,
                    posicio_x_inicial,
                    fitxa,
                    color,
                )
                return True
        else:
            return False
    else:
        return False


def moviment_alfil_blanc(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (  ## E---->D   UP---->DOWN ##
        posicio_y_final - posicio_y_inicial == 1
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   UP---->DOWN ##
        or posicio_y_final - posicio_y_inicial == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_inicial - posicio_x_final == 7
        ## E---->D   DOWN---->UP ##
        or posicio_y_inicial - posicio_y_final == 1
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   DOWN---->DOWN ##
        or posicio_y_inicial - posicio_y_final == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_inicial - posicio_x_final == 7
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "N"
        ):
            if (
                comprovar_recorregut_en_diagonal(
                    posicio_y_final,
                    posicio_x_final,
                    posicio_y_inicial,
                    posicio_x_inicial,
                )
                == False
            ):
                return False
            else:
                moviment_casella(
                    posicio_y_final,
                    posicio_x_final,
                    posicio_y_inicial,
                    posicio_x_inicial,
                    fitxa,
                    color,
                )
            return True


def moviment_reina_negra(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (  ## E---->D   UP---->DOWN ##
        posicio_y_final - posicio_y_inicial == 1
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   UP---->DOWN ##
        or posicio_y_final - posicio_y_inicial == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_inicial - posicio_x_final == 7
        or posicio_y_inicial - posicio_y_final == 1  ## E---->D   DOWN---->UP ##
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   DOWN---->DOWN ##
        or posicio_y_inicial - posicio_y_final == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_inicial - posicio_x_final == 7
        # Moviments de la reina de dalt a baix
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 3
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 4
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 5
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 6
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 7
        and abs(posicio_x_final - posicio_x_inicial) == 0
        # Moviments de la reina de baix a dalt
        or abs(posicio_y_final + posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 2
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 3
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 4
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 5
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 6
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 7
        and abs(posicio_x_final + posicio_x_inicial) == 0
        # Moviments de la reina d'esquerra a dreta
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 7
        # Moviments de la reina de dreta a esquerra
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 7
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "B"
        ):
            if (
                posicio_y_final > posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
                or posicio_y_final < posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
            ):
                if (
                    comprovar_recorregut_vertical(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                return True
            elif (
                posicio_x_final > posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
                or posicio_x_final < posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
            ):
                if (
                    comprovar_recorregut_horitzontal(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                # print("Movem la torre")
                return True
            elif posicio_y_inicial != posicio_y_final:
                if (
                    comprovar_recorregut_en_diagonal(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                    return True
    else:
        # print("No pot fer aquest moviment, la casella està ocupada!")
        pass


def moviment_reina_blanca(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (  ## E---->D   UP---->DOWN ##
        posicio_y_final - posicio_y_inicial == 1
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   UP---->DOWN ##
        or posicio_y_final - posicio_y_inicial == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_final - posicio_y_inicial == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_final - posicio_y_inicial == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_final - posicio_y_inicial == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_final - posicio_y_inicial == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_final - posicio_y_inicial == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_final - posicio_y_inicial == 7
        and posicio_x_inicial - posicio_x_final == 7
        ## E---->D   DOWN---->UP ##
        or posicio_y_inicial - posicio_y_final == 1
        and posicio_x_final - posicio_x_inicial == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_final - posicio_x_inicial == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_final - posicio_x_inicial == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_final - posicio_x_inicial == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_final - posicio_x_inicial == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_final - posicio_x_inicial == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_final - posicio_x_inicial == 7
        ## D---->E   DOWN---->DOWN ##
        or posicio_y_inicial - posicio_y_final == 1
        and posicio_x_inicial - posicio_x_final == 1
        or posicio_y_inicial - posicio_y_final == 2
        and posicio_x_inicial - posicio_x_final == 2
        or posicio_y_inicial - posicio_y_final == 3
        and posicio_x_inicial - posicio_x_final == 3
        or posicio_y_inicial - posicio_y_final == 4
        and posicio_x_inicial - posicio_x_final == 4
        or posicio_y_inicial - posicio_y_final == 5
        and posicio_x_inicial - posicio_x_final == 5
        or posicio_y_inicial - posicio_y_final == 6
        and posicio_x_inicial - posicio_x_final == 6
        or posicio_y_inicial - posicio_y_final == 7
        and posicio_x_inicial - posicio_x_final == 7
        # Moviments de la reina de dalt a baix
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 2
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 3
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 4
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 5
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 6
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 7
        and abs(posicio_x_final - posicio_x_inicial) == 0
        # Moviments de la reina de baix a dalt
        or abs(posicio_y_final + posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 2
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 3
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 4
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 5
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 6
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 7
        and abs(posicio_x_final + posicio_x_inicial) == 0
        # Moviments de la reina d'esquerra a dreta
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 7
        # Moviments de la reina de dreta a esquerra
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 2
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 3
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 4
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 5
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 6
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 7
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "N"
        ):
            if (
                posicio_y_final > posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
                or posicio_y_final < posicio_y_inicial
                and posicio_x_final == posicio_x_inicial
            ):
                if (
                    comprovar_recorregut_vertical(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                return True
            elif (
                posicio_x_final > posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
                or posicio_x_final < posicio_x_inicial
                and posicio_y_final == posicio_y_inicial
            ):
                if (
                    comprovar_recorregut_horitzontal(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    # print("Hem superat les comprovacións!")
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                # print("Movem la torre")
                return True
            elif posicio_y_inicial != posicio_y_final:
                if (
                    comprovar_recorregut_en_diagonal(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                    )
                    == False
                ):
                    return False
                else:
                    moviment_casella(
                        posicio_y_final,
                        posicio_x_final,
                        posicio_y_inicial,
                        posicio_x_inicial,
                        fitxa,
                        color,
                    )
                    return True
    else:
        # print("No pot fer aquest moviment, la casella està ocupada!")
        pass


def moviment_rei_negre(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (
        abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_y_final - posicio_y_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_y_final - posicio_y_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_y_final - posicio_y_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 1
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "B"
        ):
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True


def moviment_rei_blanc(
    posicio_y_final, posicio_x_final, posicio_y_inicial, posicio_x_inicial, fitxa, color
):
    if (
        abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_y_final - posicio_y_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_y_final - posicio_y_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == -1
        and abs(posicio_y_final - posicio_y_inicial) == -1
        or abs(posicio_y_final - posicio_y_inicial) == 1
        and abs(posicio_x_final - posicio_x_inicial) == 0
        or abs(posicio_y_final + posicio_y_inicial) == 1
        and abs(posicio_x_final + posicio_x_inicial) == 0
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final - posicio_x_inicial) == 1
        or abs(posicio_y_final - posicio_y_inicial) == 0
        and abs(posicio_x_final + posicio_x_inicial) == 1
    ):
        if (
            not taulell[posicio_y_final][posicio_x_final]["ocupada"]
            or taulell[posicio_y_final][posicio_x_final]["color"] == "N"
        ):
            moviment_casella(
                posicio_y_final,
                posicio_x_final,
                posicio_y_inicial,
                posicio_x_inicial,
                fitxa,
                color,
            )
            return True


# Fitxes Negres


plenar_casella(0, 0, "T", "N")
plenar_casella(0, 1, "C", "N")
plenar_casella(0, 2, "A", "N")
plenar_casella(0, 3, "Q", "N")
plenar_casella(0, 4, "K", "N")
plenar_casella(0, 5, "A", "N")
plenar_casella(0, 6, "C", "N")
plenar_casella(0, 7, "T", "N")

plenar_casella(1, 0, "P", "N")
plenar_casella(1, 1, "P", "N")
plenar_casella(1, 2, "P", "N")
plenar_casella(1, 3, "P", "N")
plenar_casella(1, 4, "P", "N")
plenar_casella(1, 5, "P", "N")
plenar_casella(1, 6, "P", "N")
plenar_casella(1, 7, "P", "N")

# Fitxes Blanques

plenar_casella(7, 0, "T", "B")
plenar_casella(7, 1, "C", "B")
plenar_casella(7, 2, "A", "B")
plenar_casella(7, 3, "Q", "B")
plenar_casella(7, 4, "K", "B")
plenar_casella(7, 5, "A", "B")
plenar_casella(7, 6, "C", "B")
plenar_casella(7, 7, "T", "B")

plenar_casella(6, 0, "P", "B")
plenar_casella(6, 1, "P", "B")
plenar_casella(6, 2, "P", "B")
plenar_casella(6, 3, "P", "B")
plenar_casella(6, 4, "P", "B")
plenar_casella(6, 5, "P", "B")
plenar_casella(6, 6, "P", "B")
plenar_casella(6, 7, "P", "B")

# print(taulell)


# def netejarCSV():
#     fitxer = open(
#         "static/moviments_creats_automaticament.csv", mode="r", encoding="UTF-8"
#     )
#     linies = fitxer.readlines()
#     linesNetes = list(set(linies))
#     fitxerNet = open(
#         "static/moviments_creats_automaticament.csv", mode="w", encoding="UTF-8"
#     )
#     fitxerNet.writelines(linesNetes)
#     return None

# while True:
#     moviment_IA()


# netejarCSV()
# extreureMovimentsTorre()

# Aquí comencem la zona de codi dedicada a la IA batejat amb el nom de Travis


def afegir_moviments(origen, pessa, color):
    fitxer = open(f"static/moviments_{pessa}_{color}.csv", mode="r", encoding="UTF-8")
    linies = fitxer.readlines()
    liniesPeo = []
    for linia in linies:
        liniaLlista = linia.split(",")
        if liniaLlista[2] == origen:
            liniesPeo.append(linia)
    fitxerNet = open("static/jugada.csv", mode="a", encoding="UTF-8")
    fitxerNet.writelines(liniesPeo)
    return None


def escriure_posicions(pessa, color, origen, desti, valor):
    fitxer = open("static/jugada.csv", mode="a", encoding="UTF-8")
    fitxer.writelines(f"{pessa},{color},{origen},{desti},{valor}\n")
    # print(linia)
    fitxer.close()
    return origen


def borrar_contingut_CSV():
    fitxer = open("static/jugada.csv", mode="w", encoding="UTF-8")
    fitxer.writelines("")
    fitxer.close()


def executar_moviment():
    fitxer = open("static/jugada.csv", mode="r", encoding="UTF-8")
    linies = fitxer.readlines()
    dadesB = []
    for contingut in linies:
        llistaLinia = contingut.split(",")
        if llistaLinia[1] == "B" and llistaLinia[3] != "NaN":
            dadesB.append(contingut)

    movimentRnd = rnd.choice(dadesB)
    llistaLinia = movimentRnd.split(",")
    origen = llistaLinia[2]
    desti = llistaLinia[3]

    if moviment(origen, desti) == True:
        print(origen, desti)
        print("Moviment vàlid. Fem moviment....")
        return True
    else:
        print("Moviment invàlid. Busquem un altre moviment...")
        print(origen, desti)
        return executar_moviment()


# executar_moviment()


def Travis():
    # Espai dedicat a l'analisi del terreny
    for posicio_y_inicial, caselles_x in enumerate(taulell):
        for posicio_x_inicial, casella in enumerate(caselles_x):
            casella["posicio"] = (posicio_y_inicial) * 10 + (posicio_x_inicial)
            origen = f"{posicio_y_inicial}{posicio_x_inicial}"
            if casella["ocupada"] == True:
                color = casella["color"]
                pessa = casella["fitxa"]
                if pessa == "P" and color == "N":
                    valor = "1"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    if (
                        taulell[posicio_y_inicial + 1][posicio_x_inicial]["ocupada"]
                        == False
                    ):
                        afegir_moviments(origen, pessa, color)
                elif pessa == "P" and color == "B":
                    valor = "1"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    if (
                        taulell[posicio_y_inicial - 1][posicio_x_inicial]["ocupada"]
                        == False
                    ):
                        afegir_moviments(origen, pessa, color)
                elif pessa == "T" and color == "N" or pessa == "T" and color == "B":
                    valor = "5"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    if (
                        posicio_y_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial + 1][posicio_x_inicial]["ocupada"]
                        == False
                        or posicio_y_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial - 1][posicio_x_inicial]["ocupada"]
                        == False
                        or posicio_x_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial][posicio_x_inicial + 1]["ocupada"]
                        == False
                        or posicio_x_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial][posicio_x_inicial - 1]["ocupada"]
                        == False
                    ):
                        afegir_moviments(origen, pessa, color)
                elif pessa == "C" and color == "N" or pessa == "C" and color == "B":
                    valor = "3"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    afegir_moviments(origen, pessa, color)
                elif pessa == "A" and color == "N" or pessa == "A" and color == "B":
                    valor = "3"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    if (
                        posicio_y_inicial + 1 < len(taulell)
                        and posicio_x_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial + 1][posicio_x_inicial + 1][
                            "ocupada"
                        ]
                        == False
                        or posicio_y_inicial - 1 < len(taulell)
                        and posicio_x_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial - 1][posicio_x_inicial - 1][
                            "ocupada"
                        ]
                        == False
                    ):
                        afegir_moviments(origen, pessa, color)
                elif pessa == "Q" and color == "N" or pessa == "Q" and color == "B":
                    valor = "9"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    if (
                        posicio_y_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial + 1][posicio_x_inicial]["ocupada"]
                        == False
                        or posicio_y_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial - 1][posicio_x_inicial]["ocupada"]
                        == False
                        or posicio_x_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial][posicio_x_inicial + 1]["ocupada"]
                        == False
                        or posicio_x_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial][posicio_x_inicial - 1]["ocupada"]
                        == False
                        or posicio_y_inicial + 1 < len(taulell)
                        and posicio_x_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial + 1][posicio_x_inicial + 1][
                            "ocupada"
                        ]
                        == False
                        or posicio_y_inicial - 1 < len(taulell)
                        and posicio_x_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial - 1][posicio_x_inicial - 1][
                            "ocupada"
                        ]
                        == False
                    ):
                        afegir_moviments(origen, pessa, color)
                elif pessa == "K" and color == "N" or pessa == "K" and color == "B":
                    valor = "50"
                    desti = "NaN"
                    escriure_posicions(pessa, color, origen, desti, valor)
                    if (
                        posicio_y_inicial + 1 < len(taulell)
                        and taulell[posicio_y_inicial + 1][posicio_x_inicial]["ocupada"]
                        == False
                        and taulell[posicio_y_inicial][posicio_x_inicial]["color"]
                        == "N"
                        or posicio_y_inicial - 1 < len(taulell)
                        and taulell[posicio_y_inicial - 1][posicio_x_inicial]["ocupada"]
                        == False
                        and taulell[posicio_y_inicial][posicio_x_inicial]["color"]
                        == "B"
                    ):
                        afegir_moviments(origen, pessa, color)
    # executar_moviment()
    # print("Podem fer el moviment")
    # borrar_contingut_CSV()
    # executar_moviment()
    # Fi de l'espai dedicat a l'analisi del terreny
    # Inici de l'espai dedicat a la presa de decissións
    # print(taulell[1][0])


# Travis()
# borrar_contingut_CSV()


def comprovar_vicotria():
    reiN = []
    reiB = []
    for fila in taulell:
        for casella in fila:
            if casella["fitxa"] == "K" and casella["color"] == "N":
                reiN.append(casella)
            elif casella["fitxa"] == "K" and casella["color"] == "B":
                reiB.append(casella)
    if len(reiN) == 1 and len(reiB) == 1:
        return False
        # print("Ambdós reis són vius.")
    elif len(reiN) == 1 and len(reiB) == 0:
        return "Guanyen les negres"
        # print("El rei blanc es mort")
    elif len(reiB) == 1 and len(reiN) == 0:
        # print("El rei negre es mort")
        return "GUanyen les blanques"


# comprovar_vicotria()
# Configuración y arranque de la aplicación web
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(host="localhost", port=5000, debug=True)

