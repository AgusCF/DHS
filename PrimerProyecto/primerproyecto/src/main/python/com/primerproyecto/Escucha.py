from compiladoresListener import compiladoresListener
from compiladoresParser import compiladoresParser
from tabla_simbolos import TS, Variable, Funcion

class Escucha(compiladoresListener):
    def __init__(self):
        super().__init__()
        self.ts = TS.getInstance()
        self.permitir_declaracion = True
        self.error = False

    def enterBloque(self, ctx:compiladoresParser.BloqueContext):
        self.ts.addContexto()
        self.permitir_declaracion = True

    def exitBloque(self, ctx:compiladoresParser.BloqueContext):
        if not self.error:
            self.imprimir_tabla_simbolos()
        self.ts.delContexto()

    def exitDeclaracion(self, ctx:compiladoresParser.DeclaracionContext):
        if not self.permitir_declaracion:
            print("Error semántico: declaración fuera del inicio del contexto.")
            self.error = True
            return
        tipo = ctx.tipo().getText()
        texto = ctx.getText()
        declaracion = texto.replace(tipo, '').replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=')]
                inicializado = True
            else:
                nombre = parte
                inicializado = False
            if self.ts.buscarSimboloContexto(nombre):
                print(f"Error semántico: variable '{nombre}' ya declarada en este contexto.")
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
            print(f"Error semántico: variable '{nombre}' no declarada.")
            self.error = True
        else:
            # Aquí deberías comparar tipos si tienes acceso al tipo de la expresión derecha
            simbolo.setInicializado()

    def exitFactor(self, ctx:compiladoresParser.FactorContext):
        if ctx.ID():
            nombre = ctx.ID().getText()
            simbolo = self.ts.buscarSimbolo(nombre)
            if not simbolo:
                print(f"Error semántico: variable '{nombre}' no declarada.")
                self.error = True
            else:
                simbolo.setUsado()
                if not simbolo.getInicializado():
                    print(f"Error semántico: variable '{nombre}' usada sin inicializar.")
                    self.error = True

    def imprimir_tabla_simbolos(self):
        for i, contexto in enumerate(self.ts.contextos):
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

    def visitErrorNode(self, node):
        print(f"Error sintáctico: {node.getText()}")
        self.error = True