# Compilador C Reducido - Trabajo Final DHS

## Desarrollo de Herramientas de Software

Proyecto final de la materia Desarrollo de Herramientas de Software. Se implementa un compilador para un lenguaje basado en C reducido utilizando ANTLR4 y Python3.

El compilador realiza las siguientes fases:
1. Analisis lexico y sintactico (ANTLR4)
2. Analisis semantico (verificacion de tipos, ambitos, declaraciones)
3. Generacion de codigo de tres direcciones
4. Optimizacion del codigo intermedio
5. Generacion de archivos de salida (tabla de simbolos, codigo intermedio, codigo optimizado)

---

## Arquitectura General

### Pipeline de Ejecucion

```
Archivo fuente (.txt)
        |
        v
   +---------+
   |  LEXER  |  compiladoresLexer.py (generado por ANTLR4)
   +---------+
        |
        v
   +----------+
   |  PARSER  |  compiladoresParser.py (generado por ANTLR4)
   +----------+
        |
        +---> EscuchaErroresSintacticos (detecta errores de sintaxis)
        |
        +---> Escucha (analisis semantico: tipos, ambitos, declaraciones)
        |
        v
   +-----------+
   |   TREE    |  Arbol de parseo (CST)
   +-----------+
        |
        v
   +-----------+
   | CAMINANTE |  Genera codigo de tres direcciones
   +-----------+
        |
        v
   +--------------+
   | OPTIMIZADOR  |  Plegado de constantes, propagacion de copia,
   +--------------+  eliminacion de codigo muerto
        |
        v
   +------------------+
   | Archivos de Salida|
   +------------------+
        |
        +---> ContenidoTS.txt      (tabla de simbolos)
        +---> CodigoIntermedio.txt (codigo de 3 direcciones)
        +---> CodigoOptimizado.txt (codigo optimizado)
```

### Estructura de Archivos

```
com/primerproyecto/
|-- compiladores.g4                 # Gramatica del lenguaje (ANTLR4)
|-- App.py                          # Punto de entrada del compilador
|-- Escucha.py                      # Listener de analisis semantico
|-- tabla_simbolos.py               # Tabla de simbolos (ID, Variable, Funcion, Contexto, TS)
|-- caminante.py                    # Visitor de generacion de codigo de 3 direcciones
|-- Optimizador.py                  # Optimizador de codigo intermedio
|-- Enumeraciones.py                # Enums: CType (tipos) y TipoError
|-- EscuchaErroresSintacticos.py    # Listener de errores de sintaxis
|-- compiladoresLexer.py            # Lexer generado por ANTLR4
|-- compiladoresParser.py           # Parser generado por ANTLR4
|-- compiladoresListener.py         # Listener base generado por ANTLR4
|-- compiladoresVisitor.py          # Visitor base generado por ANTLR4
|-- input/                          # Archivos de entrada
|   |-- entrada.txt
|   |-- test_extenso.txt
|-- output/                         # Archivos de salida generados
    |-- ContenidoTS.txt
    |-- CodigoIntermedio.txt
    |-- CodigoOptimizado.txt
```

### Tecnologias

- **ANTLR4 4.13.1**: Generador de parsers lexers a partir de gramaticas
- **Python 3**: Lenguaje de implementacion
- **Maven**: Gestor de dependencias del proyecto Java (para ANTLR4)
- **Git**: Control de versiones

---

## Archivos Detallados

### 1. `compiladores.g4` — Gramatica del Lenguaje

Define la sintaxis completa del lenguaje C reducido. Contiene 42 tokens y 30+ reglas de produccion.

#### Tokens (Lexer)

```antlr
// Caracteres de agrupacion
PA : '(' ;    PC : ')' ;
LLA : '{' ;   LLC : '}' ;
PYC : ';' ;

// Operadores logicos
IGUAL : '==' ;  DISTINTO : '!=' ;
MAYOR : '>' ;   MENOR : '<' ;
MAYORIG : '>=' ; MENORIG : '<=' ;
AND : '&&' ;    OR : '||' ;   NOT : '!' ;

// Operadores aritmeticos
ASIG : '=' ;   COMA : ',' ;
SUMA : '+' ;   INC : '++' ;
RESTA : '-' ;  DEC : '--' ;
MULT : '*' ;   DIV : '/' ;   MOD : '%' ;

// Tipos de datos
INT : 'int' ;  FLOAT : 'float' ;  CHAR : 'char' ;
BOOL : 'bool' ; VOID : 'void' ;

// Estructuras de control
IF : 'if' ;  ELSE : 'else' ;
FOR : 'for' ; WHILE : 'while' ;
RETURN : 'return' ;

// Literales
CARACTER : '\'' LETRA '\'' ;
TRUE_LIT : 'true' ;  FALSE_LIT : 'false' ;
NUMERO : ENTERO | DECIMAL ;
ENTERO : DIGITO+ ;
DECIMAL : DIGITO+ '.' DIGITO+ ;
ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;
```

#### Reglas de Precedencia de Operadores

La gramatica define la precedencia de operadores de menor a mayor prioridad usando reglas encadenadas:

```
opal -> expOR -> expAND -> expIGUALDAD -> expCOMP -> exp -> term -> factor -> factorSufix -> factorCore
```

Cada nivel maneja un tipo de operador:

| Nivel | Regla | Operadores | Ejemplo |
|-------|-------|------------|---------|
| 1 (menor) | `expOR` | `\|\|` | `a \|\| b` |
| 2 | `expAND` | `&&` | `a && b` |
| 3 | `expIGUALDAD` | `==`, `!=` | `a == b` |
| 4 | `expCOMP` | `>`, `<`, `>=`, `<=` | `a > b` |
| 5 | `exp` | `+`, `-` | `a + b` |
| 6 | `term` | `*`, `/`, `%` | `a * b` |
| 7 (mayor) | `factor` | `!`, `++`, `--` (prefijo) | `!a`, `++a` |
| 8 | `factorSufix` | `++`, `--` (sufijo) | `a++` |
| 9 | `factorCore` | literales, IDs, llamadas, parentesis | `a`, `f(x)`, `(a+b)` |

Ejemplo de implementacion de precedencia con recursion a la derecha:

```antlr
exp : term e ;
e : SUMA term e
  | RESTA term e
  |           // epsilon (fin de la cadena)
  ;
```

Esto permite parsear `a + b * c` como `a + (b * c)` porque `term` se resuelve primero que `e`.

#### Estructuras de Control

```antlr
// If-else
iif : IF PA opal PC instruccion ielse ;
ielse : ELSE instruccion | ;

// While
iwhile : WHILE PA opal PC instruccion ;

// For (con initialize, test, step)
ifor : FOR PA initialize PYC test PYC step PC instruccion ;
initialize : expDEC | expASIG (COMA expASIG)* | ;
test : opal | ;
step : expASIG (COMA expASIG)* | exp | ;
```

El `for` soporta tres formas de inicializacion:
- Declaracion: `for (int i = 0; ...)`
- Asignacion: `for (i = 0; ...)`
- Vacia: `for (; ...)`

#### Funciones

```antlr
// Prototipado (declaracion adelantada)
prototipo : tipo ID PA listParamsProt PC PYC ;
listParamsProt : parametroProt (COMA parametroProt)* | ;
parametroProt : tipo | tipo ID ;

// Definicion (con cuerpo)
funcion : tipo ID PA listParamsDef PC bloque ;
listParamsDef : parametroDef (COMA parametroDef)* | VOID | ;
parametroDef : tipo ID ;

// Llamada a funcion
llamadaFunc : ID PA listArgs PC ;
listArgs : opal (COMA opal)* | ;

// Return
ireturn : RETURN opal PYC | RETURN PYC ;
```

---

### 2. `App.py` — Punto de Entrada

Orquesta todo el pipeline de compilacion. Es el archivo que se ejecuta para compilar un programa.

#### Funcion Principal

```python
def main(argv):
    # 1. Resolucion de rutas (soporta ejecucion desde cualquier directorio)
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

    # 2. Creacion del Lexer y Parser
    input_stream = FileStream(archivo)
    lexer = compiladoresLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = compiladoresParser(stream)

    # 3. Configuracion de listeners
    parser.removeErrorListeners()
    escuchaErroresSintacticos = EscuchaErroresSintacticos()
    parser.addErrorListener(escuchaErroresSintacticos)

    escucha = Escucha()
    parser.addParseListener(escucha)

    # 4. Ejecucion del parsing
    tree = parser.programa()

    # 5. Generacion de salida (solo si no hay errores)
    if not escucha.huboErrores and not escuchaErroresSintacticos.errores:
        print("Entrada correcta. Generando archivos de salida...")

        # Tabla de simbolos
        with open(os.path.join(output_dir, "ContenidoTS.txt"), "w") as f:
            escucha.ts.imprimirTS(f)

        # Codigo de 3 direcciones
        visitante = Caminante()
        visitante.visitPrograma(tree)

        with open(os.path.join(output_dir, "CodigoIntermedio.txt"), "w") as f:
            for linea in visitante.codigoIntermedio:
                f.write(linea + "\n")

        # Optimizacion
        optimizador = Optimizador()
        ci_path = os.path.join(output_dir, "CodigoIntermedio.txt")
        co_path = os.path.join(output_dir, "CodigoOptimizado.txt")
        optimizador.optimizar(ci_path)
        optimizador.imprimir_codigo_optimizado(co_path)
    else:
        print("Entrada incorrecta. Limpiando archivos de salida...")
        # Limpia archivos de salida en caso de error
```

#### Ejecucion

```bash
# Desde el directorio del proyecto
python App.py input/entrada.txt

# Desde cualquier directorio (con path absoluto)
python PrimerProyecto/primerproyecto/src/main/python/com/primerproyecto/App.py
```

---

### 3. `Escucha.py` — Analisis Semantico

Listener de ANTLR4 que recorre el arbol de parseo realizando verificaciones semanticas durante el parsing.

#### Clase Principal

```python
class Escucha(compiladoresListener):
    def __init__(self):
        super().__init__()
        self.ts = TS.getInstance()           # Tabla de simbolos (singleton)
        self.huboErrores = False             # Flag de errores
        self.stackLlamadas = []              # Forward references a funciones
        self.stackReturns = []               # Returns antes de conocer la funcion
        self.tipoADeclarar = None            # Tipo actual al declarar variables
```

#### Manejo de Contextos (Ambitos)

Los contextos se crean al entrar a bloques `{...}` y a loops `for`:

```python
def enterBloque(self, ctx):
    self.ts.addContexto()   # Crea nuevo ambito
    # Si es el bloque de una funcion, carga los parametros como variables
    if ctx.parentCtx is not None and isinstance(ctx.parentCtx, compiladoresParser.FuncionContext):
        self.cargarParametrosFuncion(ctx.parentCtx)

def exitBloque(self, ctx):
    self.ts.delContexto()   # Elimina ambito (las variables locales se pierden)

def enterIfor(self, ctx):
    self.ts.addContexto()   # For crea su propio ambito

def exitIfor(self, ctx):
    self.ts.delContexto()
```

#### Declaracion de Variables

```python
def enterListaDeclaradores(self, ctx):
    # Obtiene el tipo del padre (expDEC) y lo guarda para usar en exitDeclarador
    self.tipoADeclarar = CType.fromStr(ctx.parentCtx.tipo().getText())

def exitDeclarador(self, ctx):
    if ctx.ID() is None:
        return

    nombre_variable = ctx.ID().getSymbol().text

    # Verifica que no exista en el contexto actual
    if self.ts.buscarSimboloContexto(nombre_variable):
        self.registrarError(TipoError.SEMANTICO,
            f"La variable '{nombre_variable}' ya fue declarada en este contexto.", ctx)
        return

    # Crea la variable y la agrega a la tabla de simbolos
    nueva_variable = Variable(nombre_variable, self.tipoADeclarar)
    if ctx.inic().getChildCount() > 0:
        nueva_variable.setInicializado()
    self.ts.addSimbolo(nueva_variable)
```

#### Verificacion de Tipos

La propagacion de tipos se realiza en cada nodo de expresion usando `obtenerTipoResultante()`:

```python
def obtenerTipoResultante(self, ctx):
    """
    Recorre la cadena de expresiones recursivas (ej: exp -> term e)
    y combina los tipos usando ranking.
    """
    try:
        rama_derecha = ctx.getChild(1)
        if rama_derecha.getChildCount() == 0:
            return ctx.getChild(0).tipo  # Solo un termino
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
    """
    Combina dos tipos usando ranking de precedencia.
    FLOAT > INT > CHAR > BOOL > VOID
    Si alguno es UNDETERMINED, el resultado es UNDETERMINED.
    """
    if tipo1 == CType.UNDETERMINED or tipo2 == CType.UNDETERMINED:
        return CType.UNDETERMINED
    if tipo1 == CType.VOID or tipo2 == CType.VOID:
        self.registrarError(TipoError.SEMANTICO, "Operacion invalida con tipo 'void'.", ctx)
        return CType.UNDETERMINED
    return tipo1 if tipo1.rank > tipo2.rank else tipo2
```

Ejemplo de uso: en la expresion `a + 3.5`, donde `a` es `INT`:
1. `a` tiene tipo `INT` (rank 3)
2. `3.5` tiene tipo `FLOAT` (rank 4)
3. `combinarTipos(INT, FLOAT)` retorna `FLOAT` (mayor rank)

#### Funciones: Prototipos y Definiciones

El listener verifica que:
1. Los prototipos solo se declaren en contexto global
2. Las definiciones coincidan con los prototipos (mismo tipo retorno, mismos argumentos)
3. No existan definiciones duplicadas
4. Las funciones se prototipen antes de `main()`

```python
def exitPrototipo(self, ctx):
    nombre_funcion = ctx.ID().getText()

    # Solo puede ser en contexto global
    if len(self.ts.contextos) != 1:
        self.registrarError(TipoError.SEMANTICO,
            f"La funcion '{nombre_funcion}' solo puede ser declarada en el contexto global.", ctx)
        return

    # No puede ser despues de main
    if self.ts.buscarSimbolo("main"):
        self.registrarError(TipoError.SEMANTICO,
            f"La funcion '{nombre_funcion}' no puede ser prototipada despues de 'main'.", ctx)
        return

    # No puede prototipar main
    if nombre_funcion == "main":
        self.registrarError(TipoError.SEMANTICO,
            "La funcion 'main' no puede ser prototipada.", ctx)
        return

    # Verifica que no exista ya
    if self.ts.buscarSimbolo(nombre_funcion):
        self.registrarError(TipoError.SEMANTICO,
            f"La funcion '{nombre_funcion}' ya fue declarada.", ctx)
        return

    # Registra el prototipo
    tipo_retorno = CType.fromStr(ctx.tipo().getText())
    lista_argumentos = self.obtenerParams(ctx.getChild(3), nombre_funcion)
    lista_tipos = [tipo for tipo, _ in lista_argumentos]
    nueva_funcion = Funcion(nombre_funcion, tipo_retorno, lista_tipos)
    self.ts.addSimbolo(nueva_funcion)
```

#### Llamadas a Funciones

```python
def exitLlamadaFunc(self, ctx):
    funcion = self.ts.buscarSimbolo(ctx.getChild(0).getText())

    if funcion is None:
        self.registrarError(TipoError.SEMANTICO,
            f"La funcion '{ctx.getChild(0).getText()}' no existe.", ctx)
        ctx.tipo = CType.UNDETERMINED
        return
    else:
        ctx.tipo = funcion.getTipoDato()  # Tipo de retorno

    # Verificacion de cantidad de argumentos
    lista_tipos_esperados = funcion.getListaArgs()
    if len(lista_tipos_esperados) != (ctx.getChild(2).getChildCount() // 2 + 1):
        self.registrarError(TipoError.SEMANTICO,
            f"La llamada a la funcion '{funcion.getNombre()}' tiene un error "
            f"en la cantidad de parametros.", ctx)
    else:
        # Verificacion de tipos de cada argumento
        for i, tipo_esperado in enumerate(lista_tipos_esperados):
            argumento = ctx.getChild(2).getChild(2*i)
            tipo_recibido = argumento.tipo
            if tipo_esperado != tipo_recibido:
                self.registrarError(TipoError.SEMANTICO,
                    f"La llamada a la funcion '{funcion.getNombre()}' tiene un error "
                    f"en el tipo del parametro {i+1}. Se esperaba '{tipo_esperado.name}', "
                    f"pero se recibio '{tipo_recibido.name}'.", ctx)

    funcion.setUsado()
```

#### Validacion de Return

```python
def exitIreturn(self, ctx):
    # Busca la funcion que contiene al return
    ancestro = ctx
    while ancestro is not None and not isinstance(ancestro, compiladoresParser.FuncionContext):
        ancestro = ancestro.parentCtx

    if ancestro is None:
        self.registrarError(TipoError.SEMANTICO,
            "La instruccion 'return' debe estar dentro de una funcion.", ctx)
        return

    # Obtiene el tipo del retorno
    if isinstance(ctx.getChild(1), compiladoresParser.OpalContext):
        tipo_retorno = ctx.getChild(1).tipo
    else:
        tipo_retorno = CType.VOID  # return sin valor

    # Verifica contra el tipo declarado de la funcion
    funcion_actual = self.ts.buscarSimbolo(ancestro.ID().getText())
    if funcion_actual is None:
        self.stackReturns.append((tipo_retorno, ctx))  # Forward reference
    else:
        tipo_retorno_esperado = funcion_actual.getTipoDato()
        if tipo_retorno != tipo_retorno_esperado:
            self.registrarError(TipoError.SEMANTICO,
                f"La instruccion 'return' en la funcion '{funcion_actual.getNombre()}' "
                f"tiene un error de tipo. Se esperaba '{tipo_retorno_esperado.name}', "
                f"pero se recibio '{tipo_retorno.name}'.", ctx)
```

#### Deteccion de No Usados

Al finalizar el parsing (`exitPrograma`), se verifica que todas las variables y funciones hayan sido usadas:

```python
def exitPrograma(self, ctx):
    # Verifica forward references no resueltas
    for llamada in self.stackLlamadas:
        funcion = self.ts.buscarSimbolo(llamada.getChild(0).getText())
        if funcion and not funcion.getInicializado():
            self.registrarError(TipoError.SEMANTICO,
                f"La funcion '{funcion.getNombre()}' no fue definida.", llamada)

    # Verifica simbolos no usados
    for contexto in self.ts.historialCTX:
        for nombre, simbolo in contexto.simbolos.items():
            if not simbolo.getUsado():
                tipo_sim = "variable" if isinstance(simbolo, Variable) else "funcion"
                self.registrarError(TipoError.SEMANTICO,
                    f"El simbolo (tipo: {tipo_sim}) '{nombre}' fue declarado pero no fue usado.")
```

---

### 4. `tabla_simbolos.py` — Tabla de Simbolos

Implementa la estructura de datos que almacena todas las variables, funciones y sus propiedades.

#### Jerarquia de Clases

```
ID (base)
|-- Variable
|-- Funcion

Contexto
|-- simbolos: dict[str, ID]
|-- nivel: int

TS (singleton)
|-- contextos: list[Contexto]    (stack activo)
|-- historialCTX: list[Contexto] (todos los contextos creados)
```

#### Clase `ID` (Base)

```python
class ID:
    def __init__(self, nombre, tipoDato):
        self.nombre = nombre        # Nombre del identificador
        self.tipoDato = tipoDato    # CType enum (INT, FLOAT, etc.)
        self.inicializado = False   # True si tiene valor asignado
        self.usado = False          # True si fue referenciado
```

#### Clase `Variable`

```python
class Variable(ID):
    def __init__(self, nombre, tipoDato):
        super().__init__(nombre, tipoDato)
```

#### Clase `Funcion`

```python
class Funcion(ID):
    def __init__(self, nombre, tipoDato, args=None):
        super().__init__(nombre, tipoDato)
        self.args = args if args else []  # Lista de CType de argumentos

    def getListaArgs(self):
        return self.args
```

Ejemplo: Para `int suma(int a, int b)`, la lista de args es `[CType.INT, CType.INT]`.

#### Clase `Contexto`

```python
class Contexto:
    def __init__(self):
        self.simbolos = {}   # Diccionario nombre -> ID
        self.nivel = 0       # Nivel de anidamiento (0 = global)

    def addSimbolo(self, id):
        self.simbolos[id.getNombre()] = id

    def buscarSimbolo(self, nombre):
        return self.simbolos.get(nombre, None)
```

#### Clase `TS` (Singleton)

```python
class TS:
    _instancia = None

    def __init__(self):
        self.contextos = []      # Stack de contextos activos
        self.historialCTX = []   # Todos los contextos creados (para impresion)
        self.addContexto()       # Crea el contexto global

    @staticmethod
    def getInstance():
        if TS._instancia is None:
            TS._instancia = TS()
        return TS._instancia

    def addContexto(self):
        nuevo = Contexto()
        nuevo.nivel = len(self.contextos)
        self.contextos.append(nuevo)
        self.historialCTX.append(nuevo)  # Se guarda para siempre

    def delContexto(self):
        if len(self.contextos) > 1:
            self.contextos.pop()  # No elimina el global

    def buscarSimbolo(self, nombre):
        """Busca en todos los contextos (de adentro hacia afuera)"""
        for contexto in reversed(self.contextos):
            simbolo = contexto.buscarSimbolo(nombre)
            if simbolo:
                return simbolo
        return None

    def buscarSimboloContexto(self, nombre):
        """Busca solo en el contexto actual"""
        return self.contextos[-1].buscarSimbolo(nombre)
```

La busqueda en cadena es fundamental para el soporte de ambitos anidados. Por ejemplo:

```c
int x = 10;              // Contexto #0 (global)
for (int i = 0; ...) {   // Contexto #1
    int x = 20;          // Contexto #2 (bloque del for)
    // x aqui se refiere al x del Contexto #2 (sombrea al global)
}
// x aqui se refiere al x del Contexto #0
```

#### Generacion del Archivo de Salida

```python
def imprimirTS(self, f):
    for idx, contexto in enumerate(self.historialCTX):
        prefijo = '    ' * contexto.nivel  # Indentacion segun nivel
        f.write(f"{prefijo}--- Contexto #{idx} (nivel {contexto.nivel}) ---\n")

        for nombre, simbolo in contexto.simbolos.items():
            if isinstance(simbolo, Funcion):
                args = simbolo.getListaArgs()
                args_str = ', '.join([f"{t.name}" for t in args]) if args else "void"
                f.write(f"{prefijo}funcion {simbolo.getTipoDato().name} "
                       f"{nombre}({args_str}) - "
                       f"{'definida' if simbolo.getInicializado() else 'prototipada'}, "
                       f"{'usada' if simbolo.getUsado() else 'no usada'}\n")
            else:
                estado = []
                if simbolo.getInicializado():
                    estado.append("inicializada")
                else:
                    estado.append("declarada")
                if simbolo.getUsado():
                    estado.append("usada")
                f.write(f"{prefijo}{simbolo.getTipoDato().name} {nombre} "
                       f": {', '.join(estado)}\n")
```

Ejemplo de salida (`ContenidoTS.txt`):

```
--- Contexto #0 (nivel 0) ---
funcion INT suma(INT, INT) - definida, usada
funcion INT main(VOID) - definida, usada
    --- Contexto #1 (nivel 1) ---
    INT x : inicializada, usada
    INT y : inicializada, usada
```

---

### 5. `caminante.py` — Generacion de Codigo de Tres Direcciones

Visitor de ANTLR4 que recorre el arbol de parseo generando codigo de tres direcciones.

#### Clase Principal

```python
class Caminante(compiladoresVisitor):
    def __init__(self):
        super().__init__()
        self.codigoIntermedio = []  # Lista de lineas de codigo
        self.tempCounter = 0        # Contador de temporales (t1, t2, ...)
        self.labelCounter = 0       # Contador de etiquetas (L1, L2, ...)

    def generarTemporal(self):
        self.tempCounter += 1
        return f"t{self.tempCounter}"

    def generarEtiqueta(self):
        self.labelCounter += 1
        return f"L{self.labelCounter}"
```

#### Generacion de Expresiones

Cada operador genera un temporal intermedio. Ejemplo para una expresion `a + b * c`:

```python
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
```

Para `a + b * c`, el codigo generado seria:

```
t1 = b * c      // term primero (mayor precedencia)
t2 = a + t1     // despues la suma
```

#### Pre y Post Incremento/Decremento

```python
def visitFactor(self, ctx):
    valor = self.visit(ctx.factorSufix())

    # Prefijo: ++a (primero incrementa, luego usa)
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

    # Sufijo: a++ (primero usa el valor, luego incrementa)
    if ctx.INC():
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {valor}")     # Guarda valor actual
        self.codigoIntermedio.append(f"{valor} = {valor} + 1") # Incrementa
        return temp  # Retorna el valor anterior

    if ctx.DEC():
        temp = self.generarTemporal()
        self.codigoIntermedio.append(f"{temp} = {valor}")
        self.codigoIntermedio.append(f"{valor} = {valor} - 1")
        return temp

    return valor
```

Diferencia entre `++i` e `i++`:

```
// ++i (prefijo): retorna valor ya incrementado
i = i + 1

// i++ (sufijo): retorna valor original, luego incrementa
t1 = i
i = i + 1
// t1 contiene el valor anterior de i
```

#### If-Else

```python
def visitIif(self, ctx):
    finLabel = self.generarEtiqueta()
    tieneElse = False

    if ctx.ielse().ELSE() is not None:
        tieneElse = True
        elseLabel = self.generarEtiqueta()

    condicion = self.visit(ctx.opal())
    self.codigoIntermedio.append(f"ifnot {condicion} jmp "
                                f"{elseLabel if tieneElse else finLabel}")
    self.visit(ctx.instruccion())  // Cuerpo del if

    if tieneElse:
        self.codigoIntermedio.append(f"jmp {finLabel}")
        self.codigoIntermedio.append(f"label {elseLabel}:")
        self.visit(ctx.ielse().instruccion())  // Cuerpo del else

    self.codigoIntermedio.append(f"label {finLabel}:")
```

Para `if (z > 15) { z = z + 1; } else { z = z - 1; }`:

```
t1 = z > 15
ifnot t1 jmp L2
z = z + 1
jmp L1
label L2:
z = z - 1
label L1:
```

#### While

```python
def visitIwhile(self, ctx):
    retorno = self.generarEtiqueta()
    fin = self.generarEtiqueta()

    self.codigoIntermedio.append(f"label {retorno}:")
    condicion = self.visit(ctx.opal())
    self.codigoIntermedio.append(f"ifnot {condicion} jmp {fin}")
    self.visit(ctx.instruccion())
    self.codigoIntermedio.append(f"jmp {retorno}")
    self.codigoIntermedio.append(f"label {fin}:")
```

Para `while (z > 0) { z = z - 1; }`:

```
label L1:
t1 = z > 0
ifnot t1 jmp L2
z = z - 1
jmp L1
label L2:
```

#### For

```python
def visitIfor(self, ctx):
    retorno = self.generarEtiqueta()
    fin = self.generarEtiqueta()

    self.visit(ctx.initialize())              // Inicializacion
    self.codigoIntermedio.append(f"label {retorno}:")
    condicion = self.visit(ctx.test())         // Condicion
    self.codigoIntermedio.append(f"ifnot {condicion} jmp {fin}")
    if ctx.instruccion() is not None:
        self.visit(ctx.instruccion())          // Cuerpo
    self.visit(ctx.step())                      // Incremento
    self.codigoIntermedio.append(f"jmp {retorno}")
    self.codigoIntermedio.append(f"label {fin}:")
```

Para `for (int i = 0; i < 5; i = i + 1) { z = z + i; }`:

```
i = 0
label L1:
t1 = i < 5
ifnot t1 jmp L2
z = z + i
i = i + 1
jmp L1
label L2:
```

#### Llamadas a Funciones

```python
def visitLlamadaFunc(self, ctx):
    nombreFuncion = ctx.ID().getText()
    listaArgs = ctx.listArgs().opal()

    # Push de argumentos (en orden)
    if listaArgs:
        for arg in listaArgs:
            valorArg = self.visit(arg)
            self.codigoIntermedio.append(f"push {valorArg}")

    # Push de etiqueta de retorno y salto a la funcion
    retorno = self.generarEtiqueta()
    self.codigoIntermedio.append(f"push {retorno}")
    self.codigoIntermedio.append(f"jmp {nombreFuncion}")
    self.codigoIntermedio.append(f"label {retorno}:")

    # Pop del valor de retorno
    tempRetorno = self.generarTemporal()
    self.codigoIntermedio.append(f"pop {tempRetorno}")
    return tempRetorno
```

Para `z = suma(x, y)`:

```
push x
push y
push L14
jmp suma
label L14:
pop t1
z = t1
```

#### Definicion de Funciones

```python
def visitFuncion(self, ctx):
    nombreFuncion = ctx.ID().getText()
    self.codigoIntermedio.append(f"label {nombreFuncion}:")

    if not nombreFuncion == "main":
        tempRetorno = self.generarTemporal()
        self.codigoIntermedio.append(f"pop {tempRetorno}")  # Pop etiqueta de retorno

    params = ctx.listParamsDef().parametroDef()
    if params:
        for param in reversed(params):  # Pop en orden inverso
            nombreParam = param.ID().getText()
            self.codigoIntermedio.append(f"pop {nombreParam}")

    self.visit(ctx.bloque())

    if not nombreFuncion == "main":
        self.codigoIntermedio.append(f"jmp {tempRetorno}")  # Salto de retorno
```

Para `int suma(int a, int b) { ... }`:

```
label suma:
pop t1          // Etiqueta de retorno
pop b           // Segundo parametro
pop a           // Primer parametro
...             // Cuerpo de la funcion
push resultado  // Valor de retorno
jmp t1          // Salto a quien llamo
```

---

### 6. `Optimizador.py` — Optimizacion de Codigo Intermedio

Opera sobre las lineas de texto del codigo intermedio (no sobre AST).

#### Arquitectura

```python
class Optimizador:
    def __init__(self):
        self.codigo = []  # Lista de lineas de codigo

    def optimizar(self, archivo_entrada):
        """Ejecuta las 3 pasadas iterativamente hasta convergencia"""
        self.cargar_codigo(archivo_entrada)

        while True:
            hubo_plegado = self.plegado_constantes()
            hubo_propagacion = self.propagacion_copia()
            hubo_eliminacion = self.eliminacion_codigo_muerto()

            if not (hubo_plegado or hubo_propagacion or hubo_eliminacion):
                break  # No hubo cambios, convergio
```

#### Expresiones Regulares

El optimizador usa regex para reconocer patrones en las lineas de codigo:

```python
# Patron para operacion binaria con dos constantes: t1 = 3 + 5
REGEX_BINARIA_CONSTANTE = re.compile(
    r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(-?\d+(?:\.\d+)?)\s*(==|!=|>=|<=|&&|\|\||[+\-*/%<>])\s*(-?\d+(?:\.\d+)?)$'
)

# Patron para asignacion simple: t1 = a
REGEX_ASIGNACION_SIMPLE = re.compile(
    r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)$'
)

# Patron para incremento: i = i + 1
REGEX_INCREMENTO = re.compile(
    r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\1\s*([+\-])\s*(?:1(?:\.0)?)\s*$'
)
```

#### Plegado de Constantes (Constant Folding)

Reemplaza operaciones con operandos constantes por su resultado:

```python
def plegado_constantes(self):
    nuevo_codigo = []
    hubo_cambios = False

    for linea in self.codigo:
        match = REGEX_BINARIA_CONSTANTE.match(linea)
        if match:
            destino, op1, operador, op2 = match.groups()
            val1 = float(op1)
            val2 = float(op2)

            if operador == '+':
                resultado = val1 + val2
            elif operador == '*':
                resultado = val1 * val2
            elif operador == '/':
                resultado = val1 / val2
            # ... otros operadores ...

            nueva_linea = f"{destino} = {resultado}"
            if nueva_linea != linea:
                hubo_cambios = True
            nuevo_codigo.append(nueva_linea)
            continue

        nuevo_codigo.append(linea)

    self.codigo = nuevo_codigo
    return hubo_cambios
```

Ejemplo:

```
// Antes:
t1 = 3 + 5
t2 = t1 * 2

// Despues:
t1 = 8
t2 = t1 * 2
```

#### Propagacion de Copia (Copy Propagation)

Reemplaza referencias a temporales con su valor original cuando es seguro:

```python
def propagacion_copia(self):
    nuevo_codigo = []
    hubo_cambios = False
    constantes = {}  # Maps: variable -> valor

    for linea in self.codigo:
        # Si hay salto, limpia el diccionario (no es seguro propagar)
        if REGEX_EFECTO.search(linea):
            constantes.clear()
            nuevo_codigo.append(linea)
            continue

        # Para asignaciones simples: t2 = a + b; resultado = t2
        # Se fusiona en: resultado = a + b
        if match := REGEX_ASIGNACION_SIMPLE.match(linea):
            destino, origen = match.groups()

            if nuevo_codigo:
                linea_previa = nuevo_codigo[-1]
                # Verifica si la linea anterior asigna a 'origen'
                if m_previo := re.match(
                    fr'^{re.escape(origen)}\s*=\s*(.*)$', linea_previa):
                    expresion_previa = m_previo.group(1)
                    nueva_linea = f"{destino} = {expresion_previa}"
                    hubo_cambios = True
                    nuevo_codigo.append(nueva_linea)
                    continue

            nuevo_codigo.append(linea)
            continue

        # Para asignaciones binarias: t3 = t1 + t2
        # Sustituye t1 y t2 si son conocidos
        if match := REGEX_ASIGNACION_BINARIA.match(linea):
            destino, op1, operador, op2 = match.groups()

            op1_cambiado = constantes.get(op1, op1)
            op2_cambiado = constantes.get(op2, op2)

            nueva_linea = f"{destino} = {op1_cambiado} {operador} {op2_cambiado}"
            if nueva_linea != linea:
                hubo_cambios = True
            nuevo_codigo.append(nueva_linea)
            continue

        nuevo_codigo.append(linea)

    self.codigo = nuevo_codigo
    return hubo_cambios
```

Ejemplo:

```
// Antes:
t2 = a + b
resultado = t2

// Despues (fusion de asignaciones):
resultado = a + b
```

#### Eliminacion de Codigo Muerto (Dead Code Elimination)

Elimina temporales que solo se asignan pero nunca se usan:

```python
def eliminacion_codigo_muerto(self):
    usos = {}
    nuevo_codigo = []

    # Primera pasada: contar usos de cada variable
    for linea in self.codigo:
        for match in re.finditer(ID, linea):
            var = match.group(0)
            usos[var] = usos.get(var, 0) + 1

    # Segunda pasada: eliminar asignaciones a temporales no usados
    for linea in self.codigo:
        if match := REGEX_ASIGNACION.match(linea):
            destino = match.group(1)
            # Solo elimina temporales (t1, t2, ...) con un solo uso
            if re.fullmatch(r't\d+', destino) and usos.get(destino, 0) == 1:
                hubo_cambios = True
                continue  # Elimina la linea
        nuevo_codigo.append(linea)

    self.codigo = nuevo_codigo
    return hubo_cambios
```

Ejemplo:

```
// Antes:
t1 = a + b    // t1 solo se asigna, nunca se usa
z = t1 + 1

// Despues:
z = t1 + 1    // t1 = a + b eliminado
```

#### Funcion de Limpiar Diccionario

Invalida entradas del diccionario cuando una variable es modificada:

```python
def limpiar_diccionario(mapa, clave_eliminada):
    # Elimina la variable directamente
    if clave_eliminada in mapa:
        del mapa[clave_eliminada]

    # Elimina cualquier entrada que contenga la variable en su expresion
    claves_a_borrar = [k for k, v in mapa.items()
                       if re.search(fr'\b{re.escape(clave_eliminada)}\b', v)]
    for k in claves_a_borrar:
        del mapa[k]
```

---

### 7. `Enumeraciones.py` — Enums de Tipos

Define los tipos de datos del lenguaje y los tipos de error.

```python
from enum import Enum, auto

class TipoError(Enum):
    SINTACTICO = auto()   # Errores de sintaxis (falta ;, }, etc.)
    SEMANTICO = auto()    # Errores semanticos (tipo incompatible, no declarada, etc.)

    def __str__(self):
        return self.name

class CType(Enum):
    UNDETERMINED = ("undetermined", -1)
    VOID = ("void", 0)
    BOOL = ("bool", 1)
    CHAR = ("char", 2)
    INT = ("int", 3)
    FLOAT = ("float", 4)

    def __init__(self, text, rank):
        self.text = text
        self.rank = rank  # Ranking para coercicion de tipos

    def __str__(self):
        return self.text

    def fromStr(texto: str):
        """Convierte un string a CType. Retorna UNDETERMINED si no encuentra."""
        for t in CType:
            if t.text == texto:
                return t
        return CType.UNDETERMINED
```

#### Ranking de Tipos

El ranking se usa para la coercicion automatica de tipos (implicit casting):

| Tipo | Rank | Ejemplo |
|------|------|---------|
| UNDETERMINED | -1 | Error de tipo |
| VOID | 0 | `void f()` |
| BOOL | 1 | `true`, `false` |
| CHAR | 2 | `'a'` |
| INT | 3 | `42` |
| FLOAT | 4 | `3.14` |

Cuando se combinan dos tipos, el de mayor ranking "gana":

```python
# En combinarTipos():
return tipo1 if tipo1.rank > tipo2.rank else tipo2
```

Ejemplo:
- `int + float` → `float` (rank 4 > rank 3)
- `char + int` → `int` (rank 3 > rank 2)
- `bool + int` → `int` (rank 3 > rank 1)

---

### 8. `EscuchaErroresSintacticos.py` — Listener de Errores de Sintaxis

Personaliza los mensajes de error de ANTLR4 para que sean en espanol y descriptivos.

```python
class EscuchaErroresSintacticos(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        texto = offendingSymbol.text if offendingSymbol is not None else ""
        mensaje = ""

        # Deteccion de errores comunes
        if "expecting ')'" in msg or "no viable alternative" in msg:
            if texto in ["{", ";", "else", "ID", "NUMERO"]:
                mensaje = f"ERROR {TipoError.SINTACTICO}: falta un parentesis de cierre ')' antes de '{texto}' (linea {line})"

        elif "expecting ';'" in msg or "mismatched input" in msg:
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta un punto y coma ';' al final de la instruccion (linea {line})"

        elif "expecting '}'" in msg or texto == "<EOF>":
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta una llave de cierre '}}' (linea {line})"

        elif "expecting '{'" in msg:
            mensaje = f"ERROR {TipoError.SINTACTICO}: falta una llave de apertura '{{' (linea {line})"

        else:
            mensaje = f"ERROR {TipoError.SINTACTICO} (linea {line}, columna {column}): {msg}"

        self.errores.append(mensaje)
        print(mensaje)
```

Ejemplos de errores detectados:

```
// Falta parentesis de cierre
if (x > 5 { ... }
→ ERROR SINTACTICO: falta un parentesis de cierre ')' antes de '{' (linea 1)

// Falta punto y coma
int x = 10
→ ERROR SINTACTICO: falta un punto y coma ';' al final de la instruccion (linea 1)

// Falta llave de cierre
int main() {
→ ERROR SINTACTICO: falta una llave de cierre '}' (linea 1)
```

---

### 9. Archivos Generados por ANTLR4

Los siguientes archivos son generados automaticamente por ANTLR4 a partir de `compiladores.g4`:

| Archivo | Descripcion |
|---------|-------------|
| `compiladoresLexer.py` | Lexer que convierte caracteres en tokens. Contiene la definicion de los 42 tokens (reglas lexicas). Generado a partir de las definiciones de tokens en la gramatica. |
| `compiladoresParser.py` | Parser que verifica la estructura sintactica. Contiene las clases de contexto para cada regla de produccion (30+ reglas). Generado a partir de las reglas del parser. |
| `compiladoresListener.py` | Interfaz base con metodos `enter`/`exit` para cada regla. Las clases `Escucha` y `EscuchaErroresSintacticos` heredan de ahi. |
| `compiladoresVisitor.py` | Interfaz base con metodos `visit` para cada regla. La clase `Caminante` hereda de ahi. |

#### Comando de Regeneracion

```bash
java -jar "C:\Facultad\Aplicaciones\antlr\antlr-4.13.1-complete.jar" \
    -Dlanguage=Python3 \
    -visitor \
    compiladores.g4 \
    -o .
```

> **Nota**: Estos archivos NO deben editarse manualmente. Si se modifica la gramatica (`compiladores.g4`), se deben regenerar ejecutando el comando anterior.

---

## Ejemplo Completo de Ejecucion

### Entrada (`input/entrada.txt`)

```c
int suma(int a, int b);

int suma(int a, int b) {
    int resultado;
    resultado = a + b;
    return resultado;
}

int main() {
    int x, y, z;
    x = 10;
    y = 20;
    z = suma(x, y);
    if (z > 15) {
        z = z + 1;
    } else {
        z = z - 1;
    }
    for (int i = 0; i < 5; i = i + 1) {
        z = z + i;
    }
    return z;
}
```

### Salida: `ContenidoTS.txt`

```
--- Contexto #0 (nivel 0) ---
funcion INT suma(INT, INT) - definida, usada
funcion INT main(VOID) - definida, usada
    --- Contexto #1 (nivel 1) ---
    INT resultado : inicializada, usada
    --- Contexto #2 (nivel 2) ---
    INT x : inicializada, usada
    INT y : inicializada, usada
    INT z : inicializada, usada
        --- Contexto #3 (nivel 3) ---
        INT i : inicializada, usada
            --- Contexto #4 (nivel 4) ---
            (vacio)
```

### Salida: `CodigoIntermedio.txt`

```
label suma:
pop t1
pop b
pop a
t2 = a + b
resultado = t2
push resultado
jmp t1
label main:
x = 10
y = 20
push x
push y
push L1
jmp suma
label L1:
pop t3
z = t3
t4 = z > 15
ifnot t4 jmp L3
z = z + 1
jmp L2
label L3:
z = z - 1
label L2:
i = 0
label L4:
t5 = i < 5
ifnot t5 jmp L6
z = z + i
i = i + 1
jmp L4
label L6:
push z
```

### Salida: `CodigoOptimizado.txt`

```
label suma:
pop t1
pop b
pop a
resultado = a + b
push resultado
jmp t1
label main:
x = 10
y = 20
push x
push y
push L1
jmp suma
label L1:
pop t3
z = t3
t4 = z > 15
ifnot t4 jmp L3
z = z + 1
jmp L2
label L3:
z = z - 1
label L2:
i = 0
label L4:
t5 = i < 5
ifnot t5 jmp L6
z = z + i
i = i + 1
jmp L4
label L6:
push z
```

---

## Errores que Detecta el Compilador

### Errores Sintacticos

| Error | Mensaje | Ejemplo |
|-------|---------|---------|
| Falta `)` | falta un parentesis de cierre `)` antes de ... | `if (x > 5 { }` |
| Falta `(` | falta un parentesis de apertura `(` | `if x > 5) { }` |
| Falta `;` | falta un punto y coma `;` al final de la instruccion | `int x = 10` (sin `;`) |
| Falta `}` | falta una llave de cierre `}` | `int main() {` |
| Falta `{` | falta una llave de apertura `{` | `int main() }` |
| Declaracion invalida | formato incorrecto en la lista de declaracion de variables | `int = 10` |

### Errores Semanticos

| Error | Mensaje | Ejemplo |
|-------|---------|---------|
| Variable no declarada | El identificador 'x' no existe. | `x = 10` (sin `int x`) |
| Redeclaracion | La variable 'x' ya fue declarada en este contexto. | `int x; int x;` |
| Tipo incompatible | Error en el tipo del parametro. Se esperaba 'INT', pero se recibio 'FLOAT'. | `int f(int a); f(3.5);` |
| Funcion no prototipada | La funcion 'f' no fue prototipada. | Definir `f` sin prototipo antes de `main` |
| Funcion no definida | La funcion 'f' no fue definida. | Prototipar `f` sin definirla |
| Redeclaracion de funcion | La funcion 'f' ya fue declarada. | `int f(); int f();` |
| Funcion no global | La funcion 'f' solo puede ser declarada en el contexto global. | `int main() { int f(); }` |
| Return incorrecto | La instruccion 'return' tiene un error de tipo. Se esperaba 'INT', pero se recibio 'FLOAT'. | `int f() { return 3.5; }` |
| Variable no usada | El simbolo (tipo: variable) 'x' fue declarado pero no fue usado. | `int x;` (sin usar `x`) |
| Variable no inicializada | La variable 'x' fue usada sin ser inicializada. | `int x; y = x + 1;` |
| Operacion con void | Operacion invalida con tipo 'void'. | `void f(); x = f() + 1;` |

---

## Ejecucion

### Requisitos

- Python 3.8+
- Java Runtime Environment (para ANTLR4)
- ANTLR4 4.13.1 (jar en `C:\Facultad\Aplicaciones\antlr\`)

### Pasos

```bash
# 1. Regenerar archivos ANTLR4 (solo si se modifica compiladores.g4)
java -jar "C:\Facultad\Aplicaciones\antlr\antlr-4.13.1-complete.jar" \
    -Dlanguage=Python3 -visitor compiladores.g4 -o .

# 2. Ejecutar el compilador
python App.py input/entrada.txt

# 3. Verificar archivos de salida en output/
cat output/ContenidoTS.txt
cat output/CodigoIntermedio.txt
cat output/CodigoOptimizado.txt
```

### Desde VS Code

1. Abrir el proyecto en VS Code
2. Seleccionar `App.py`
3. Presionar F5 (Run)
4. Los archivos de salida se generan en `output/`
