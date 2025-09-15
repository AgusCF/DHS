grammar compiladores;

//Tipos de dato
INT : 'int' ;
FLOAT : 'float' ;
STRING : 'string' ;
CHAR : 'char' ;
BOOLEAN : 'boolean' ;
DOUBLE : 'double' ;

//Palabras recervadas
WHILE : 'while' ;
RETURN : 'return' ;
IF : 'if' ;
ELSE : 'else' ;
FOR : 'for' ;


//Operadores y simbolos
ASIGN : '=' ;
PLUS : '+';
MINUS : '-';
MULT : '*';
DIV : '/';
COMMA : ',';
PYC : ';' ;
PA : '(' ;
PC : ')' ;
LLA : '{' ;
LLC : '}' ;
OPAL : '>' | '<' | '>=' | '<=' | '==' | '!=' ;

//Ignorar espacios en blanco
WS : [ \t\r\n]+ -> skip ;


fragment LETRA : [A-Za-z] ;
fragment DIGITO : [0-9] ;

NUMERO : DIGITO+ ;
OTRO : . ;
ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;



  
  
  programa : instrucciones EOF ;
  instrucciones : instruccion instrucciones | ;
  instruccion : asignacion | declaracion | iwhile | bloque | iif ; //Instrucciones Simples
  bloque : LLA instrucciones LLC ; //Instrucciones Compuestas

  //Estructuras de control
  iwhile : WHILE PA opal PC LLA instruccion LLC ;
  
  //------------------------TARMINAR------------------------
  ifor: FOR PA PYC opal PYC PC instruccion ;  // usar el ++i es mas optimizado --> for (i=0; i<10; ++i)

    //IF con ELSE opcional
  iif : IF PA opal PC LLA instruccion LLC ielse ; // (ELSE instruccion)? No seria recursivo.
  ielse: ELSE instruccion | ; //El tener " algo | ; " hace que sea opcional. (Puede o no estar)

  declaracion : tipo ID PYC ;
  tipo : INT | FLOAT | STRING | CHAR | BOOLEAN | DOUBLE ;
  asignacion : ID ASIGN opal PYC ;  
  opal : NUMERO | ID ;

  /*
  s : ID     {print("ID ->" + $ID.text + "<--") }         s
  | NUMERO {print("NUMERO ->" + $NUMERO.text + "<--") } s
  | OTRO   {print("Otro ->" + $OTRO.text + "<--") }     s
  | EOF
  ; */