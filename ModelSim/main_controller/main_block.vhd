library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity main_block is
	port (
		iCLK		:	in std_logic;
		iRESET	: in std_logic;
		iTX_ACK	: in std_logic;
		iVALUE	: in std_logic_vector (11 downto 0);
		iADC_CH	:	in std_logic_vector (2 downto 0);
		oTX_ON	:	out	std_logic;
		oBYTE		:	out std_logic_vector (7 downto 0);
		oNEXT_CH:	out std_logic_vector (2 downto 0)
	);
end main_block;

architecture def of main_block is
	-- SEÑALES INTERNAS
	-- señales de unidad de control
	type estado is (e0,e1,e2,e3,e4);
	signal 		ep,es				: estado;
	
	-- registro del canal muestreado
	signal		adc_ch			:	std_logic_vector (2 downto 0);
	signal  	ld_adc_ch		:	std_logic;
	
	-- registro del valor del ADC
	signal		adc_data		:	std_logic_vector (11 downto 0);
	signal  	ld_data			:	std_logic;

	-- contador ascendente de número de canal
	constant	ch_init			:	unsigned (2 downto 0) := "000";
	signal		ch_ct				:	unsigned (2 downto 0);
	signal		ld_ch_ct		:	std_logic;
	signal		inc_ch_ct		:	std_logic;
	
	-- contador descendente de bytes enviados por uart
	constant	sent_init		: unsigned (1 downto 0) := "10";
	signal		sent_ct			:	unsigned (1 downto 0);
	signal		ld_sent_ct	:	std_logic;
	signal		dec_sent_ct	:	std_logic;
	signal		end_sent_ct	:	std_logic;

	-- Resgitro desplazamiento de byte
	signal		ld_reg			: std_logic;
	signal		shift_reg		:	std_logic;
	-- signal		byte_to_send:	std_logic_vector (7 downto 0);
	signal		bits_to_send:	std_logic_vector (15 downto 0);
	
	-- Otras señales
	signal		tx_on				:	std_logic;
	signal		tx_ack			:	std_logic;
	
begin

	-- control de reset 
	process (iCLK, iRESET)
		begin
			if iRESET = '1' then ep <= e0;
			elsif rising_edge(iCLK) 
				then ep <= es; 
			end if;  
	end process;  
	
	----UNIDAD DE CONTROL-----
	--------------------------  
	process (ep, tx_ack, end_sent_ct)
	begin
		case ep is
			when e0 =>	es <= e1;
			when e1 =>	es <= e2;
			when e2 =>	es <= e3;
			when e3 =>	if tx_ack = '0' then es <= e3;
									elsif end_sent_ct = '0' then es <= e4;
									else es <= e1;
									end if;
			when e4 => 	es <= e3;
		end case;
	end process;

	ld_ch_ct		<= '1' when ep = e0 else '0';
	ld_data			<= '1' when ep = e1 else '0';
	ld_adc_ch		<= '1' when ep = e1 else '0';
	inc_ch_ct		<= '1' when ep = e1 else '0';
	ld_sent_ct	<= '1' when ep = e1	else '0';	
	ld_reg			<= '1' when ep = e2 else '0';
	tx_on				<= '1' when ep = e3 else '0';
	shift_reg		<= '1' when ep = e4 else '0';
	dec_sent_ct	<= '1' when ep = e2 or ep = e4 else '0';
	
	----UNIDAD DE PROCESO-----
	-------------------------- 
	
	--Biestable D
	process (iCLK, iTX_ACK)
		begin
			if rising_edge(iCLK) then  
				if iTX_ACK = '1' then tx_ack <= '1'; 
				else tx_ack <= '0'; 
				end if;  
			end if; 
	end process;  
	
	------------------------
	-- Registro dato de ADC
	process (iCLK, ld_data)
		begin
			if rising_edge(iCLK) then  
				if ld_data = '1' then 
					adc_data <= iVALUE; 
				end if;  
			end if; 
	end process; 
	
	------------------------
	-- Registro canal muestreado
	process (iCLK, ld_adc_ch)
		begin
			if rising_edge(iCLK) then  
				if ld_adc_ch = '1' then adc_ch <= iADC_CH; 
				end if;  
			end if; 
	end process; 
	
	-------------------------
	-- Contador ascendente para número de canal
		-- Contador de 0 a 7, cuando llega a 7, 
		-- hace overflow y vuelve a empezar en 0
	process (iCLK, ld_ch_ct, inc_ch_ct)
		begin
			if rising_edge(iCLK) then  
				if ld_ch_ct = '1' then ch_ct <= ch_init; 
				elsif inc_ch_ct = '1' then ch_ct 	<= ch_ct + 1;
				end if;  
			end if; 
	end process;  
	
	-- próximo canal a muestrear
	oNEXT_CH <= std_logic_vector(ch_ct);

	---------------------------------
	-- Contador descendente para bytes enviados
	process (iCLK, ld_sent_ct, dec_sent_ct)
		begin
			if rising_edge(iCLK) then   
				if ld_sent_ct = '1' then sent_ct <= sent_init; 
				elsif dec_sent_ct = '1' then sent_ct <= sent_ct - 1;
				end if;  
			end if; 
	end process;  

	end_sent_ct<= '1' when sent_ct = 0 else '0'; 
	
	---------------------------------
	-- Registro de desplazamiento izquierda (16 bits)
		-- Byte a enviar por UART.
		-- Primero envía byte más significativo.
	process (iCLK, ld_reg, shift_reg)
	begin
		if rising_edge(iCLK) then 
			if ld_reg = '1' then	
				-- bit 15:			irrelevante
				-- bit 12..14:	canal muestreado
				-- bit 0..11:		valor ADC
				bits_to_send (15) <= '0';
				bits_to_send (14 downto 12) <= adc_ch;
				bits_to_send (11 downto 0)	<= adc_data;
			elsif shift_reg = '1' then 
				for I in 0 to 7 loop
					bits_to_send(I+8) <= bits_to_send(I);
				end loop;
			end if;
		end if;
	end process;

	-- byte a enviar por uart
	oBYTE <= bits_to_send (15 downto 8); 
	
	-- byte_to_send (7 downto 0) <= bits_to_send (15 downto 8); 
	
	-- -- byte a enviar por uart
	-- oBYTE <= byte_to_send;
	
	-- UART puede enviar
	oTX_ON <= tx_on;
	
end def; 