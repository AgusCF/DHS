# tabla_simbolos.py

class ID:
    def __init__(self, nombre, tipoDato):
        self.nombre = nombre
        self.tipoDato = tipoDato
        self.inicializado = False
        self.usado = False

    def getNombre(self):
        return self.nombre

    def getTipoDato(self):
        return self.tipoDato

    def setInicializado(self, val=True):
        self.inicializado = val

    def getInicializado(self):
        return self.inicializado

    def setUsado(self):
        self.usado = True

    def getUsado(self):
        return self.usado

#----------------------------------------
class Variable(ID):
    def __init__(self, nombre, tipoDato):
        super().__init__(nombre, tipoDato)

class Funcion(ID):
    def __init__(self, nombre, tipoDato, args=None):
        super().__init__(nombre, tipoDato)
        self.args = args if args else []

    def getListaArgs(self):
        return self.args

#----------------------------------------
class Contexto:
    def __init__(self):
        self.simbolos = {}

    def addSimbolo(self, id):
        self.simbolos[id.getNombre()] = id

    def buscarSimbolo(self, nombre):
        return self.simbolos.get(nombre, None)

#----------------------------------------
class TS:
    _instancia = None

    def __init__(self):
        self.contextos = [Contexto()]  # Comienza con un contexto global

    @staticmethod
    def getInstance():
        if TS._instancia is None:
            TS._instancia = TS()
        return TS._instancia

    def addContexto(self):
        self.contextos.append(Contexto())

    def delContexto(self):
        if len(self.contextos) > 1:
            self.contextos.pop()

    def addSimbolo(self, id):
        self.contextos[-1].addSimbolo(id)

    def buscarSimbolo(self, nombre):
        # Busca desde el contexto más interno hacia afuera
        for contexto in reversed(self.contextos):
            simbolo = contexto.buscarSimbolo(nombre)
            if simbolo:
                return simbolo
        return None

    def buscarSimboloContexto(self, nombre):
        # Solo busca en el contexto actual
        return self.contextos[-1].buscarSimbolo(nombre)