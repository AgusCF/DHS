from compiladoresVisitor import compiladoresVisitor
from compiladoresParser import compiladoresParser
class Caminante(compiladoresVisitor):
    def __init__(self):
        self.instr = 0

    def visitS(self, ctx:compiladoresParser.SContext):
        print("Visitando la sentencia")
        return self.visitChildren(ctx)

    def visitInstruccion(self, ctx:compiladoresParser.InstruccionContext):
        self.instr += 1
        print(f"Número de instrucciones visitadas: {self.instr}")
        print("Instrucción" + str(self.instr))
        print("\t" + ctx.getText())
        print("Visitando una instrucción")
        return self.visitChildren(ctx)