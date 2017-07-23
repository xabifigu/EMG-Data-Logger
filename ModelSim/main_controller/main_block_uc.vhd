library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity main_block_uc is
	port (
	  clk					:	in std_logic;
		reset				: in std_logic;
		ld_ch_ct		:	out std_logic;
		ld_data			:	out std_logic;
		ld_adc_ch		:	out std_logic;
		inc_ch_ct		:	out std_logic;
		ld_sent_ct	:	out std_logic;	
		ld_reg			:	out std_logic;
		tx_on				:	out std_logic;
		shift_reg		:	out std_logic;
		dec_sent_ct	:	out std_logic;
		tx_ack			: in std_logic;
		end_sent_ct	:	in std_logic
	);
end main_block_uc;

architecture def of main_block_uc is
	type estado is (e0,e1,e2,e3,e4);
	signal ep,es	: estado;
	
begin

	process (clk, reset)
		begin
			if reset= '1' then ep<=e0;
			elsif rising_edge(clk) 
				then ep<=es; 
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
	
end def; 