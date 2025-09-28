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
AND : '&&' ;
OR : '||' ;
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

iwhile : WHILE PA opal PC instrucciones ;

iif : IF PA opal PC instrucciones ielse ;

ielse : ELSE instruccion 
      | 
      ;

ifor : FOR PA (declaracion | asignacion PYC | PYC) opal PYC asignacion PC instruccion ;

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

return : RETURN opal PYC;

opal : exp
     | expOR
     ;

//ExpOR = operaciones OR
expOR : expAND or ;
or : OR expAND or
   |
   ;

//ExpAND = operaciones AND
expAND : expIGUAL and ;
and : AND expIGUAL and
    |
    ;

//ExpIGUAL = igualdad y desigualdad
expIGUAL : expCOMP ig ;
ig : ASIG ASIG expCOMP ig
   | DIS expCOMP ig
   |
   ;

//ExpCOMP = comparadores
expCOMP : exp comp ;
comp : ME exp comp
     | MA exp comp
     | ME ASIG exp comp
     | MA ASIG exp comp
     |
     ; 

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

//Declaracion, llamada y prototipo de funciones
llamada_funcion : ID PA lista_argumentos PC
                ;

lista_argumentos : exp (COMA exp)* 
                 | 
                 ;

prototipo_funcion : (tipo | VOID) ID PA lista_parametros PC PYC ;

lista_parametros : tipo ID (COMA tipo ID)* |
                 ;

declaracion_funcion : tipo ID PA lista_parametros PC bloque ; 

