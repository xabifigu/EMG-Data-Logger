LIBRARY ieee  ; 
USE ieee.NUMERIC_STD.all  ; 
USE ieee.std_logic_1164.all  ; 
ENTITY main_block_uc_tb  IS 
END ; 
 
ARCHITECTURE main_block_uc_tb_arch OF main_block_uc_tb IS
  -- señales de entrada
  SIGNAL reset        :  STD_LOGIC  := '1' ; 
  SIGNAL clk          :  STD_LOGIC  := '0' ;
  SIGNAL end_sent_ct  :  STD_LOGIC  := '0' ; 
  SIGNAL tx_ack       :  STD_LOGIC  := '0' ;

  -- señales de salida
  SIGNAL ld_ch_ct     :  STD_LOGIC  ; 
  SIGNAL tx_on        :  STD_LOGIC  ; 
  SIGNAL ld_sent_ct   :  STD_LOGIC  ; 
  SIGNAL ld_data      :  STD_LOGIC  ; 
  SIGNAL ld_adc_ch    :  STD_LOGIC  ; 
  SIGNAL inc_ch_ct    :  STD_LOGIC  ; 
  SIGNAL shift_reg    :  STD_LOGIC  ; 
  SIGNAL dec_sent_ct  :  STD_LOGIC  ; 
  SIGNAL ld_reg       :  STD_LOGIC  ; 

  COMPONENT main_block_uc  
    PORT ( 
      ld_ch_ct      : out STD_LOGIC ; 
      tx_on         : out STD_LOGIC ; 
      ld_sent_ct    : out STD_LOGIC ; 
      ld_data       : out STD_LOGIC ; 
      ld_adc_ch     : out STD_LOGIC ; 
      shift_reg     : out STD_LOGIC ; 
      dec_sent_ct   : out STD_LOGIC ; 
      ld_reg        : out STD_LOGIC ; 
      inc_ch_ct     : out STD_LOGIC ; 
      reset         : in STD_LOGIC  ; 
      clk           : in STD_LOGIC  ; 
      tx_ack        : in STD_LOGIC  ; 
      end_sent_ct   : in STD_LOGIC  ); 
  END COMPONENT ; 
BEGIN
  DUT  : main_block_uc  
    PORT MAP ( 
      ld_ch_ct      => ld_ch_ct  ,
      tx_on         => tx_on  ,
      reset         => reset  ,
      ld_sent_ct    => ld_sent_ct  ,
      ld_data       => ld_data  ,
      ld_adc_ch     => ld_adc_ch  ,
      clk           => clk  ,
      inc_ch_ct     => inc_ch_ct  ,
      tx_ack        => tx_ack  ,
      shift_reg     => shift_reg  ,
      dec_sent_ct   => dec_sent_ct  ,
      ld_reg        => ld_reg  ,
      end_sent_ct   => end_sent_ct   ) ; 

      -- Generador de señal de reloj
      clk <= not clk after 20 ns;

      -- Proceso principal
      process
      begin
        wait for 100 ns;
        reset <= '0';

        -- loop sobre toda la unidad de control
        for I in 0 to 2 loop 
          -- loop de envío de bytes
          for I in 0 to 2 loop
            wait for 40 ns;
            tx_ack <= '0';
            wait for 225 ns;
            tx_ack <= '1';
          end loop;

          end_sent_ct <= '1';

          wait for 50 ns;
          end_sent_ct <= '0';
          tx_ack <= '0';
        end loop;

      end process;   

END ; 

