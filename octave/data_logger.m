pkg load instrument-control

%@@@@@@@@@@@@@@@@@@@@@@@@@@
% SCRIPT START   
%@@@@@@@@@@@@@@@@@@@@@@@@@@
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
    
    % Optional Flush input and output buffers
    srl_flush(s1);

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
      time_vector(end+1) = (0.0010416667*dataRead) + 0.0;
      dataRead++;
    endwhile  % fin bucle recepción de puerto serie
  
    % cerrar puerto serie
    fclose(s1);
 
%  PROCESAR DATOS 
    % obtener el primer byte válido
    start_byte = -1;
    if (dataRead != 0)
      start_byte = searchHeader(serial_data);
    endif
 
% GUARDAR DATOS
    
% MOSTRAR DATOS
    % mostrar gráfica de los datos obtenidos, siempre y cuando se haya
    % recibido al menos un dato
    if (dataRead != 0)
      plot(time_vector,serial_data);
      xlabel ("time (s)");
      ylabel ("read data");
      title ("EMG data");
    endif
    
    % mostrar tiempo total de la ejecución de script
    printf('Total CPU tic-toc: %f\n', toc(t_start));
    
    disp("FIN");
endif  