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

NUMERO : DIGITO+ ;

INT : 'int' ;
DOUBLE : 'double' ;
WHILE : 'while' ;
IF : 'if' ;
ELSE : 'else' ;
FOR : 'for' ; 

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

iwhile : WHILE PA opal PC instruccion ;
               // deberias ser un comp antes que opal

iif : IF PA opal PC instruccion ielse ;
ielse : ELSE instruccion 
      | 
      ;

//ifor : FOR PA "asignacion" PYC "comp" PYC "opal" PYC PC instruccion ;

declaracion : arranque listavar PYC ;

listavar : COMA ID listavar 
         | COMA asignacion listavar 
         |
         ;

arranque : tipo asignacion
         | tipo ID
         ;

tipo : INT
     | DOUBLE
     ;

asignacion : ID ASIG opal ;

opal : NUMERO
     | ID
     ;

