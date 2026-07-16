grammar compiladores;

fragment LETRA : [A-Za-z] ;
fragment DIGITO : [0-9] ;

// Caracteres de agrupación
PA : '(' ;
PC : ')' ;
LLA : '{' ;
LLC : '}' ;
PYC : ';' ;

// Operadores lógicos
IGUAL    : '==' ;
DISTINTO :'!=' ;
MAYOR    : '>' ;
MENOR    : '<' ;
MAYORIG  : '>=' ;
MENORIG  : '<=' ;
AND      : '&&' ;
OR       : '||' ;
NOT      : '!' ;

// Operadores aritméticos
ASIG : '=' ;
COMA : ',' ;
SUMA : '+' ;
INC : '++' ;
RESTA : '-' ;
DEC : '--' ;
MULT : '*' ;
DIV : '/' ;
MOD : '%' ;

// Palabras reservadas - Tipos de datos
INT : 'int' ;
FLOAT : 'float' ;
CHAR : 'char' ;
BOOL : 'bool' ;
VOID : 'void' ;

// Estructuras de control
IF :    'if' ;
ELSE :  'else' ;
FOR :   'for' ;
WHILE : 'while' ;

RETURN : 'return' ;

// Literales
CARACTER : '\'' LETRA '\'' ;
TRUE_LIT : 'true' ;
FALSE_LIT : 'false' ;

NUMERO : ENTERO
       | DECIMAL
       ;
ENTERO : DIGITO+ ;
DECIMAL : DIGITO+ '.' DIGITO+ ;

ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;

WS : [ \n\r\t] -> skip ;
OTRO : . ;

// ======= Estructura basica =======

programa : instrucciones EOF ;

instrucciones : instruccion instrucciones
              |
              ;

instruccion : asignacion
            | declaracion
            | iif
            | iwhile
            | ifor
            | bloque
            | prototipo
            | funcion
            | ireturn
            | llamadaFunc PYC
            ;

bloque : LLA instrucciones LLC ;

// ======= Funciones =======

// Prototipado
prototipo : tipo ID PA listParamsProt PC PYC ;
listParamsProt : parametroProt (COMA parametroProt)*
               |
               ;
parametroProt : tipo
              | tipo ID
              ;

// Definición
funcion : tipo ID PA listParamsDef PC bloque ;
listParamsDef : parametroDef (COMA parametroDef)*
              | VOID
              |
              ;
parametroDef : tipo ID;

ireturn : RETURN opal PYC
        | RETURN PYC
        ;

// Llamada
llamadaFunc : ID PA listArgs PC ;
listArgs : opal (COMA opal)*
         |
         ;

// ======= Instrucciones de control =======

iwhile : WHILE PA opal PC instruccion ;

iif : IF PA opal PC instruccion ielse ;
ielse : ELSE instruccion
      |
      ;

ifor : FOR PA initialize PYC test PYC step PC instruccion
     | FOR PA initialize PYC test PYC step PC PYC
     ;

initialize : expDEC
           | expASIG (COMA expASIG)*
           |
           ;

test : opal
     |
     ;

step: expASIG (COMA expASIG)*
    | exp
    |
    ;

// ======= Declaraciones y asignación de variables =======

declaracion : expDEC PYC ;
expDEC : tipo listaDeclaradores ;
tipo : INT
     | FLOAT
     | CHAR
     | BOOL
     | VOID
     ;
listaDeclaradores : declarador (COMA declarador)* ;
declarador : ID inic ;
inic : ASIG opal
     |
     ;

asignacion : expASIG PYC ;
expASIG : ID ASIG opal ;

// ======= Operaciones aritmetico/logicas =======

opal : expOR ;

expOR : expAND o;
o : OR expAND o
  |
  ;

expAND: expIGUALDAD a;
a : AND expIGUALDAD a
  |
  ;

expIGUALDAD: expCOMP i;
i : IGUAL expCOMP i
  | DISTINTO expCOMP i
  |
  ;

expCOMP: exp c;
c : MAYOR exp c
  | MAYORIG exp c
  | MENOR exp c
  | MENORIG exp c
  |
  ;

exp : term e ;
e : SUMA term e
  | RESTA term e
  |
  ;

term : factor t ;
t : MULT factor t
  | DIV factor t
  | MOD factor t
  |
  ;

factor : (NOT | INC | DEC)? factorSufix;
factorSufix : factorCore (INC | DEC)? ;
factorCore : NUMERO
           | CARACTER
           | TRUE_LIT
           | FALSE_LIT
           | ID
           | PA exp PC
           | llamadaFunc
           ;
