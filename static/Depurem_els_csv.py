# import csv


# def afegir_moviments():
#     # Obrim el fitxer CSV en mode lectura
#     with open("static/moviments_creats_automaticament_B.csv", mode="r", encoding="UTF-8") as csv_file:
#         csv_reader = csv.reader(csv_file)
#         data = list(csv_reader)

#     # Modifiquem les dades que volem actualitzar (tercera columna)
#     for linia in data:
#         if linia[2] == "0":
#             linia[2] = "00"
#         elif linia[2] == "1":
#             linia[2] = "01"
#         elif linia[2] == "2":
#             linia[2] = "02"
#         elif linia[2] == "3":
#             linia[2] = "03"
#         elif linia[2] == "4":
#             linia[2] = "04"
#         elif linia[2] == "5":
#             linia[2] = "05"
#         elif linia[2] == "6":
#             linia[2] = "06"
#         elif linia[2] == "7":
#             linia[2] = "07"
#         elif linia[3] == "0":
#             linia[3] = "00"
#         elif linia[3] == "1":
#             linia[3] = "01"
#         elif linia[3] == "2":
#             linia[3] = "02"
#         elif linia[3] == "3":
#             linia[3] = "03"
#         elif linia[3] == "4":
#             linia[3] = "04"
#         elif linia[3] == "5":
#             linia[3] = "05"
#         elif linia[3] == "6":
#             linia[3] = "06"
#         elif linia[3] == "7":
#             linia[3] = "07"

#     # Obrim el fitxer CSV en mode escriptura i escrivim les dades actualitzades
#     with open(
#         "static/moviments_creats_automaticamentB.csv", mode="a", encoding="UTF-8", newline=""
#     ) as csv_file:
#         csv_writer = csv.writer(csv_file)
#         csv_writer.writerows(data)

#     return None


# # afegir_moviments()


# def afegir_moviments():
#     fitxer = open("static/moviments.csv", mode="r", encoding="UTF-8")
#     linies = fitxer.readlines()
#     liniesPeo = []
#     for linia in linies:
#         liniaLlista = linia.split(",")
#         if liniaLlista[1] == "B":
#             liniesPeo.append(linia)
#     fitxerNet = open("static/moviments_P_B.csv", mode="w", encoding="UTF-8")
#     fitxerNet.writelines(liniesPeo)
#     return None

# afegir_moviments()


# def crear_moviments():
#     numero = [
#         "00",
#         "01",
#         "02",
#         "03",
#         "04",
#         "05",
#         "06",
#         "07",
#         "10",
#         "11",
#         "12",
#         "13",
#         "14",
#         "15",
#         "16",
#         "17",
#         "20",
#         "21",
#         "22",
#         "23",
#         "24",
#         "25",
#         "26",
#         "27",
#         "30",
#         "31",
#         "32",
#         "33",
#         "34",
#         "35",
#         "36",
#         "37",
#         "40",
#         "41",
#         "42",
#         "43",
#         "44",
#         "45",
#         "46",
#         "47",
#         "50",
#         "51",
#         "52",
#         "53",
#         "54",
#         "55",
#         "56",
#         "57",
#         "60",
#         "61",
#         "62",
#         "63",
#         "64",
#         "65",
#         "66",
#         "67",
#         "70",
#         "71",
#         "72",
#         "73",
#         "74",
#         "75",
#         "76",
#         "77",
#     ]
#     origen = rnd.choice(numero)
#     desti = rnd.choice(numero)
#     # print(moviment(origen, desti))
#     # print(origen,desti)
#     if moviment(origen, desti) == False:
#         fitxer = open(
#             "static/moviments_creats_automaticament_A-B.csv", mode="a", encoding="UTF-8"
#         )
#         # print(origen, desti)
#         fitxa = "A"
#         color = "B"
#         valor = "3"
#         fitxer.writelines(fitxa, color, origen, desti, valor)


# # crear_moviments()

# while True:
#     crear_moviments()