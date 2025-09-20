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

NUMERO : DIGITO+ ;

INT : 'int' ;
DOUBLE : 'double' ;
WHILE : 'while' ;
IF : 'if' ;
ELSE : 'else' ;
FOR : 'for' ; 
RETURN : 'return';

ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;

WS : [ \n\r\t] -> skip ;
OTRO : . ;

// s : ID     {print("ID ->" + $ID.text + "<--") }         s
//   | NUMERO {print("NUMERO ->" + $NUMERO.text + "<--") } s
//   | OTRO   {print("Otro ->" + $OTRO.text + "<--") }     s
//   | EOF
//   ;

// s : PA s PC s
//   |
//   ;

s : instrucciones EOF ;

instrucciones : instruccion instrucciones
              |
              ;

instruccion : asignacion PYC
            | declaracion
            | iwhile
            | bloque
            | iif
            ;

bloque : LLA instrucciones LLC ;

iwhile : WHILE PA comp PC instruccion ;

comp : opal comp opal
     | MA
     | ME
     | ASIG ASIG
     | MA ASIG
     | ME ASIG
     | DIS
     ;

iif : IF PA opal PC instruccion ielse ;

ielse : ELSE instruccion 
      | 
      ;

ifor : FOR PA declaracion PYC comp PYC opal PYC PC bloque ;

declaracion : tipo arranque listavar PYC ;

listavar : COMA ID listavar 
         | COMA asignacion listavar 
         |
         ;
//Tipo adentro??
arranque : asignacion
         | ID
         ;

tipo : INT
     | DOUBLE
     ;

asignacion : ID ASIG opal ;

opal : NUMERO
     | ID
     ;

return : RETURN opal PYC;