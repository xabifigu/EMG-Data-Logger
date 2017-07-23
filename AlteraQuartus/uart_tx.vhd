library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity uart_tx is
	port (
		iRESET		:	in std_logic;
		iCLK			: in std_logic;
		iDATA			: in std_logic_vector(7 downto 0);
		iSTART_TX	: in std_logic;
		oTX_OUT		: out std_logic; 
		oTX_ACK		: out std_logic
	);
end uart_tx;

architecture def of uart_tx is
	type estado is (e0,e1,e2,e3,e4);
	signal ep,es: estado;
--	constant temp_value	: unsigned(12 downto 0):="0000110110010"; -- 434 (115200 bauds)
	constant temp_value	: unsigned(12 downto 0):="1010001010000"; -- 5200 (9600 bauds)
--	constant temp_value	: unsigned(12 downto 0):="0000000000011"; -- 3 -> constante para test
	constant num_bits		:	unsigned(3 downto 0):="1010"; -- 10
--	constant num_bits		:	unsigned(3 downto 0):="0010"; -- 2 -> constante para test
	signal fintemp	:	std_logic; 
	signal finbits	:	std_logic;
	signal ldtemp		:	std_logic;
	signal ldbits		:	std_logic;
	signal ldbyte		:	std_logic;
	signal dectemp	:	std_logic;
	signal despbit	:	std_logic;
	signal decbits	:	std_logic;
	signal temp			:	unsigned(12 downto 0);
	signal bytereg	:	std_logic_vector(9 downto 0);
	signal bits			:	unsigned(3 downto 0);
	signal start		:	std_logic;
	signal tx_ack		:	std_logic;
	signal tx_idle	:	std_logic;

	begin

	process (iCLK, iRESET)
		begin
			if iRESET = '1' then ep <= e0;
			elsif rising_edge(iCLK)  
				then ep <= es; 
			end if;  
	end process;  

	----UNIDAD DE CONTROL-----
	--------------------------  
	process (ep, start, fintemp, finbits)
	begin
		case ep is
			when e0 =>	if start='0' then es <= e0;
									else es <= e1;
									end if;
			when e1 => 	es <= e2;
			when e2 => 	if fintemp = '0' then es <= e2;
									elsif finbits = '1' then es <= e4;
									else es <= e3;
									end if;
			when e3 => 	es <= e2;
			when e4 => 	es <= e0;
		end case;
	end process;

	tx_idle	<= '1' when ep = e0 or ep = e4 else '0';	
	ldtemp	<= '1' when ep = e1 or ep = e3 else '0';
	ldbits	<= '1' when ep = e1 else '0';
	ldbyte	<= '1' when ep = e1 else '0';
	dectemp	<= '1' when ep = e2 else '0';
	despbit	<= '1' when ep = e3 else '0';
	decbits	<= '1' when ep = e3 else '0';
	tx_ack	<= '1' when ep = e4 else '0';

	----UNIDAD DE PROCESO-----
	--------------------------
	--Biestable D
	process (iCLK, iRESET, iSTART_TX)
		begin
			if iRESET = '1' then
				start <= '0';
			elsif rising_edge(iCLK) then  
				if iSTART_TX='1' then start<='1'; 
				else start<='0'; 
				end if;  
			end if; 
	end process;  

	-- contador de tiempo
	process (iCLK, ldtemp, dectemp)
	begin
		if rising_edge(iCLK) then 
			if ldtemp='1' then temp<=temp_value;
			elsif dectemp='1' then temp<=temp-1;
			end if;
		end if;
	end process;
	fintemp<='1' when temp=0 else '0';

	-- registro para sacar los bits a enviar, para pasar de paralelo a serie
	process (iCLK, iRESET, ldbyte, despbit)
	begin
		if iRESET = '1' then
				bytereg <= (others=>'0');
		elsif rising_edge(iCLK) then 
			if ldbyte='1' then
				bytereg(9) <= '1'; -- stop bit
				bytereg(8 downto 1) <= iDATA; -- dato
				bytereg(0) <= '0'; -- start bit
			elsif despbit='1' then 
				for I in 0 to 8 loop
					bytereg(I)<=bytereg(I+1);
				end loop;
			end if;
		end if;
	end process;

	--multiplexor para poner la salida a '1' cuando la linea este libre
	oTX_OUT <= '1' when tx_idle = '1' else bytereg(0);
	
	oTX_ACK <= tx_ack;

	-- contador de bits enviados
	process (iCLK, ldbits, decbits)
	begin
		if rising_edge(iCLK) then
			if ldbits='1' then bits<=num_bits;
			elsif decbits='1' then bits<=bits-1;
			end if;
		end if;
	end process;
	finbits<='1' when bits=0 else '0';


end def;