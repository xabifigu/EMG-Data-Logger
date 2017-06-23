pkg load instrument-control

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%       FUNCIONES PUERTO SERIE      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function serialPortInit(s1)
  
%    s1 = serial("\\\\.\\COM5")   % Open the port
%    pause(1);                    % Optional wait for device to wake up 
    
    % Set the port parameters
    % set(s1, 'baudrate', 9600);     % 9600
		set(s1, 'baudrate', 115200);     % 9600
    set(s1, 'bytesize', 8);        % 5, 6, 7 or 8
    set(s1, 'parity', 'n');        % 'n' or 'y'
    set(s1, 'stopbits', 1);        % 1 or 2
    set(s1, 'timeout', 5);         % 0.5 Seconds
        
    % Optional commands, these can be 'on' or 'off'
    set(s1, 'requesttosend', 'off');      % Sets the RTS line to off
    set(s1, 'dataterminalready', 'off'); % Sets the DTR line to off
    
    % Optional Flush input and output buffers
    srl_flush(s1);
    
endfunction

%function serialPortStop(s1)
%    % cerrar puerto serie
%    fclose(s1);
%endfunction


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%       FUNCIONES TRATA DE DATOS       %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ret = getHighNibbleFromByte(data)
  x = bitand(data, 0xF0);
  ret = bitshift(x,-4);
endfunction

function ret = getLowNibbleFromByte(data)
  ret = bitand(data, 0x0F);
endfunction

function ret = bytes2Word(highByte, lowByte)
	aux = bitshift(uint16(highByte), 8);
  ret = bitor(aux, uint16(lowByte));
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

%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
% SCRIPT START   
%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
MAX_CHANNELS = 8;

% function getADCData()
% limpiar variables
clear;

% guardar tiempo de inicio del script
%%t_start = tic();
printf('Start CPU tic-toc: %f', tic());

% INICIALIZAR PUERTO SERIE
% comprobar si los puertos serie tiene algún problema
if (exist("serial") != 3)
    % error en los puertos serie
    disp("No Serial Support");
else
    % Puertos series correctos
    
    % Instantiate the Serial Port
    % Naturally, set the COM port # to match your device
    % Use this crazy notation for any COM port number: 1 - 255
    s1 = serial("\\\\.\\COM5")   % Open the port
    pause(1);                    % Optional wait for device to wake up 
    
		serialPortInit(s1);

% OBTENER DATOS         
    % inicializar contador de bytes recibidos
    dataRead = 0;
    t_start = tic()+0.0;
    % bucle de recepción de datos
    while (1)
      % se intenta optener un dato del puerto series, si
      % no se recibe un dato nuevo pasao el tiempo definido por 'timeout',
      % se genera un evento, el cual termina con la recepción de datos
      try
        % obtener 1 byte del puerto serie y guardarlo tras la última
        % posición del vector de datos (append)
        % '0.0' indica que el dato a almacenar es double
        serial_data(end+1) = srl_read(s1,1) + 0.0;
%          a=fread(s1,1,'char');
%        horzcat(serial_data, srl_read(sl,10));
      catch
        disp("X.F.: Serial Port stopped");
        break
      end_try_catch
      % almacenar el tiempo en el cual se ha obtenido el dato.
      % Se guarda tras la última posición del vector de tiempo(append)
%      time_vector(end+1) = toc(t_start) + 0.0;
      time_vector(end+1) = (0.086805555*dataRead) + 0.0;
      dataRead++;
    endwhile  % fin bucle recepción de puerto serie
  
    % cerrar puerto serie
    fclose(s1);
 
%  PROCESAR DATOS 
    
    start_byte = -1;
    if (dataRead != 0)
			% obtener el primer byte válido
      start_byte = searchHeader(serial_data);
			
			% separa los datos según el canal leído
			index = start_byte;
			while (index < dataRead)
				currentData = serial_data(index:index+1);
				[ch_nb, adc_val] = getProcessReadData(currentData);
				% los índices empiezan en 1, por lo que al número de canal se le sumará uno, 
				% para evitar tener 0 como índice
				ch_array {ch_nb+1}(end+1) = adc_val;
				time_array {ch_nb+1}(end+1) = time_vector(index);
				index += 2;
			endwhile
    endif
		 
% GUARDAR DATOS
		% los datos se guardan en CSV:
		%	Columna 0: tiempo
		% Columna 1: valores ADC
    if (dataRead != 0)
			for i = 1:8
				M = [time_array{i};double(ch_array{i})];
				MT = M';
				file_name = strcat("data_channel_", num2str(i-1), ".csv");
				csvwrite(file_name,MT);
			endfor
		endif
		
% MOSTRAR DATOS
    % mostrar gráfica de los datos obtenidos, siempre y cuando se haya
    % recibido al menos un dato
    if (dataRead != 0)
			% una misma ventana para todos los canales
			% figure(1);
			% for i = 1:8
				% subplot (8, 1, i);
				% plot(time_array{i},ch_array{i})
				% xlabel ("time (s)");
				% ylabel ("value");
				% title(strcat("channel", num2str(i-1)));
				% % title ("EMG data channel");
			% endfor
				
			% un ventana por cada canal
			for i = 1:8
				figure(i);
				plot(time_array{i},ch_array{i});
				xlabel ("time (ms)");
				ylabel ("value");
				title(strcat("channel", num2str(i-1)));
				% title ("EMG data channel");
			endfor
		
    endif
    
    % mostrar tiempo total de la ejecución de script
    printf('Total CPU tic-toc: %f\n', toc(t_start));
    
    disp("FIN");
endif  
% endfunction 



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%       FUNCIONES PUERTO SERIE      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%function serialPortInit(s1)
%    % Set the port parameters
%    set(s1, 'baudrate', 9600);     % 9600
%    set(s1, 'bytesize', 8);        % 5, 6, 7 or 8
%    set(s1, 'parity', 'n');        % 'n' or 'y'
%    set(s1, 'stopbits', 1);        % 1 or 2
%    set(s1, 'timeout', 5);         % 0.5 Seconds
%        
%    % Optional commands, these can be 'on' or 'off'
%    set(s1, 'requesttosend', 'off');      % Sets the RTS line to off
%    set(s1, 'dataterminalready', 'off'); % Sets the DTR line to off
%endfunction