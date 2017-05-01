LIBRARY ieee  ; 
USE ieee.NUMERIC_STD.all  ; 
USE ieee.std_logic_1164.all  ; 
ENTITY main_block_uc_tb  IS 
END ; 
 
ARCHITECTURE main_block_uc_tb_arch OF main_block_uc_tb IS
  SIGNAL tx_on   :  STD_LOGIC  ; 
  SIGNAL ld_reg   :  STD_LOGIC  ; 
  SIGNAL ld_data   :  STD_LOGIC  ; 
  SIGNAL end_sent_ct   :  STD_LOGIC := '0'  ; 
  SIGNAL tx_ack   :  STD_LOGIC := '0'  ; 
  SIGNAL inc_ch_ct   :  STD_LOGIC  ; 
  SIGNAL clk   :  STD_LOGIC := '0' ; 
  SIGNAL dec_sent_ct   :  STD_LOGIC  ; 
  SIGNAL shift_reg   :  STD_LOGIC  ; 
  SIGNAL ld_sent_ct   :  STD_LOGIC  ; 
  SIGNAL reset   :  STD_LOGIC := '1' ; 
  COMPONENT main_block_uc  
    PORT ( 
      tx_on  : out STD_LOGIC ; 
      ld_reg  : out STD_LOGIC ; 
      ld_data  : out STD_LOGIC ; 
      end_sent_ct  : in STD_LOGIC ; 
      tx_ack  : in STD_LOGIC ; 
      inc_ch_ct  : out STD_LOGIC ; 
      clk  : in STD_LOGIC ; 
      dec_sent_ct  : out STD_LOGIC ; 
      shift_reg  : out STD_LOGIC ; 
      ld_sent_ct  : out STD_LOGIC ; 
      reset  : in STD_LOGIC ); 
  END COMPONENT ; 
BEGIN
  DUT  : main_block_uc  
    PORT MAP ( 
      tx_on   => tx_on  ,
      ld_reg   => ld_reg  ,
      ld_data   => ld_data  ,
      end_sent_ct   => end_sent_ct  ,
      tx_ack   => tx_ack  ,
      inc_ch_ct   => inc_ch_ct  ,
      clk   => clk  ,
      dec_sent_ct   => dec_sent_ct  ,
      shift_reg   => shift_reg  ,
      ld_sent_ct   => ld_sent_ct  ,
      reset   => reset   ) ; 
			

			clk <= not clk after 20 ns;

			process
        begin
        wait for 100 ns;
        reset<='0';
        for I in 0 to 10 loop   
          wait for 100 ns;
          tx_ack<='1';
					wait for 20 ns;
					tx_ack<='0';
					wait for 40 ns;
					end_sent_ct <='1';
          wait for 85 ns;
					tx_ack<='1';
					
        end loop;   
      end process;     
			
END ; 

