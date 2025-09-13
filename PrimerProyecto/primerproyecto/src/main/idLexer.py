# Generated from c:/Users/aguca/AndroidStudioProjects/DHS/PrimerProyecto/primerproyecto/src/main/id.g4 by ANTLR 4.13.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


  package compiladores;


def serializedATN():
    return [
        4,0,3,34,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,
        1,1,1,1,2,1,2,3,2,18,8,2,1,2,1,2,1,2,5,2,23,8,2,10,2,12,2,26,9,2,
        1,3,4,3,29,8,3,11,3,12,3,30,1,4,1,4,0,0,5,1,0,3,0,5,1,7,2,9,3,1,
        0,2,2,0,65,90,97,122,1,0,48,57,36,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,
        0,0,0,1,11,1,0,0,0,3,13,1,0,0,0,5,17,1,0,0,0,7,28,1,0,0,0,9,32,1,
        0,0,0,11,12,7,0,0,0,12,2,1,0,0,0,13,14,7,1,0,0,14,4,1,0,0,0,15,18,
        3,1,0,0,16,18,5,95,0,0,17,15,1,0,0,0,17,16,1,0,0,0,18,24,1,0,0,0,
        19,23,3,1,0,0,20,23,3,3,1,0,21,23,5,95,0,0,22,19,1,0,0,0,22,20,1,
        0,0,0,22,21,1,0,0,0,23,26,1,0,0,0,24,22,1,0,0,0,24,25,1,0,0,0,25,
        6,1,0,0,0,26,24,1,0,0,0,27,29,3,3,1,0,28,27,1,0,0,0,29,30,1,0,0,
        0,30,28,1,0,0,0,30,31,1,0,0,0,31,8,1,0,0,0,32,33,9,0,0,0,33,10,1,
        0,0,0,5,0,17,22,24,30,0
    ]

class idLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    ID = 1
    NUMERO = 2
    OTRO = 3

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "ID", "NUMERO", "OTRO" ]

    ruleNames = [ "LETRA", "DIGITO", "ID", "NUMERO", "OTRO" ]

    grammarFileName = "id.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


