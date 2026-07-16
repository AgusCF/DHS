from compiladoresListener import compiladoresListener
from compiladoresParser import compiladoresParser
from tabla_simbolos import TS, Variable, Funcion
from Enumeraciones import TipoError, CType
from antlr4 import ErrorNode, ParserRuleContext
import os

class Escucha(compiladoresListener):

    def __init__(self):
        super().__init__()
        self.ts = TS.getInstance()
        self.huboErrores = False
        self.stackLlamadas = []
        self.stackReturns = []
        self.tipoADeclarar = None

    def __str__(self):
        pass

    # ###
    # Utilidades
    # ###

    def registrarError(self, tipo, msj, ctx=None):
        self.huboErrores = True
        if ctx is not None and hasattr(ctx, 'start'):
            linea = ctx.start.line
        else:
            linea = '?'
        print(f"ERROR {tipo} (ln {linea}): {msj}")

    def comprobarExistenciaSimbolo(self, nombre, ctx=None):
        simbolo = self.ts.buscarSimbolo(nombre)
        if simbolo is None:
            self.registrarError(TipoError.SEMANTICO, f"El identificador '{nombre}' no existe.", ctx)
            return False
        else:
            simbolo.setUsado()
            return True

    def obtenerTipoResultante(self, ctx):
        try:
            rama_derecha = ctx.getChild(1)
            if rama_derecha.getChildCount() == 0:
                return ctx.getChild(0).tipo
            else:
                tipoResultante = ctx.getChild(0).tipo
                while rama_derecha.getChildCount() > 0:
                    tipo_leido = rama_derecha.getChild(1).tipo
                    tipoResultante = self.combinarTipos(tipoResultante, tipo_leido)
                    rama_derecha = rama_derecha.getChild(2)
                return tipoResultante
        except AttributeError:
            return CType.UNDETERMINED

    def combinarTipos(self, tipo1, tipo2, ctx=None):
        if tipo1 == CType.UNDETERMINED or tipo2 == CType.UNDETERMINED:
            return CType.UNDETERMINED
        if tipo1 == CType.VOID or tipo2 == CType.VOID:
            self.registrarError(TipoError.SEMANTICO, "Operacion invalida con tipo 'void'.", ctx)
            return CType.UNDETERMINED
        if tipo1.rank > tipo2.rank:
            return tipo1
        else:
            return tipo2

    def obtenerParams(self, ctx, nombre_funcion):
        lista_args = []
        if ctx.getChildCount() > 0:
            if ctx.getText() == 'void':
                lista_args.append((CType.VOID, None))
            elif 'void' in ctx.getText():
                self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' tiene una declaracion de parametros invalida con 'void'.", ctx)
            else:
                for i in range(ctx.getChildCount() // 2 + 1):
                    tipo_param = ctx.getChild(2*i).tipo().getText()
                    nombre_param = ctx.getChild(2*i).ID().getText() if ctx.getChild(2*i).ID() else None
                    lista_args.append((CType.fromStr(tipo_param), nombre_param))
        else:
            lista_args.append((CType.VOID, None))
        return lista_args

    # ###
    # Inicio
    # ###

    def enterPrograma(self, ctx):
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "ContenidoTS.txt"), "w") as f:
            pass
        print(" ------ Comienza el parsing ------ ")

    def exitPrograma(self, ctx):
        for llamada in self.stackLlamadas:
            funcion = self.ts.buscarSimbolo(llamada.getChild(0).getText())
            if funcion and not funcion.getInicializado():
                self.registrarError(TipoError.SEMANTICO, f"La funcion '{funcion.getNombre()}' no fue definida.", llamada)

        for contexto in self.ts.historialCTX:
            for nombre, simbolo in contexto.simbolos.items():
                if not simbolo.getUsado():
                    tipo_sim = "variable" if isinstance(simbolo, Variable) else "funcion"
                    self.registrarError(TipoError.SEMANTICO, f"El simbolo (tipo: {tipo_sim}) '{nombre}' fue declarado pero no fue usado.")

        print(" ------ Termina el parsing ------ ")

    # ###
    # Manejo de contextos
    # ###

    def enterBloque(self, ctx):
        self.ts.addContexto()
        if ctx.parentCtx is not None and isinstance(ctx.parentCtx, compiladoresParser.FuncionContext):
            self.cargarParametrosFuncion(ctx.parentCtx)

    def exitBloque(self, ctx):
        self.ts.delContexto()

    def enterIfor(self, ctx):
        self.ts.addContexto()

    def exitIfor(self, ctx):
        self.ts.delContexto()

    # ###
    # Declaracion de variables
    # ###

    def enterListaDeclaradores(self, ctx):
        self.tipoADeclarar = CType.fromStr(ctx.parentCtx.tipo().getText())

    def exitDeclarador(self, ctx):
        if ctx.ID() is None:
            return

        token = ctx.ID().getSymbol()
        nombre_variable = token.text

        if nombre_variable.startswith("<missing"):
            return

        if self.ts.buscarSimboloContexto(nombre_variable):
            self.registrarError(TipoError.SEMANTICO, f"La variable '{nombre_variable}' ya fue declarada en este contexto.", ctx)
            return

        nueva_variable = Variable(nombre_variable, self.tipoADeclarar)

        if ctx.inic().getChildCount() > 0:
            nueva_variable.setInicializado()

        self.ts.addSimbolo(nueva_variable)

    def cargarParametrosFuncion(self, ctx):
        lista_argumentos = self.obtenerParams(ctx.listParamsDef(), ctx.ID().getText())
        if not lista_argumentos:
            return
        if not lista_argumentos == [(CType.VOID, None)]:
            for tipo, nombre in lista_argumentos:
                nueva_variable = Variable(nombre, tipo)
                nueva_variable.setInicializado()
                self.ts.addSimbolo(nueva_variable)

    # ###
    # Funciones
    # ###

    def exitPrototipo(self, ctx):
        if any(isinstance(hijo, ErrorNode) for hijo in ctx.getChildren()):
            return

        nombre_funcion = ctx.ID().getText()

        if len(self.ts.contextos) != 1:
            self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' solo puede ser declarada en el contexto global.", ctx)
            return
        if self.ts.buscarSimbolo("main"):
            self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' no puede ser prototipada despues de 'main'.", ctx)
            return
        if nombre_funcion == "main":
            self.registrarError(TipoError.SEMANTICO, "La funcion 'main' no puede ser prototipada.", ctx)
            return
        if self.ts.buscarSimbolo(nombre_funcion):
            self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' ya fue declarada.", ctx)
            return

        tipo_retorno = CType.fromStr(ctx.tipo().getText())
        lista_argumentos = self.obtenerParams(ctx.getChild(3), nombre_funcion)
        if not lista_argumentos:
            return
        lista_tipos = [tipo for tipo, _ in lista_argumentos]
        nueva_funcion = Funcion(nombre_funcion, tipo_retorno, lista_tipos)
        self.ts.addSimbolo(nueva_funcion)

    def enterFuncion(self, ctx):
        self.stackReturns.clear()

    def exitFuncion(self, ctx):
        if any(isinstance(hijo, ErrorNode) for hijo in ctx.getChildren()):
            return

        nombre_funcion = ctx.ID().getText()
        existente = self.ts.buscarSimbolo(nombre_funcion)

        if len(self.ts.contextos) != 1:
            self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' solo puede ser declarada en el contexto global.", ctx)
            return
        if self.ts.buscarSimbolo("main"):
            if not existente:
                self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' no fue prototipada.", ctx)
                return
        if existente is not None:
            if existente.getInicializado():
                self.registrarError(TipoError.SEMANTICO, f"La funcion '{nombre_funcion}' ya fue definida.", ctx)
                return

        tipo_retorno = CType.fromStr(ctx.tipo().getText())
        lista_argumentos = self.obtenerParams(ctx.getChild(3), nombre_funcion)
        if not lista_argumentos:
            return
        lista_tipos = [tipo for tipo, _ in lista_argumentos]

        if existente is not None:
            if tipo_retorno != existente.getTipoDato() or lista_tipos != existente.getListaArgs():
                self.registrarError(TipoError.SEMANTICO, f"La definicion de la funcion '{nombre_funcion}' no coincide con su prototipo.", ctx)
                return
            existente.setInicializado()
            return

        nueva_funcion = Funcion(nombre_funcion, tipo_retorno, lista_tipos)
        nueva_funcion.setInicializado()
        if nombre_funcion == "main":
            nueva_funcion.setUsado()
        self.ts.addSimbolo(nueva_funcion)

        for tipo_retorno_recibido, ctx_return in self.stackReturns:
            if tipo_retorno != tipo_retorno_recibido:
                self.registrarError(TipoError.SEMANTICO, f"La instruccion 'return' en la funcion '{nombre_funcion}' tiene un error de tipo. Se esperaba '{tipo_retorno.name}', pero se recibio '{tipo_retorno_recibido.name}'.", ctx_return)

    # ###
    # Asignaciones y expresiones
    # ###

    def exitExpASIG(self, ctx):
        nombre_id = ctx.ID().getText()
        if self.comprobarExistenciaSimbolo(nombre_id, ctx):
            self.ts.buscarSimbolo(nombre_id).setInicializado()

    def exitFactorCore(self, ctx):
        ctx.tipo = CType.UNDETERMINED

        if ctx.ID():
            nombre_id = ctx.ID().getText()
            if self.comprobarExistenciaSimbolo(nombre_id, ctx):
                variable = self.ts.buscarSimbolo(nombre_id)
                ctx.tipo = variable.getTipoDato()
                if not variable.getInicializado():
                    self.registrarError(TipoError.SEMANTICO, f"La variable '{nombre_id}' fue usada sin ser inicializada.", ctx)
                variable.setUsado()

        if ctx.NUMERO():
            ctx.tipo = CType.FLOAT if '.' in ctx.NUMERO().getText() else CType.INT
        if ctx.CARACTER():
            ctx.tipo = CType.CHAR
        if ctx.TRUE_LIT():
            ctx.tipo = CType.BOOL
        if ctx.FALSE_LIT():
            ctx.tipo = CType.BOOL
        if ctx.PA():
            ctx.tipo = ctx.exp().tipo
        if ctx.llamadaFunc():
            ctx.tipo = ctx.llamadaFunc().tipo

    def exitFactor(self, ctx):
        if any(isinstance(hijo, ErrorNode) for hijo in ctx.getChildren()) or ctx.factorSufix() is None or ctx.factorSufix().factorCore() is None:
            ctx.tipo = CType.UNDETERMINED
        else:
            ctx.tipo = ctx.factorSufix().factorCore().tipo

    def exitTerm(self, ctx):
        ctx.tipo = self.obtenerTipoResultante(ctx)

    def exitExp(self, ctx):
        ctx.tipo = self.obtenerTipoResultante(ctx)

    def exitExpCOMP(self, ctx):
        ctx.tipo = self.obtenerTipoResultante(ctx)

    def exitExpIGUALDAD(self, ctx):
        ctx.tipo = self.obtenerTipoResultante(ctx)

    def exitExpAND(self, ctx):
        ctx.tipo = self.obtenerTipoResultante(ctx)

    def exitExpOR(self, ctx):
        ctx.tipo = self.obtenerTipoResultante(ctx)

    def exitOpal(self, ctx):
        ctx.tipo = ctx.getChild(0).tipo

    def exitLlamadaFunc(self, ctx):
        funcion = self.ts.buscarSimbolo(ctx.getChild(0).getText())

        if funcion is None:
            self.registrarError(TipoError.SEMANTICO, f"La funcion '{ctx.getChild(0).getText()}' no existe.", ctx)
            ctx.tipo = CType.UNDETERMINED
            return
        else:
            ctx.tipo = funcion.getTipoDato()

        if not funcion.getInicializado():
            self.stackLlamadas.append(ctx)

        lista_tipos_esperados = funcion.getListaArgs()

        if len(lista_tipos_esperados) != (ctx.getChild(2).getChildCount() // 2 + 1):
            self.registrarError(TipoError.SEMANTICO, f"La llamada a la funcion '{funcion.getNombre()}' tiene un error en la cantidad de parametros. Se esperaban {len(lista_tipos_esperados)} parametros, pero se recibieron {ctx.getChild(2).getChildCount()}.", ctx)
        else:
            for i, tipo_esperado in enumerate(lista_tipos_esperados):
                argumento = ctx.getChild(2).getChild(2*i)
                tipo_recibido = argumento.tipo
                if tipo_esperado != tipo_recibido:
                    self.registrarError(TipoError.SEMANTICO, f"La llamada a la funcion '{funcion.getNombre()}' tiene un error en el tipo del parametro {i+1}. Se esperaba '{tipo_esperado.name}', pero se recibio '{tipo_recibido.name}'.", ctx)

        funcion.setUsado()

    def exitIreturn(self, ctx):
        ancestro = ctx
        while ancestro is not None and not isinstance(ancestro, compiladoresParser.FuncionContext):
            ancestro = ancestro.parentCtx
        if ancestro is None:
            self.registrarError(TipoError.SEMANTICO, "La instruccion 'return' debe estar dentro de una funcion.", ctx)
            return

        if isinstance(ctx.getChild(1), compiladoresParser.OpalContext):
            tipo_retorno = ctx.getChild(1).tipo
        else:
            tipo_retorno = CType.VOID

        funcion_actual = self.ts.buscarSimbolo(ancestro.ID().getText())
        if funcion_actual is None:
            self.stackReturns.append((tipo_retorno, ctx))
        else:
            tipo_retorno_esperado = funcion_actual.getTipoDato()
            if tipo_retorno != tipo_retorno_esperado:
                self.registrarError(TipoError.SEMANTICO, f"La instruccion 'return' en la funcion '{funcion_actual.getNombre()}' tiene un error de tipo. Se esperaba '{tipo_retorno_esperado.name}', pero se recibio '{tipo_retorno.name}'.", ctx)
