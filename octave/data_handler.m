%% Función: synchSerialPort
%% Detalles: sincroniza por primera vez los datos recibidos parallel
%%           detectar dónde comienzan los datos de cada canal
%% Argumentos: ---
%% Return: Devuelve qué byte es el primero de cada canal
%%         0 -> primer byte en bytes par
%%         1 -> primer byte en bytes impares
%%         -1 -> error de sincronización
%function retval = synchSerialPort
%  retval = -1;
%  
%endfunction


function ret = getHighNibbleFromByte(data)
  x = bitand(data, 0xF0);
  ret = bitshift(x,-4);
endfunction

function ret = getLowNibbleFromByte(data)
  ret = bitand(data, 0x0F);
endfunction

function ret = bytes2Word(highByte, lowByte)
	aux = bitshift(highByte, 8);
  ret = bitor(aux, lowByte);
endfunction

function	[ch, value] = getProcessReadData(in_data)
	ch = getHighNibbleFromByte(in_data(1));
	
	aux = getLowNibbleFromByte(in_data(1));
	value = bytes2Word(aux,in_data(2));
endfunction

function  data_start = searchHeader(in_data)
    % Formato de datos lo componen dos bytes XY0 Y1Y2
    %       X = número de canal (4 bits)
    %       Y0Y1Y2 = dato del canal (12 bits)
    % Primero hay que determinar qué bytes contienen la 
    % cabecera de cada canal: pares o impares 
    data_start = -1;
    
    headersFound = false;
    index = 1;
    expected_ch = 0;
    ch_counter = 0;
    start_search = false;
    
    %  Bucle para encontrar el patrón correcto
    %  Se ejecutará hasta encontrar la secuencia buscada 18 veces, o 
    %  hasta que se hayan leído 50 bytes sin encontrar la cabecera 
    while ((ch_counter < (18)) && (index <= 50)) % hay que leer el primer canal 2 veces
      while (start_search != true)
        expected_ch = getHighNibbleFromByte(in_data(index));
        if (expected_ch < 8)
          % posible canal encontrado
          start_search = true;
          data_start = index;  % se guarda el primer dato del cuál hay que empezar a leer
          % se almacena el siguinte canal que se espera encontrar
          if (expected_ch == (8-1))
            expected_ch = 0;
          else
            expected_ch++;
          endif
          index += 2;   % se incrementa el índice en dos (se busca cabecera/num canal)
          ch_counter++; % se incrementa el contados de cabeceras encontradas
        else
          % posible canal no encontrado, comprobar siguiente byte
          index++;    
        endif
      endwhile
      
      % Bucle hasta encontrar todas las cabeceras esperadas o encontrar un error
      while ((ch_counter < (18)) && (ch_counter != 0))
        if (expected_ch == getHighNibbleFromByte(in_data(index)))
          % el canal encontrado es el esperado
          index += 2;     % se incrementa el índice en dos (se busca cabecera/num canal)
          ch_counter++;   % se incrementa el contados de cabeceras encontradas 
          % se almacena el siguinte canal que se espera encontrar 
          if (expected_ch == (8-1))
            expected_ch = 0;
          else
            expected_ch++;
          endif
        else
          % se ha detectado un error en la trama
          % se resetean el contador y se decrementa el índice, ya que el
          % byte correcto puede haberse saltado
          expected_ch = 0;
          ch_counter = 0;
          index--;
          start_search = false;
        endif
      endwhile     
    endwhile
    
    if (ch_counter >= (18))
      disp('Patron correcto!');
    else
      disp('Patron no encontrado');
      data_start = -1;  % no se ha encontrado el patrón, se devuelve -1
    endif
endfunction