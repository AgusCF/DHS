grammar compiladores;

fragment LETRA : [A-Za-z] ;
fragment DIGITO : [0-9] ;

PA : '(' ;
PC : ')' ;
LLA : '{' ;
LLC : '}' ;
PYC : ';' ;
ASIG : '=' ;
COMA : ',' ;
MA : '>';
ME : '<';
DIS: '!=';
SUMA : '+' ;
RESTA : '-' ;
MULT : '*' ;
DIV : '/' ;
MOD : '%' ;

NUMERO : DIGITO+ ;

VOID : 'void' ;
INT : 'int' ;
DOUBLE : 'double' ;
FLOAT : 'float' ;
WHILE : 'while' ;
IF : 'if' ;
ELSE : 'else' ;
FOR : 'for' ; 
RETURN : 'return';

ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;

WS : [ \n\r\t] -> skip ;
OTRO : . ;



s : instrucciones EOF ;

instrucciones : instruccion instrucciones
              |
              ;

instruccion : asignacion PYC
            | declaracion
            | iwhile
            | bloque
            | iif
            | ifor
            | return
            | prototipo_funcion
            | declaracion_funcion
            ;

bloque : LLA instrucciones LLC ;

iwhile : WHILE PA comp PC instrucciones ;

comp : opal comp opal
     | MA
     | ME
     | ASIG ASIG
     | MA ASIG
     | ME ASIG
     | DIS
     ;

iif : IF PA comp PC instruccion ielse ;

ielse : ELSE instruccion 
      | 
      ;

ifor : FOR PA declaracion PYC comp PYC opal PYC PC instruccion;

declaracion : tipo arranque listavar PYC ;

listavar : COMA ID listavar 
         | COMA asignacion listavar 
         |
         ;

arranque : asignacion
         | ID
         ;

tipo : INT
     | DOUBLE
     | FLOAT
     ;

asignacion : ID ASIG opal ;

opal : exp ;

return : RETURN opal PYC;

//----------------------22/9---------------------- El orden de las reglas. Leer primero + - ; luego ; * / ; y asi sucesivamente
//Exp = sumadores y restadores
exp : term exp1 ; //exp1 = e
exp1 : SUMA term exp1
     | RESTA term exp1
     | 
     ;
//Term = multiplicadores y divisores
term : factor term1 ; //term1 = t
term1 : MULT factor term1
      | DIV factor term1
      | MOD factor term1
      | 
      ;
//Factor = identificadores y literales
factor : NUMERO
        | ID
        | llamada_funcion //No la dio. La tenemos qeue hacer nosotros
        | PA exp PC
        ;
//Faltan aritmeticas logicas

//Joaco: Agus mas arriba hice un "comp" que es el comparador

//LLAMADA A FUNCION DE COPAILOT. VER
llamada_funcion : ID PA lista_argumentos PC
                ;

lista_argumentos : exp (COMA exp)* //Creo que no se podia usar (COMA exp)* ~~~ CREO QUE ESO ES "listavar"
                 | 
                 ;

prototipo_funcion : (tipo | VOID) ID PA lista_parametros PC PYC ;

lista_parametros : tipo ID (COMA tipo ID)* |
                 ;

declaracion_funcion : tipo ID PA lista_parametros PC bloque ; 

