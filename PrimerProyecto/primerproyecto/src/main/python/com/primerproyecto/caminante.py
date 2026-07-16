from compiladoresVisitor import compiladoresVisitor
from compiladoresParser import compiladoresParser

class Caminante(compiladoresVisitor):
    def __init__(self):
        super().__init__()
        self.codigoIntermedio = []
        self.tempCounter = 0
        self.labelCounter = 0

    # ###
    # Utilidades
    # ###

    def generarTemporal(self):
        self.tempCounter += 1
        return f"t{self.tempCounter}"

    def generarEtiqueta(self):
        self.labelCounter += 1
        return f"L{self.labelCounter}"

    # ###
    # Recorrido del arbol
    # ###

    def visitPrograma(self, ctx):
        self.visitChildren(ctx)

    def visitInstrucciones(self, ctx):
        self.visitChildren(ctx)

    def visitInstruccion(self, ctx):
        self.visitChildren(ctx)

    def visitBloque(self, ctx):
        self.visitChildren(ctx)

    # ###
    # Asignaciones
    # ###

    def visitAsignacion(self, ctx):
        self.visit(ctx.expASIG())

    def visitExpASIG(self, ctx):
        destino = ctx.ID().getText()
        valor = self.visit(ctx.opal())
        self.codigoIntermedio.append(f"{destino} = {valor}")

    def visitOpal(self, ctx):
        return self.visit(ctx.expOR())

    def visitExpOR(self, ctx):
        left = self.visit(ctx.expAND())
        return self._resolverOR(left, ctx.o())

    def _resolverOR(self, left, octx):
        if octx is None or octx.getChildCount() == 0:
            return left
        right = self.visit(octx.expAND())
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {left} || {right}")
        return self._resolverOR(temp, octx.o())

    def visitExpAND(self, ctx):
        left = self.visit(ctx.expIGUALDAD())
        return self._resolverAND(left, ctx.a())

    def _resolverAND(self, left, actx):
        if actx is None or actx.getChildCount() == 0:
            return left
        right = self.visit(actx.expIGUALDAD())
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {left} && {right}")
        return self._resolverAND(temp, actx.a())

    def visitExpIGUALDAD(self, ctx):
        left = self.visit(ctx.expCOMP())
        return self._resolverIGUALDAD(left, ctx.i())

    def _resolverIGUALDAD(self, left, ictx):
        if ictx is None or ictx.getChildCount() == 0:
            return left

        if ictx.IGUAL():
            op = "=="
        else:
            op = "!="

        right = self.visit(ictx.expCOMP())
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {left} {op} {right}")
        return self._resolverIGUALDAD(temp, ictx.i())

    def visitExpCOMP(self, ctx):
        left = self.visit(ctx.exp())
        return self._resolverCOMP(left, ctx.c())

    def _resolverCOMP(self, left, cctx):
        if cctx is None or cctx.getChildCount() == 0:
            return left

        if cctx.MAYOR():
            op = ">"
        elif cctx.MAYORIG():
            op = ">="
        elif cctx.MENOR():
            op = "<"
        else:
            op = "<="

        right = self.visit(cctx.exp())
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {left} {op} {right}")
        return self._resolverCOMP(temp, cctx.c())

    def visitExp(self, ctx):
        left = self.visit(ctx.term())
        return self._resolverSUMA(left, ctx.e())

    def _resolverSUMA(self, left, ectx):
        if ectx is None or ectx.getChildCount() == 0:
            return left

        if ectx.SUMA():
            op = "+"
        else:
            op = "-"

        right = self.visit(ectx.term())
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {left} {op} {right}")
        return self._resolverSUMA(temp, ectx.e())

    def visitTerm(self, ctx):
        left = self.visit(ctx.factor())
        return self._resolverMULT(left, ctx.t())

    def _resolverMULT(self, left, tctx):
        if tctx is None or tctx.getChildCount() == 0:
            return left

        if tctx.MULT():
            op = "*"
        elif tctx.DIV():
            op = "/"
        else:
            op = "%"

        right = self.visit(tctx.factor())
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {left} {op} {right}")
        return self._resolverMULT(temp, tctx.t())

    def visitFactor(self, ctx):
        valor = self.visit(ctx.factorSufix())

        if ctx.INC():
            self.codigoIntermedio.append(f"{valor} = {valor} + 1")
            return valor

        if ctx.DEC():
            self.codigoIntermedio.append(f"{valor} = {valor} - 1")
            return valor

        if ctx.NOT():
            temp = self.generarTemporal()
            self.codigoIntermedio.append(f"{temp} = !{valor}")
            return temp

        return valor

    def visitFactorSufix(self, ctx):
        valor = self.visit(ctx.factorCore())

        if ctx.INC():
            temp = self.generarTemporal()
            self.codigoIntermedio.append(f"{temp} = {valor}")
            self.codigoIntermedio.append(f"{valor} = {valor} + 1")
            return temp

        if ctx.DEC():
            temp = self.generarTemporal()
            self.codigoIntermedio.append(f"{temp} = {valor}")
            self.codigoIntermedio.append(f"{valor} = {valor} - 1")
            return temp

        return valor

    def visitFactorCore(self, ctx):
        if ctx.NUMERO():
            return ctx.NUMERO().getText()
        if ctx.CARACTER():
            return ctx.CARACTER().getText()
        if ctx.TRUE_LIT():
            return "true"
        if ctx.FALSE_LIT():
            return "false"
        if ctx.ID():
            return ctx.ID().getText()
        if ctx.exp():
            return self.visit(ctx.exp())
        if ctx.llamadaFunc():
            return self.visit(ctx.llamadaFunc())

    # ###
    # Declaraciones
    # ###

    def visitDeclaracion(self, ctx):
        self.visit(ctx.expDEC())

    def visitExpDEC(self, ctx):
        self.visit(ctx.listaDeclaradores())

    def visitListaDeclaradores(self, ctx):
        for decl in ctx.declarador():
            self.visit(decl)

    def visitDeclarador(self, ctx):
        if ctx.inic().ASIG() is not None:
            destino = ctx.ID().getText()
            valor = self.visit(ctx.inic().opal())
            self.codigoIntermedio.append(f"{destino} = {valor}")

    # ###
    # Condicionales y bucles
    # ###

    def visitIif(self, ctx):
        finLabel = self.generarEtiqueta()
        tieneElse = False

        if ctx.ielse().ELSE() is not None:
            tieneElse = True
            elseLabel = self.generarEtiqueta()

        condicion = self.visit(ctx.opal())
        self.codigoIntermedio.append(f"ifnot {condicion} jmp {elseLabel if tieneElse else finLabel}")
        self.visit(ctx.instruccion())
        if tieneElse:
            self.codigoIntermedio.append(f"jmp {finLabel}")
            self.codigoIntermedio.append(f"label {elseLabel}:")
            self.visit(ctx.ielse().instruccion())
        self.codigoIntermedio.append(f"label {finLabel}:")

    def visitIwhile(self, ctx):
        retorno = self.generarEtiqueta()
        fin = self.generarEtiqueta()

        self.codigoIntermedio.append(f"label {retorno}:")
        condicion = self.visit(ctx.opal())
        self.codigoIntermedio.append(f"ifnot {condicion} jmp {fin}")
        self.visit(ctx.instruccion())
        self.codigoIntermedio.append(f"jmp {retorno}")
        self.codigoIntermedio.append(f"label {fin}:")

    def visitIfor(self, ctx):
        retorno = self.generarEtiqueta()
        fin = self.generarEtiqueta()

        self.visit(ctx.initialize())
        self.codigoIntermedio.append(f"label {retorno}:")
        condicion = self.visit(ctx.test())
        self.codigoIntermedio.append(f"ifnot {condicion} jmp {fin}")
        if ctx.instruccion() is not None:
            self.visit(ctx.instruccion())
        self.visit(ctx.step())
        self.codigoIntermedio.append(f"jmp {retorno}")
        self.codigoIntermedio.append(f"label {fin}:")

    def visitInitialize(self, ctx):
        if ctx.expDEC():
            self.visit(ctx.expDEC())
        if ctx.expASIG():
            for e in ctx.expASIG():
                self.visit(e)

    def visitTest(self, ctx):
        if ctx.opal() is not None:
            return self.visit(ctx.opal())

    def visitStep(self, ctx):
        if ctx.expASIG():
            for e in ctx.expASIG():
                self.visit(e)
        elif ctx.exp() is not None:
            self.visit(ctx.exp())

    # ###
    # Funciones
    # ###

    def visitLlamadaFunc(self, ctx):
        nombreFuncion = ctx.ID().getText()
        listaArgs = ctx.listArgs().opal()

        if listaArgs:
            for arg in listaArgs:
                valorArg = self.visit(arg)
                self.codigoIntermedio.append(f"push {valorArg}")

        retorno = self.generarEtiqueta()
        self.codigoIntermedio.append(f"push {retorno}")
        self.codigoIntermedio.append(f"jmp {nombreFuncion}")
        self.codigoIntermedio.append(f"label {retorno}:")

        tempRetorno = self.generarTemporal()
        self.codigoIntermedio.append(f"pop {tempRetorno}")
        return tempRetorno

    def visitFuncion(self, ctx):
        nombreFuncion = ctx.ID().getText()
        self.codigoIntermedio.append(f"label {nombreFuncion}:")

        if not nombreFuncion == "main":
            tempRetorno = self.generarTemporal()
            self.codigoIntermedio.append(f"pop {tempRetorno}")

        params = ctx.listParamsDef().parametroDef()
        if params:
            for param in reversed(params):
                nombreParam = param.ID().getText()
                self.codigoIntermedio.append(f"pop {nombreParam}")

        self.visit(ctx.bloque())

        if not nombreFuncion == "main":
            self.codigoIntermedio.append(f"jmp {tempRetorno}")

    def visitIreturn(self, ctx):
        if ctx.opal() is not None:
            valorRetorno = self.visit(ctx.opal())
            self.codigoIntermedio.append(f"push {valorRetorno}")
        else:
            self.codigoIntermedio.append(f"push None")
