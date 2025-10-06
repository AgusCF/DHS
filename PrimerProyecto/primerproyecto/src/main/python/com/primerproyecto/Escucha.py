    
from compiladoresListener import compiladoresListener
from compiladoresParser import compiladoresParser
from tabla_simbolos import TS, Variable, Funcion

class Escucha(compiladoresListener):
    def __init__(self):
        super().__init__()
        self.ts = TS.getInstance()

    # --- Manejo de bloques (contextos) ---
    def enterBloque(self, ctx:compiladoresParser.BloqueContext):
        self.ts.addContexto()
        print(">> Nuevo contexto (bloque) creado.")

    def exitBloque(self, ctx:compiladoresParser.BloqueContext):
        self.ts.delContexto()
        print("<< Contexto (bloque) eliminado.")

    # --- Declaración de variables ---
    def exitDeclaracion(self, ctx:compiladoresParser.DeclaracionContext):
        tipo = ctx.tipo().getText()
        # listavar puede ser recursiva, aquí simplificamos suponiendo que es una lista separada por comas
        texto = ctx.getText()
        # Extraer variables y asignaciones
        # Ejemplo: int a=1, b, c=2;
        declaracion = texto.replace(tipo, '').replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=')]
                inicializado = True
            else:
                nombre = parte
                inicializado = False
            # Verifica si ya existe en este contexto
            if self.ts.buscarSimboloContexto(nombre):
                print(f"Error: variable '{nombre}' ya declarada en este contexto.")
            else:
                var = Variable(nombre, tipo)
                var.setInicializado(inicializado)
                self.ts.addSimbolo(var)
                print(f"Declarada variable '{nombre}' tipo {tipo}, inicializada: {inicializado}")

    # --- Asignación de variables ---
    def exitAsignacion(self, ctx:compiladoresParser.AsignacionContext):
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if simbolo:
            simbolo.setInicializado()
            simbolo.setUsado()
            print(f"Asignación: variable '{nombre}' marcada como usada e inicializada.")
        else:
            print(f"Error: variable '{nombre}' no definida.")

    # --- Uso de variables en expresiones ---
    def exitFactor(self, ctx:compiladoresParser.FactorContext):
        if ctx.ID():
            nombre = ctx.ID().getText()
            simbolo = self.ts.buscarSimbolo(nombre)
            if simbolo:
                simbolo.setUsado()
                print(f"Uso: variable '{nombre}' marcada como usada.")
            else:
                print(f"Error: variable '{nombre}' no definida.")

    # --- Declaración de funciones (prototipo o definición) ---
    def exitPrototipo_funcion(self, ctx:compiladoresParser.Prototipo_funcionContext):
        tipo = ctx.tipo().getText() if ctx.tipo() else "void"
        nombre = ctx.ID().getText()
        # Aquí podrías extraer los parámetros si lo deseas
        if self.ts.buscarSimboloContexto(nombre):
            print(f"Error: función '{nombre}' ya declarada en este contexto.")
        else:
            fun = Funcion(nombre, tipo, [])
            self.ts.addSimbolo(fun)
            print(f"Prototipo de función '{nombre}' tipo {tipo} declarado.")

    def exitDeclaracion_funcion(self, ctx:compiladoresParser.Declaracion_funcionContext):
        tipo = ctx.tipo().getText()
        nombre = ctx.ID().getText()
        if self.ts.buscarSimboloContexto(nombre):
            print(f"Error: función '{nombre}' ya declarada en este contexto.")
        else:
            fun = Funcion(nombre, tipo, [])
            self.ts.addSimbolo(fun)
            print(f"Función '{nombre}' tipo {tipo} declarada.")

    # --- Llamada a función ---
    def exitLlamada_funcion(self, ctx:compiladoresParser.Llamada_funcionContext):
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if simbolo and isinstance(simbolo, Funcion):
            simbolo.setUsado()
            print(f"Llamada a función '{nombre}' registrada como usada.")
        else:
            print(f"Error: función '{nombre}' no definida.")
