from compiladoresListener import compiladoresListener
from compiladoresParser import compiladoresParser
from tabla_simbolos import TS, Variable, Funcion
import copy

class Escucha(compiladoresListener):
    def __init__(self):
        super().__init__()
        self.ts = TS.getInstance()
        self.permitir_declaracion = True
        self.error = False
        self.contextos_finales = []
        self.mensajes_error = []

    def enterBloque(self, ctx:compiladoresParser.BloqueContext):
        self.ts.addContexto()
        self.permitir_declaracion = True

    def exitBloque(self, ctx:compiladoresParser.BloqueContext):
        # Guarda una copia profunda del contexto antes de borrarlo
        self.contextos_finales.append(copy.deepcopy(self.ts.contextos[-1]))
        self.ts.delContexto()

    def exitDeclaracion(self, ctx:compiladoresParser.DeclaracionContext):
        tipo = ctx.tipo().getText()
        texto = ctx.getText()
        declaracion = texto.replace(tipo, '').replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]
        if not self.permitir_declaracion:
            for parte in partes:
                nombre = parte.split('=')[0].strip()
                self.mensajes_error.append(f"Error semántico: declarado '{nombre}' fuera del inicio del contexto.")
                self.error = True
            return
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=')]
                inicializado = True
            else:
                nombre = parte
                inicializado = False
            if self.ts.buscarSimboloContexto(nombre):
                self.mensajes_error.append(f"Error semántico: variable '{nombre}' ya declarada en este contexto.")
                self.error = True
            else:
                var = Variable(nombre, tipo)
                var.setInicializado(inicializado)
                self.ts.addSimbolo(var)

    def exitAsignacion(self, ctx:compiladoresParser.AsignacionContext):
        self.permitir_declaracion = False
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if not simbolo:
            self.mensajes_error.append(f"Error semántico: variable '{nombre}' no declarada.")
            self.error = True
        else:
            simbolo.setInicializado()

    def exitFactor(self, ctx:compiladoresParser.FactorContext):
        self.permitir_declaracion = False
        if ctx.ID():
            nombre = ctx.ID().getText()
            simbolo = self.ts.buscarSimbolo(nombre)
            if not simbolo:
                self.mensajes_error.append(f"Error semántico: variable '{nombre}' no declarada.")
                self.error = True
            else:
                simbolo.setUsado()
                if not simbolo.getInicializado():
                    self.mensajes_error.append(f"Error semántico: variable '{nombre}' usada sin inicializar.")
                    self.error = True

    def imprimir_tabla_simbolos(self):
        # Imprime el contexto global (el primero)
        print(f"Contexto Nº0")
        for nombre, simbolo in self.ts.contextos[0].simbolos.items():
            estado = []
            if simbolo.getInicializado():
                estado.append("inicializada")
            else:
                estado.append("declarada")
            if simbolo.getUsado():
                estado.append("usada")
            print(f"{simbolo.getTipoDato()} {nombre} : {', '.join(estado)}")
        print("~~~~~")
        # Imprime los contextos guardados al salir de cada bloque
        for i, contexto in enumerate(self.contextos_finales, start=1):
            print(f"Contexto Nº{i}")
            for nombre, simbolo in contexto.simbolos.items():
                estado = []
                if simbolo.getInicializado():
                    estado.append("inicializada")
                else:
                    estado.append("declarada")
                if simbolo.getUsado():
                    estado.append("usada")
                print(f"{simbolo.getTipoDato()} {nombre} : {', '.join(estado)}")
            print("~~~~~")

        # Imprime los errores al final
        if self.mensajes_error:
            print("ERRORES ENCONTRADOS:")
            for msg in self.mensajes_error:
                print(msg)

    def visitErrorNode(self, node):
        self.mensajes_error.append(f"Error sintáctico: {node.getText()}")
        self.error = True