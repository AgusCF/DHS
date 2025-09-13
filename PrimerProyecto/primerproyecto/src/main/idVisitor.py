# Generated from c:/Users/aguca/AndroidStudioProjects/DHS/PrimerProyecto/primerproyecto/src/main/id.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .idParser import idParser
else:
    from idParser import idParser

  package compiladores;


# This class defines a complete generic visitor for a parse tree produced by idParser.

class idVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by idParser#s.
    def visitS(self, ctx:idParser.SContext):
        return self.visitChildren(ctx)



del idParser