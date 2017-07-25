library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adc_one_ch is
	port (
		iCLK			:	in std_logic;
		iRESET		: in std_logic;
		iDOUT			: in std_logic;
		oDIN			:	out std_logic;
		oSCLK			:	out std_logic;
		oCS_OUT_n	:	out std_logic;
		oVALUE		: out std_logic_vector (11 downto 0)	:= (others => '0') ;
		oCURR_CH	: out std_logic_vector (2 downto 0)		:= (others => '0') ;
		iNEXT_CH	:	in std_logic_vector (2 downto 0)
	);
end adc_one_ch;

architecture def of adc_one_ch is
	-- señal auxiliar
	signal	aux			:	std_logic;
	-- número de canal a enviar al ADC
	signal	ch_data	:	std_logic;
	-- siguiente canal a muestrear
	signal	nxt_ch	:	std_logic_vector (2 downto 0);
	-- canal muestreado
	signal	curr_ch	: std_logic_vector (2 downto 0);
	-- contador de flacos ascendentes
	signal	count_r	:	unsigned (3 downto 0) := (others => '0') ;
	-- contador de flacos descendentes
	signal	count_f	:	unsigned (3 downto 0) := (others => '0') ;
	-- valor del ADC a enviar al control
	signal	value		:	std_logic_vector (11 downto 0);
      
begin

-- establecer señal para CS negado el ADC	
	oCS_OUT_n	<=	iRESET;

-- señal de reloj del ADC
	oSCLK		<=	iCLK when iRESET='0' else '1';
	
-- señal para selección del canal
	oDIN		<=	ch_data;
		
-- contador 4 bits (de 0 a 15)	
	process(iCLK, iRESET)
	begin
		if iRESET = '1' then
			count_r <= X"0";
		elsif rising_edge(iCLK) then
			count_r <= count_r + 1;
		end if;
	end process;
	
-- Biestable D para contar los flancos de bajada
	process(iCLK)
	begin
		if falling_edge(iCLK) then
			count_f <= count_r;
		end if;
	end process;

-- Registro desplazamiento para canal
	process(iCLK, iRESET, count_r)
	begin
		if iRESET = '1' then
			ch_data <= '0';
		elsif falling_edge(iCLK) then
			case count_r is
				when X"2" => ch_data <= nxt_ch(2); 
				when X"3" => ch_data <= nxt_ch(1); 
				when X"4" => ch_data <= nxt_ch(0); 
				when others  =>	ch_data <= '0';
			end case;
		end if;
	end process;
	
-- Registro desplazamiento para dato
	process(iCLK, iRESET, count_f)
	begin
		if iRESET = '1' then
			value <= X"000";
		elsif rising_edge(iCLK) then
			case count_f is
				when X"4" => value(11) <= iDOUT; 
				when X"5" => value(10) <= iDOUT; 
				when X"6" => value(9) <= iDOUT; 
				when X"7" => value(8) <= iDOUT; 
				when X"8" => value(7) <= iDOUT; 
				when X"9" => value(6) <= iDOUT; 
				when X"A" => value(5) <= iDOUT; 
				when X"B" => value(4) <= iDOUT; 
				when X"C" => value(3) <= iDOUT; 
				when X"D" => value(2) <= iDOUT; 
				when X"E" => value(1) <= iDOUT; 
				when X"F" => value(0) <= iDOUT; 
				when others => aux <= iDOUT;
			end case;
		end if;
	end process;
	
-- Canal a muestrear
-- Número de canal recibido	
	process(iCLK, iRESET, count_f)
	begin
		if iRESET = '1' then
			nxt_ch <= "000";
		elsif falling_edge(iCLK) then
			if count_r = 1 then
				nxt_ch <= iNEXT_CH; 
			end if;
		end if;
	end process;

-- Registro del número de canal
-- Se necesita un doble registro
-- Cuando re reinicia el contador de flancos descendentes, se almacena
-- el canal a muestrear que se ha recibio. Cuando acaba la recepción
-- de datos actual, los datos obtenidos son del canal previo (no del
-- nuevo canal que se ha recibido), por ello se ha de enviar el canal
-- anterior junto a los datos del ADC. La siguiente vez que se reinicie
-- el contador, comenzará la recepción de datos del canal que se recibió.
-- Por ello hace falta el doble registro que almacene el canal que
-- se ha muestreado antes de recibir el nuevo
	process(iCLK, iRESET, count_f)
	begin
		if iRESET = '1' then
			curr_ch <= "000";
		elsif rising_edge(iCLK) then
			if count_f = 0 then
				curr_ch <= nxt_ch;
				oCURR_CH <= curr_ch;
			end if;
		end if;
	end process;

	-- Registro datos ADC a enviar
	process(iCLK, count_f)
	begin
		if rising_edge(iCLK) then
			if count_f = 0 then
				oVALUE <= value;  
			end if;
		end if;
	end process;

end def; 