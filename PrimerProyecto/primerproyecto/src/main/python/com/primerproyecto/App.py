import sys
from antlr4 import *
from compiladoresLexer  import compiladoresLexer
from compiladoresParser import compiladoresParser
from Escucha import Escucha


def main(argv):
    archivo = "input/entrada.txt"
    if len(argv) > 1 :
        archivo = argv[1]
    input = FileStream(archivo)
    lexer = compiladoresLexer(input)
    stream = CommonTokenStream(lexer)
    parser = compiladoresParser(stream)
    
    escucha = Escucha()
    parser.addParseListener(escucha)
    print(escucha)# Imprime el numero de declaraciones (Lo que este en el metodo "__str__" de Escucha.py)
    
    tree = parser.s()
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)
    
#java -jar C:\Facultad\Aplicaciones\antlr\antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor C:\Users\aguca\AndroidStudioProjects\DHS\PrimerProyecto\primerproyecto\src\main\python\com\primerproyecto\compiladores.g4 -o .