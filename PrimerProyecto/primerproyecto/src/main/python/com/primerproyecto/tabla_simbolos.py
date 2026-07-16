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
        self.nivel = 0

    def addSimbolo(self, id):
        self.simbolos[id.getNombre()] = id

    def addFuncion(self, funcion):
        self.simbolos[funcion.getNombre()] = funcion

    def buscarSimbolo(self, nombre):
        return self.simbolos.get(nombre, None)

#----------------------------------------
class TS:
    _instancia = None

    def __init__(self):
        self.contextos = []
        self.historialCTX = []
        self.addContexto()

    @staticmethod
    def getInstance():
        if TS._instancia is None:
            TS._instancia = TS()
        return TS._instancia

    def addContexto(self):
        nuevo = Contexto()
        nuevo.nivel = len(self.contextos)
        self.contextos.append(nuevo)
        self.historialCTX.append(nuevo)

    def delContexto(self):
        if len(self.contextos) > 1:
            self.contextos.pop()

    def addSimbolo(self, id):
        self.contextos[-1].addSimbolo(id)

    def addFuncion(self, funcion):
        self.contextos[-1].addFuncion(funcion)

    def buscarFuncion(self, nombre):
        for contexto in reversed(self.contextos):
            simbolo = contexto.buscarSimbolo(nombre)
            if simbolo and isinstance(simbolo, Funcion):
                return simbolo
        return None

    def buscarSimbolo(self, nombre):
        for contexto in reversed(self.contextos):
            simbolo = contexto.buscarSimbolo(nombre)
            if simbolo:
                return simbolo
        return None

    def buscarSimboloContexto(self, nombre):
        return self.contextos[-1].buscarSimbolo(nombre)

    def check_assignment_compatibility(self, dest_type, source_text):
        if source_text is None:
            return False, "valor desconocido"

        txt = source_text.strip()
        is_literal = txt.replace('.', '', 1).isdigit()

        if is_literal:
            if '.' in txt:
                if dest_type in ('float', 'double'):
                    return True, None
                else:
                    return False, f"Tipos incompatibles en asignacion ({dest_type} = float literal)"
            else:
                if dest_type in ('int', 'float', 'double'):
                    return True, None
                else:
                    return False, f"Tipos incompatibles en asignacion ({dest_type} = int literal)"

        simbolo = self.buscarSimbolo(txt)
        if simbolo is None:
            return False, f"variable '{txt}' no declarada"
        tipo_origen = simbolo.getTipoDato()
        if tipo_origen == dest_type:
            return True, None
        return False, f"Tipos incompatibles en asignacion ({dest_type} = {tipo_origen})"

    def imprimirTS(self, f):
        if not self.historialCTX:
            f.write("Tabla de simbolos vacia.\n")
            return

        for idx, contexto in enumerate(self.historialCTX):
            prefijo = '    ' * contexto.nivel
            f.write(f"{prefijo}--- Contexto #{idx} (nivel {contexto.nivel}) ---\n")

            simbolos = contexto.simbolos
            if not simbolos:
                f.write(f"{prefijo}(vacio)\n")
                continue

            for nombre, simbolo in simbolos.items():
                tipo = simbolo.getTipoDato()
                inicializado = simbolo.getInicializado()
                usado = simbolo.getUsado()

                if isinstance(simbolo, Funcion):
                    args = simbolo.getListaArgs()
                    if args:
                        args_str = ', '.join([f"{t.name}" for t in args])
                    else:
                        args_str = "void"
                    f.write(f"{prefijo}funcion {tipo.name} {nombre}({args_str}) - {'definida' if inicializado else 'prototipada'}, {'usada' if usado else 'no usada'}\n")
                else:
                    estado = []
                    if inicializado:
                        estado.append("inicializada")
                    else:
                        estado.append("declarada")
                    if usado:
                        estado.append("usada")
                    f.write(f"{prefijo}{tipo.name} {nombre} : {', '.join(estado)}\n")
