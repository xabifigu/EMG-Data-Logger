library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity uart_tx_uc is
	port (
    clk				:	in std_logic;
		reset			: in std_logic;
		start		  :	in std_logic;
		fintemp		: in std_logic;
		finbits		: in std_logic;
    tx_idle	  : out std_logic;
    ldtemp	  : out std_logic;
    ldbits	  : out std_logic; 
    ldbyte	  : out std_logic; 
    dectemp	  : out std_logic; 
    despbit	  : out std_logic; 
    decbits	  : out std_logic; 
    tx_ack	  : out std_logic
	);
end uart_tx_uc;

architecture def of uart_tx_uc is
	type estado is (e0,e1,e2,e3,e4);
  signal ep,es: estado;

	begin

	process (clk, reset)
		begin
			if reset = '1' then ep <= e0;
			elsif rising_edge(clk)  
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


end def;