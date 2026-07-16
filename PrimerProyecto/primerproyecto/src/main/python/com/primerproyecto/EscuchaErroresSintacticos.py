from antlr4.error.ErrorListener import ErrorListener
from Enumeraciones import TipoError

class EscuchaErroresSintacticos(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        texto = offendingSymbol.text if offendingSymbol is not None else ""
        mensaje = ""

        # Error parentesis de cierre
        if ("expecting ')'" in msg or "missing ')'" in msg or "no viable alternative at input" in msg) \
           and texto in ["{", ";", "else", "ID", "NUMERO"]:
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta un parentesis de cierre ')' antes de '{texto}' (linea {line})"

        # Error parentesis abierto
        elif ("extraneous input" in msg and texto == ")") or ("missing '('" in msg):
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta un parentesis de apertura '(' (linea {line})"

        # Error punto y coma
        elif ("expecting ';'" in msg
                or ("mismatched input" in msg and "expecting ';'" in msg)
                or ("mismatched input" in msg and texto in ["}", "else"])
                or ("no viable alternative at input" in msg and texto in ["int", "double", "float", "char", "bool", "if", "while", "for", "return"])):
            linea_reportada = line
            if "expecting ';'" in msg or "no viable alternative" in msg:
                tokens = recognizer.getInputStream().tokens
                if offendingSymbol.tokenIndex > 0:
                    prev_token = tokens[offendingSymbol.tokenIndex - 1]
                    linea_reportada = prev_token.line
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta un punto y coma ';' al final de la instruccion (linea {linea_reportada})"

        # Error declaracion de variables
        elif ("missing ID" in msg
              or ("mismatched input" in msg and "ID" in msg)
              or ("no viable alternative at input" in msg and texto.isidentifier())
              or (texto == "," and ("no viable alternative" in msg or "extraneous input" in msg))
              or ("missing ','" in msg)
              or ("extraneous input" in msg and texto.isidentifier())):
            mensaje = f"ERROR {TipoError.SINTACTICO}: formato incorrecto en la lista de declaracion de variables (linea {line})"

        # Error llave de cierre
        elif ("expecting '}'" in msg
              or "missing '}'" in msg
              or ("no viable alternative at input" in msg and texto == "<EOF>")):
            linea_reportada = line
            if texto == "<EOF>" and offendingSymbol is not None and offendingSymbol.tokenIndex > 0:
                tokens = recognizer.getInputStream().tokens
                prev_token = tokens[offendingSymbol.tokenIndex - 1]
                linea_reportada = prev_token.line
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta una llave de cierre '}}' (linea {linea_reportada})"

        # Error llave de apertura
        elif ("expecting '{'" in msg
              or "missing '{'" in msg
              or ("mismatched input" in msg and "expecting '{'" in msg)):
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta una llave de apertura '{{' (linea {line})"

        # Otros errores
        else:
            mensaje = f"ERROR {TipoError.SINTACTICO} (linea {line}, columna {column}): {msg}"

        self.errores.append(mensaje)
        print(mensaje)
