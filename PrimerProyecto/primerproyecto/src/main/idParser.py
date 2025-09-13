# Generated from c:/Users/aguca/AndroidStudioProjects/DHS/PrimerProyecto/primerproyecto/src/main/id.g4 by ANTLR 4.13.1
# encoding: utf-8
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
        4,1,3,15,2,0,7,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,3,0,13,
        8,0,1,0,0,0,1,0,0,0,16,0,12,1,0,0,0,2,3,5,1,0,0,3,4,6,0,-1,0,4,13,
        3,0,0,0,5,6,5,2,0,0,6,7,6,0,-1,0,7,13,3,0,0,0,8,9,5,3,0,0,9,10,6,
        0,-1,0,10,13,3,0,0,0,11,13,5,0,0,1,12,2,1,0,0,0,12,5,1,0,0,0,12,
        8,1,0,0,0,12,11,1,0,0,0,13,1,1,0,0,0,1,12
    ]

class idParser ( Parser ):

    grammarFileName = "id.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "ID", "NUMERO", "OTRO" ]

    RULE_s = 0

    ruleNames =  [ "s" ]

    EOF = Token.EOF
    ID=1
    NUMERO=2
    OTRO=3

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class SContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self._ID = None # Token
            self._NUMERO = None # Token
            self._OTRO = None # Token

        def ID(self):
            return self.getToken(idParser.ID, 0)

        def s(self):
            return self.getTypedRuleContext(idParser.SContext,0)


        def NUMERO(self):
            return self.getToken(idParser.NUMERO, 0)

        def OTRO(self):
            return self.getToken(idParser.OTRO, 0)

        def EOF(self):
            return self.getToken(idParser.EOF, 0)

        def getRuleIndex(self):
            return idParser.RULE_s

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterS" ):
                listener.enterS(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitS" ):
                listener.exitS(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitS" ):
                return visitor.visitS(self)
            else:
                return visitor.visitChildren(self)




    def s(self):

        localctx = idParser.SContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_s)
        try:
            self.state = 12
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2
                localctx._ID = self.match(idParser.ID)

                       System.out.println("ID ->" + localctx._ID.getText() + "<--");
                self.state = 4
                self.s()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 5
                localctx._NUMERO = self.match(idParser.NUMERO)

                       System.out.println("NUMERO ->" + localctx._NUMERO.getText() + "<--");
                self.state = 7
                self.s()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 8
                localctx._OTRO = self.match(idParser.OTRO)

                       System.out.println("OTRO ->" + localctx._OTRO.getText() + "<--");
                self.state = 10
                self.s()
                pass
            elif token in [-1]:
                self.enterOuterAlt(localctx, 4)
                self.state = 11
                self.match(idParser.EOF)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





