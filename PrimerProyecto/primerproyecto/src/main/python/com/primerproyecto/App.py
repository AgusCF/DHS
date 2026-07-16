import sys
import os
from antlr4 import *
from compiladoresLexer import compiladoresLexer
from compiladoresParser import compiladoresParser
from Escucha import Escucha
from EscuchaErroresSintacticos import EscuchaErroresSintacticos
from caminante import Caminante
from Optimizador import Optimizador

def main(argv):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    if len(argv) > 1:
        archivo = os.path.abspath(argv[1])
    elif os.path.exists(os.path.join(cwd, "input", "entrada.txt")):
        archivo = os.path.join(cwd, "input", "entrada.txt")
    else:
        archivo = os.path.join(base_dir, "input", "entrada.txt")

    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    input = FileStream(archivo)
    lexer = compiladoresLexer(input)
    stream = CommonTokenStream(lexer)
    parser = compiladoresParser(stream)

    parser.removeErrorListeners()
    escuchaErroresSintacticos = EscuchaErroresSintacticos()
    parser.addErrorListener(escuchaErroresSintacticos)

    escucha = Escucha()
    parser.addParseListener(escucha)

    tree = parser.programa()

    if not escucha.huboErrores and not escuchaErroresSintacticos.errores:
        print("Entrada correcta. Generando archivos de salida...")

        with open(os.path.join(output_dir, "ContenidoTS.txt"), "w") as f:
            escucha.ts.imprimirTS(f)

        visitante = Caminante()
        visitante.visitPrograma(tree)

        with open(os.path.join(output_dir, "CodigoIntermedio.txt"), "w") as f:
            for linea in visitante.codigoIntermedio:
                f.write(linea + "\n")

        optimizador = Optimizador()
        ci_path = os.path.join(output_dir, "CodigoIntermedio.txt")
        co_path = os.path.join(output_dir, "CodigoOptimizado.txt")
        optimizador.optimizar(ci_path)
        optimizador.imprimir_codigo_optimizado(co_path)

    else:
        print("Entrada incorrecta. Limpiando archivos de salida...")
        with open(os.path.join(output_dir, "ContenidoTS.txt"), "w") as f:
            pass
        with open(os.path.join(output_dir, "CodigoIntermedio.txt"), "w") as f:
            pass
        with open(os.path.join(output_dir, "CodigoOptimizado.txt"), "w") as f:
            pass

if __name__ == '__main__':
    main(sys.argv)
