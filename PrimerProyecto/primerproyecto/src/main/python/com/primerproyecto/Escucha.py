from compiladoresListener import compiladoresListener
from compiladoresParser import compiladoresParser
from tabla_simbolos import TS, Variable, Funcion
import copy

class Escucha(compiladoresListener):
    def exitPrototipo_funcion(self, ctx:compiladoresParser.Prototipo_funcionContext):
        tipo = ctx.tipo().getText() if ctx.tipo() else "void"
        nombre = ctx.ID().getText()
        args = []
        if ctx.lista_parametros():
            params = ctx.lista_parametros().getText().split(',')
            for p in params:
                p = p.strip()
                if p:
                    # Asume formato tipo nombre
                    partes = p.split()
                    if len(partes) == 2:
                        args.append((partes[0], partes[1]))
        funcion = Funcion(nombre, tipo, args)
        self.ts.addFuncion(funcion)

    def exitDeclaracion_funcion(self, ctx:compiladoresParser.Declaracion_funcionContext):
        tipo = ctx.tipo().getText()
        nombre = ctx.ID().getText()
        args = []
        if ctx.lista_parametros():
            params = ctx.lista_parametros().getText().split(',')
            for p in params:
                p = p.strip()
                if p:
                    partes = p.split()
                    if len(partes) == 2:
                        args.append((partes[0], partes[1]))
        funcion = Funcion(nombre, tipo, args)
        self.ts.addFuncion(funcion)

    def exitLlamada_funcion(self, ctx:compiladoresParser.Llamada_funcionContext):
        nombre = ctx.ID().getText()
        funcion = self.ts.buscarFuncion(nombre)
        if not funcion:
            self.mensajes_error.append(f"Error semántico: función '{nombre}' no declarada.")
            self.error = True
    
    def __init__(self):
        super().__init__()
        self.ts = TS.getInstance()
        self.error = False
        self.contextos_finales = []
        self.mensajes_error = []

    def enterBloque(self, ctx:compiladoresParser.BloqueContext):
        self.ts.addContexto()

    def exitBloque(self, ctx:compiladoresParser.BloqueContext):
        # Guarda una copia profunda del contexto antes de borrarlo
        self.contextos_finales.append(copy.deepcopy(self.ts.contextos[-1]))
        self.ts.delContexto()

    def exitDeclaracion(self, ctx:compiladoresParser.DeclaracionContext):
        tipo = ctx.tipo().getText()
        texto = ctx.getText()
        declaracion = texto.replace(tipo, '').replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]

        # 1. Agrega todas las variables primero (sin inicializar)
        nombres = []
        for parte in partes:
            if '=' in parte:
                nombre = parte.split('=')[0].strip()
            else:
                nombre = parte
            if self.ts.buscarSimboloContexto(nombre):
                self.mensajes_error.append(f"Error semántico: variable '{nombre}' ya declarada en este contexto.")
                self.error = True
            else:
                var = Variable(nombre, tipo)
                var.setInicializado(False)
                self.ts.addSimbolo(var)
            nombres.append(nombre)

        # 2. Procesa inicializaciones y verifica uso
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=')]
                simbolo = self.ts.buscarSimboloContexto(nombre)
                if valor in nombres:
                    simbolo_origen = self.ts.buscarSimboloContexto(valor)
                    if simbolo_origen:
                        simbolo_origen.setUsado()
                        # Verifica tipo
                        if simbolo_origen.getTipoDato() != tipo:
                            self.mensajes_error.append(f"Error semántico: tipos incompatibles en inicialización de '{nombre}' ({tipo} = {simbolo_origen.getTipoDato()}).")
                            self.error = True
                    else:
                        self.mensajes_error.append(f"Error semántico: variable '{valor}' no declarada en inicialización de '{nombre}'.")
                        self.error = True
                else:
                    # Si es un número, deduce tipo
                    if valor.replace('.', '', 1).isdigit():
                        tipo_origen = 'float' if '.' in valor else 'int'
                        if tipo_origen != tipo:
                            self.mensajes_error.append(f"Error semántico: tipos incompatibles en inicialización de '{nombre}' ({tipo} = {tipo_origen}).")
                            self.error = True
                    else:
                        self.mensajes_error.append(f"Error semántico: variable '{valor}' no declarada en inicialización de '{nombre}'.")
                        self.error = True
                simbolo.setInicializado(True)

    def exitAsignacion(self, ctx:compiladoresParser.AsignacionContext):
        self.permitir_declaracion = False
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if not simbolo:
            self.mensajes_error.append(f"Error semántico: variable '{nombre}' no declarada.")
            self.error = True
            return
        # Verificar tipo de dato del valor asignado
        valor_ctx = ctx.opal()
        tipo_destino = simbolo.getTipoDato()
        tipo_origen = None
        # Si el valor es un ID, buscar su tipo
        if valor_ctx and valor_ctx.getText() in self.ts.contextos[-1].simbolos:
            simbolo_origen = self.ts.buscarSimbolo(valor_ctx.getText())
            if simbolo_origen:
                tipo_origen = simbolo_origen.getTipoDato()
        # Si el valor es un número, deducir tipo
        elif valor_ctx and valor_ctx.getText().replace('.', '', 1).isdigit():
            if '.' in valor_ctx.getText():
                tipo_origen = 'float'
            else:
                tipo_origen = 'int'
        # Si no se puede deducir, dejar tipo_origen en None
        # Permitir asignar literales numéricos float/double a float o double
        if tipo_origen:
            if tipo_destino != tipo_origen:
                # Si el origen es un literal numérico (no variable), permitir float/double indistintamente
                if valor_ctx and valor_ctx.getText().replace('.', '', 1).isdigit():
                    if tipo_destino in ['float', 'double'] and tipo_origen in ['float', 'double']:
                        pass  # permitido
                    else:
                        self.mensajes_error.append(f"Error semántico: tipos incompatibles en asignación a '{nombre}' ({tipo_destino} = {tipo_origen}).")
                        self.error = True
                else:
                    # Si el origen es variable, no permitir mezclar float/double
                    if (tipo_destino == 'float' and tipo_origen == 'double') or (tipo_destino == 'double' and tipo_origen == 'float'):
                        self.mensajes_error.append(f"Error semántico: no se puede asignar {tipo_origen} a {tipo_destino} en '{nombre}'.")
                        self.error = True
                    else:
                        self.mensajes_error.append(f"Error semántico: tipos incompatibles en asignación a '{nombre}' ({tipo_destino} = {tipo_origen}).")
                        self.error = True
        simbolo.setInicializado()

    def exitFactor(self, ctx:compiladoresParser.FactorContext):
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
            if isinstance(simbolo, Funcion):
                args_str = ', '.join([f"{t} {n}" for t, n in simbolo.getListaArgs()])
                print(f"funcion {simbolo.getTipoDato()} {nombre}({args_str})")
            else:
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
                if isinstance(simbolo, Funcion):
                    args_str = ', '.join([f"{t} {n}" for t, n in simbolo.getListaArgs()])
                    print(f"funcion {simbolo.getTipoDato()} {nombre}({args_str})")
                else:
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
