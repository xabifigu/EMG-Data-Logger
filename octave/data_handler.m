% Función: synchSerialPort
% Detalles: sincroniza por primera vez los datos recibidos parallel
%           detectar dónde comienzan los datos de cada canal
% Argumentos: ---
% Return: Devuelve qué byte es el primero de cada canal
%         0 -> primer byte en bytes par
%         1 -> primer byte en bytes impares
%         -1 -> error de sincronización
function retval = synchSerialPort
  retval = -1;
  
endfunction