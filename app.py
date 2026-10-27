# -*- coding: utf-8 -*-
# Sistema de Gestion de Solicitudes Academicas
# Version 1.0 - prototipo

import json
import os
from datetime import datetime

ARCHIVO = "datos.json"


class Sistema:

    def __init__(self):
        self.lst = []      # lista de solicitudes
        self.cont = 0      # contador de ids
        self.resp = [
            {"cod": "R1", "nom": "Ana Gomez", "area": "Alumnos"},
            {"cod": "R2", "nom": "Luis Perez", "area": "Academica"},
            {"cod": "R3", "nom": "Marta Diaz", "area": "Tesoreria"},
        ]
        self.cargar()

    def cargar(self):
        try:
            if os.path.exists(ARCHIVO):
                f = open(ARCHIVO, "r", encoding="utf-8")
                d = json.load(f)
                f.close()
                self.lst = d["solicitudes"]
                self.cont = d["contador"]
        except:
            self.lst = []
            self.cont = 0

    # registra una solicitud nueva
    def registrar(self, nom, leg, mail, tipo, desc, prio):
        # validaciones
        if nom == None or nom.strip() == "":
            print("Error: el nombre es obligatorio")
            return -1
        if not leg.isdigit():
            print("Error: el legajo debe ser numerico")
            return -1
        if not "@" in mail or not "." in mail:
            print("Error: el email no es valido")
            return -1
        if tipo != "1" and tipo != "2" and tipo != "3" and tipo != "4":
            print("Error: tipo de solicitud invalido")
            return -1
        if desc.strip() == "":
            print("Error: la descripcion es obligatoria")
            return -1
        if prio != "alta" and prio != "media" and prio != "baja":
            print("Error: la prioridad debe ser alta, media o baja")
            return -1

        # convertir el tipo
        if tipo == "1":
            t = "CERTIFICADO"
        elif tipo == "2":
            t = "EQUIVALENCIA"
        elif tipo == "3":
            t = "CAMBIO_COMISION"
        else:
            t = "RECLAMO_NOTA"

        self.cont = self.cont + 1
        x = {}
        x["id"] = self.cont
        x["nom"] = nom.strip()
        x["leg"] = leg
        x["mail"] = mail
        x["tipo"] = t
        x["desc"] = desc.strip()
        x["prio"] = prio
        x["est"] = "P"
        x["resp"] = None
        x["fecha"] = datetime.now().strftime("%Y-%m-%d")
        self.lst.append(x)

        # guardar
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"contador": self.cont, "solicitudes": self.lst}, f, indent=2, ensure_ascii=False)
        f.close()

        print("Solicitud registrada con ID " + str(self.cont))
        return self.cont

    def cambiar_estado(self, id, op):
        s = None
        for i in range(len(self.lst)):
            if self.lst[i]["id"] == id:
                s = self.lst[i]
        if s == None:
            print("Error: no existe la solicitud " + str(id))
            return False

        if op == "1":
            n = "E"
        elif op == "2":
            n = "R"
        elif op == "3":
            n = "X"
        else:
            print("Error: opcion de estado invalida")
            return False

        # reglas de transicion
        if s["est"] == "P":
            if n == "E":
                if s["resp"] == None:
                    print("Error: la solicitud debe tener responsable para pasar a EN PROCESO")
                    return False
            elif n == "R":
                print("Error: no se puede pasar de PENDIENTE a RESUELTA")
                return False
        elif s["est"] == "E":
            if n == "E":
                print("Error: la solicitud ya esta EN PROCESO")
                return False
        else:
            print("Error: la solicitud esta cerrada y no puede modificarse")
            return False

        s["est"] = n

        # guardar
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"contador": self.cont, "solicitudes": self.lst}, f, indent=2, ensure_ascii=False)
        f.close()

        if n == "E":
            e = "EN PROCESO"
        elif n == "R":
            e = "RESUELTA"
        else:
            e = "RECHAZADA"
        print("Solicitud " + str(id) + " actualizada a " + e)
        return True

    def asignar(self, id, cod):
        s = None
        for x in self.lst:
            if x["id"] == id:
                s = x
        if s == None:
            print("Error: no existe la solicitud " + str(id))
            return False
        if s["est"] == "R" or s["est"] == "X":
            print("Error: la solicitud esta cerrada y no puede modificarse")
            return False
        r = None
        for x in self.resp:
            if x["cod"] == cod.upper():
                r = x
        if r == None:
            print("Error: no existe el responsable " + cod)
            return False
        s["resp"] = r["cod"]

        # guardar
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"contador": self.cont, "solicitudes": self.lst}, f, indent=2, ensure_ascii=False)
        f.close()

        print("Responsable " + r["nom"] + " (" + r["area"] + ") asignado a la solicitud " + str(id))
        return True

    def buscar(self, op, val):
        res = []
        if op == "1":
            # por estado
            if val == "1":
                e = "P"
            elif val == "2":
                e = "E"
            elif val == "3":
                e = "R"
            elif val == "4":
                e = "X"
            else:
                print("Error: estado invalido")
                return
            for x in self.lst:
                if x["est"] == e:
                    res.append(x)
        elif op == "2":
            # por tipo
            if val == "1":
                t = "CERTIFICADO"
            elif val == "2":
                t = "EQUIVALENCIA"
            elif val == "3":
                t = "CAMBIO_COMISION"
            elif val == "4":
                t = "RECLAMO_NOTA"
            else:
                print("Error: tipo de solicitud invalido")
                return
            for x in self.lst:
                if x["tipo"] == t:
                    res.append(x)
        elif op == "3":
            # por legajo
            for x in self.lst:
                if x["leg"] == val:
                    res.append(x)
        else:
            print("Error: criterio invalido")
            return

        if len(res) == 0:
            print("No se encontraron solicitudes")
        else:
            for x in res:
                if x["est"] == "P":
                    e = "PENDIENTE"
                elif x["est"] == "E":
                    e = "EN PROCESO"
                elif x["est"] == "R":
                    e = "RESUELTA"
                else:
                    e = "RECHAZADA"
                rn = "sin asignar"
                for r in self.resp:
                    if r["cod"] == x["resp"]:
                        rn = r["nom"]
                print("#" + str(x["id"]) + " [" + x["tipo"] + "] " + x["nom"] + " (legajo " + x["leg"] + ") - prioridad " + x["prio"] + " - " + e + " - responsable: " + rn)

    def reporte(self):
        print("==== REPORTE DE SOLICITUDES ====")
        print("Total: " + str(len(self.lst)))
        p = 0
        en = 0
        r = 0
        x = 0
        for s in self.lst:
            if s["est"] == "P":
                p = p + 1
            elif s["est"] == "E":
                en = en + 1
            elif s["est"] == "R":
                r = r + 1
            else:
                x = x + 1
        print("Por estado:")
        print("  PENDIENTE: " + str(p))
        print("  EN PROCESO: " + str(en))
        print("  RESUELTA: " + str(r))
        print("  RECHAZADA: " + str(x))
        c1 = 0
        c2 = 0
        c3 = 0
        c4 = 0
        for s in self.lst:
            if s["tipo"] == "CERTIFICADO":
                c1 += 1
            if s["tipo"] == "EQUIVALENCIA":
                c2 += 1
            if s["tipo"] == "CAMBIO_COMISION":
                c3 += 1
            if s["tipo"] == "RECLAMO_NOTA":
                c4 += 1
        print("Por tipo:")
        print("  CERTIFICADO: " + str(c1))
        print("  EQUIVALENCIA: " + str(c2))
        print("  CAMBIO_COMISION: " + str(c3))
        print("  RECLAMO_NOTA: " + str(c4))
        print("Pendientes de prioridad alta:")
        hay = False
        for s in self.lst:
            if s["est"] == "P" and s["prio"] == "alta":
                hay = True
                rn = "sin asignar"
                for rr in self.resp:
                    if rr["cod"] == s["resp"]:
                        rn = rr["nom"]
                print("  #" + str(s["id"]) + " [" + s["tipo"] + "] " + s["nom"] + " (legajo " + s["leg"] + ") - prioridad " + s["prio"] + " - PENDIENTE - responsable: " + rn)
        if not hay:
            print("  (ninguna)")
        print("================================")

    # def exportar_csv(self):
    #     f = open("solicitudes.csv", "w")
    #     for s in self.lst:
    #         f.write(str(s["id"]) + ";" + s["nom"] + "\n")
    #     f.close()

    def calcular_prioridad(self, tipo):
        # TODO: ver si se usa
        if tipo == "RECLAMO_NOTA":
            return "alta"
        return "media"


def main():
    s = Sistema()
    while True:
        print("")
        print("=== GESTION DE SOLICITUDES ACADEMICAS ===")
        print("1. Registrar solicitud")
        print("2. Cambiar estado")
        print("3. Asignar responsable")
        print("4. Buscar solicitudes")
        print("5. Reporte")
        print("0. Salir")
        op = input("Opcion: ")
        try:
            if op == "1":
                nom = input("Nombre del estudiante: ")
                leg = input("Legajo: ")
                mail = input("Email: ")
                print("Tipos: 1-Certificado 2-Equivalencia 3-Cambio de comision 4-Reclamo de nota")
                tipo = input("Tipo: ")
                desc = input("Descripcion: ")
                prio = input("Prioridad (alta/media/baja): ")
                s.registrar(nom, leg, mail, tipo, desc, prio)
            elif op == "2":
                id = int(input("ID de la solicitud: "))
                print("Estados: 1-En proceso 2-Resuelta 3-Rechazada")
                e = input("Nuevo estado: ")
                s.cambiar_estado(id, e)
            elif op == "3":
                id = int(input("ID de la solicitud: "))
                for r in s.resp:
                    print("  " + r["cod"] + " - " + r["nom"] + " (" + r["area"] + ")")
                c = input("Codigo de responsable: ")
                s.asignar(id, c)
            elif op == "4":
                print("Criterios: 1-Estado 2-Tipo 3-Legajo")
                c = input("Criterio: ")
                v = input("Valor: ")
                s.buscar(c, v)
            elif op == "5":
                s.reporte()
            elif op == "0":
                print("Hasta luego")
                break
            else:
                print("Opcion invalida")
        except:
            print("Ocurrio un error")


if __name__ == "__main__":
    main()
