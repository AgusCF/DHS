import re

# ###
# Reglas lexicas para reconocer patrones de codigo intermedio
# ###

ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
TEMPORAL = r't\d+'
NUM = r'-?\d+(?:\.\d+)?'
OP_BIN = r'==|!=|>=|<=|&&|\|\||[+\-*/%<>]'
OP_UNARIO = r'!'

REGEX_EFECTO = re.compile(r'\b(ifnot|if|push|pop|jmp|label)\b')
REGEX_INCREMENTO = re.compile(fr'^({ID})\s*=\s*\\1\s*([+\-])\s*(?:1(?:\.0)?)\s*$')
REGEX_BINARIA_CONSTANTE = re.compile(fr'^({ID})\s*=\s*({NUM})\s*({OP_BIN})\s*({NUM})$')
REGEX_UNARIA_CONSTANTE = re.compile(fr'^({ID})\s*=\s*({OP_UNARIO})\s*({NUM})$')
REGEX_ASIGNACION_CONSTANTE = re.compile(fr'^({ID})\s*=\s*({NUM})$')
REGEX_ASIGNACION_SIMPLE = re.compile(fr'^({ID})\s*=\s*({ID})$')
REGEX_ASIGNACION_BINARIA = re.compile(fr'^({ID})\s*=\s*({ID}|{NUM})\s*({OP_BIN})\s*({ID}|{NUM})$')
REGEX_ASIGNACION = re.compile(fr'^({ID})\s*=\s*(.+)$')

# ###
# Optimizador de codigo intermedio
# ###

class Optimizador:
    def __init__(self):
        self.codigo = []

    def optimizar(self, archivo_entrada):
        if not self.cargar_codigo(archivo_entrada) or len(self.codigo) == 0:
            print("No hay codigo para optimizar.")
            return

        print("OPTIMIZANDO CODIGO INTERMEDIO...")
        iteracion = 1
        while True:
            print(f"Iteracion {iteracion}")
            hubo_plegado = self.plegado_constantes()
            hubo_propagacion = self.propagacion_copia()
            hubo_eliminacion = self.eliminacion_codigo_muerto()

            if not (hubo_plegado or hubo_propagacion or hubo_eliminacion):
                print("No se realizaron mas cambios. Terminando optimizacion...")
                break
            iteracion += 1

    def cargar_codigo(self, archivo_entrada):
        try:
            with open(archivo_entrada, "r") as f:
                self.codigo = [linea.strip() for linea in f.readlines()]
            return True
        except FileNotFoundError:
            self.codigo = []
            print(f"ERROR: '{archivo_entrada}' no encontrado.")
            return False
        except Exception as e:
            self.codigo = []
            print(f"ERROR al cargar el archivo: {e}")
            return False

    def imprimir_codigo_optimizado(self, archivo_salida):
        with open(archivo_salida, "w") as f:
            for linea in self.codigo:
                f.write(linea + "\n")
        print(f"Codigo optimizado guardado en '{archivo_salida}'.")

    # --- Plegado de constantes ---
    def plegado_constantes(self):
        nuevo_codigo = []
        hubo_cambios = False

        for linea in self.codigo:
            match = REGEX_BINARIA_CONSTANTE.match(linea)
            if match:
                destino, op1, operador, op2 = match.groups()
                val1 = float(op1)
                val2 = float(op2)
                resultado = None

                try:
                    if operador == '+':
                        resultado = val1 + val2
                    elif operador == '-':
                        resultado = val1 - val2
                    elif operador == '*':
                        resultado = val1 * val2
                    elif operador == '/':
                        if val2 != 0:
                            if op1.isdigit() and op2.isdigit():
                                resultado = val1 // val2
                            else:
                                resultado = val1 / val2
                        else:
                            raise ZeroDivisionError("Division por cero")
                    elif operador == '%':
                        if val2 != 0:
                            if op1.isdigit() and op2.isdigit():
                                resultado = val1 % val2
                            else:
                                raise ValueError("Operador modulo solo valido para enteros")
                        else:
                            raise ZeroDivisionError("Modulo por cero")
                    elif operador == '||':
                        resultado = 1 if (val1 != 0 or val2 != 0) else 0
                    elif operador == '&&':
                        resultado = 1 if (val1 != 0 and val2 != 0) else 0
                    elif operador == '==':
                        resultado = 1 if val1 == val2 else 0
                    elif operador == '!=':
                        resultado = 1 if val1 != val2 else 0
                    elif operador == '>':
                        resultado = 1 if val1 > val2 else 0
                    elif operador == '>=':
                        resultado = 1 if val1 >= val2 else 0
                    elif operador == '<':
                        resultado = 1 if val1 < val2 else 0
                    elif operador == '<=':
                        resultado = 1 if val1 <= val2 else 0
                    else:
                        nuevo_codigo.append(linea)
                        continue

                    if isinstance(resultado, float) and resultado.is_integer():
                        resultado = int(resultado)

                    nueva_linea = f"{destino} = {resultado}"
                    if nueva_linea != linea:
                        print(f"Plegado de constantes: '{linea}' -> '{nueva_linea}'")
                        hubo_cambios = True
                    nuevo_codigo.append(nueva_linea)
                    continue

                except (ZeroDivisionError, ValueError) as e:
                    nuevo_codigo.append(linea)
                    print(f"ERROR: {e}. No se puede optimizar la linea '{linea}'")
                    continue

            match = REGEX_UNARIA_CONSTANTE.match(linea)
            if match:
                destino, operador, operando = match.groups()
                val = float(operando)
                resultado = 0 if val != 0 else 1
                nueva_linea = f"{destino} = {resultado}"
                if nueva_linea != linea:
                    print(f"Plegado de constantes: '{linea}' -> '{nueva_linea}'")
                    hubo_cambios = True
                nuevo_codigo.append(nueva_linea)
                continue

            nuevo_codigo.append(linea)

        self.codigo = nuevo_codigo
        return hubo_cambios

    # --- Propagacion de copia ---
    def propagacion_copia(self):
        nuevo_codigo = []
        hubo_cambios = False
        constantes = {}
        bloqueados = set()

        for linea in self.codigo:
            if REGEX_EFECTO.search(linea):
                constantes.clear()
                bloqueados.clear()
                nuevo_codigo.append(linea)
                continue

            if match := REGEX_INCREMENTO.match(linea):
                var_incrementada = match.group(1)
                limpiar_diccionario(constantes, var_incrementada)
                if nuevo_codigo:
                    if m_previo := REGEX_ASIGNACION_SIMPLE.match(nuevo_codigo[-1]):
                        destino_prev, origen_prev = m_previo.groups()
                        if origen_prev == var_incrementada and destino_prev.startswith('t'):
                            bloqueados.add(destino_prev)
                    nuevo_codigo.append(linea)
                    continue

            if match := REGEX_ASIGNACION_CONSTANTE.match(linea):
                variable, valor = match.groups()
                limpiar_diccionario(constantes, variable)
                constantes[variable] = valor
                nuevo_codigo.append(linea)
                continue

            if match := REGEX_ASIGNACION_SIMPLE.match(linea):
                destino, origen = match.groups()
                limpiar_diccionario(constantes, destino)

                if nuevo_codigo:
                    linea_previa = nuevo_codigo[-1]
                    if m_previo := re.match(fr'^{re.escape(origen)}\s*=\s*(.*)$', linea_previa):
                        expresion_previa = m_previo.group(1)
                        nueva_linea = f"{destino} = {expresion_previa}"
                        hubo_cambios = True
                        print(f"Propagacion: '{linea_previa}' + '{linea}' -> '{nueva_linea}'")
                        nuevo_codigo.append(nueva_linea)
                        continue

                if origen in constantes and origen not in bloqueados:
                    nueva_linea = f"{destino} = {constantes[origen]}"
                    hubo_cambios = True
                    print(f"Propagacion: '{linea}' -> '{nueva_linea}'")
                    nuevo_codigo.append(nueva_linea)
                    continue

                nuevo_codigo.append(linea)
                continue

            if match := REGEX_ASIGNACION_BINARIA.match(linea):
                destino, op1, operador, op2 = match.groups()
                limpiar_diccionario(constantes, destino)

                if op1 in constantes and op1 not in bloqueados:
                    op1_cambiado = constantes[op1]
                else:
                    op1_cambiado = op1
                if op2 in constantes and op2 not in bloqueados:
                    op2_cambiado = constantes[op2]
                else:
                    op2_cambiado = op2

                nueva_linea = f"{destino} = {op1_cambiado} {operador} {op2_cambiado}"
                if nueva_linea != linea:
                    hubo_cambios = True
                    print(f"Propagacion: '{linea}' -> '{nueva_linea}'")
                nuevo_codigo.append(nueva_linea)
                continue

            nuevo_codigo.append(linea)

        self.codigo = nuevo_codigo
        return hubo_cambios

    # --- Eliminacion de codigo muerto ---
    def eliminacion_codigo_muerto(self):
        usos = {}
        nuevo_codigo = []
        hubo_cambios = False

        for linea in self.codigo:
            for match in re.finditer(ID, linea):
                var = match.group(0)
                if var not in usos:
                    usos[var] = 0
                usos[var] += 1

        for linea in self.codigo:
            if match := REGEX_ASIGNACION.match(linea):
                destino = match.group(1)
                if re.fullmatch(TEMPORAL, destino) and usos.get(destino, 0) == 1:
                    hubo_cambios = True
                    print(f"Eliminacion de codigo muerto: '{linea}' eliminado porque '{destino}' no se usa.")
                    continue
            nuevo_codigo.append(linea)

        self.codigo = nuevo_codigo
        return hubo_cambios

# ###
# Utilidades
# ###

def limpiar_diccionario(mapa, clave_eliminada):
    if clave_eliminada in mapa:
        del mapa[clave_eliminada]

    claves_a_borrar = [k for k, v in mapa.items() if re.search(fr'\b{re.escape(clave_eliminada)}\b', v)]
    for k in claves_a_borrar:
        del mapa[k]
