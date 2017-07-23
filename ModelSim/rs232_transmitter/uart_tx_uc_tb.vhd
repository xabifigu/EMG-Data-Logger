LIBRARY ieee  ; 
USE ieee.NUMERIC_STD.all  ; 
USE ieee.std_logic_1164.all  ; 
ENTITY uart_tx_uc_tb  IS 
END ; 
 
ARCHITECTURE uart_tx_uc_tb_arch OF uart_tx_uc_tb IS
  -- señales de entrada
  SIGNAL clk      :  STD_LOGIC := '0' ; 
  SIGNAL reset    :  STD_LOGIC := '1' ;
  SIGNAL start    :  STD_LOGIC := '0' ; 
  SIGNAL fintemp  :  STD_LOGIC := '0' ; 
  SIGNAL finbits  :  STD_LOGIC := '0' ; 

  -- señales de salida
  SIGNAL tx_idle  :  STD_LOGIC  ; 
  SIGNAL ldbits   :  STD_LOGIC  ; 
  SIGNAL dectemp  :  STD_LOGIC  ; 
  SIGNAL ldbyte   :  STD_LOGIC  ; 
  SIGNAL decbits  :  STD_LOGIC  ; 
  SIGNAL tx_ack   :  STD_LOGIC  ; 
  SIGNAL despbit  :  STD_LOGIC  ; 
  SIGNAL ldtemp   :  STD_LOGIC  ; 

  COMPONENT uart_tx_uc  
    PORT ( 
      tx_idle   : out STD_LOGIC ; 
      ldbits    : out STD_LOGIC ; 
      dectemp   : out STD_LOGIC ; 
      reset     : in STD_LOGIC ; 
      fintemp   : in STD_LOGIC ; 
      ldbyte    : out STD_LOGIC ; 
      decbits   : out STD_LOGIC ; 
      finbits   : in STD_LOGIC ; 
      tx_ack    : out STD_LOGIC ; 
      clk       : in STD_LOGIC ; 
      despbit   : out STD_LOGIC ; 
      start     : in STD_LOGIC ; 
      ldtemp    : out STD_LOGIC ); 
  END COMPONENT ; 
BEGIN
  DUT  : uart_tx_uc  
    PORT MAP ( 
      tx_idle   => tx_idle  ,
      ldbits    => ldbits  ,
      dectemp   => dectemp  ,
      reset     => reset  ,
      fintemp   => fintemp  ,
      ldbyte    => ldbyte  ,
      decbits   => decbits  ,
      finbits   => finbits  ,
      tx_ack    => tx_ack  ,
      clk       => clk  ,
      despbit   => despbit  ,
      start     => start  ,
      ldtemp    => ldtemp   ) ; 

      -- Generador de señal de reloj
      clk <= not clk after 20 ns;

            -- Proceso principal
      process
      begin
        wait for 100 ns;
        reset <= '0';

        -- loop sobre toda la unidad de control
        for I in 0 to 2 loop 
          wait for 75 ns;
          finbits <= '0';
          fintemp <= '0';
          start   <= '1';
          
          wait for 50 ns;
          start <= '0';
          -- loop de bits
          for I in 0 to 2 loop
            wait for 35 ns;
            fintemp <= '0';
            wait for 75 ns;
            fintemp <= '1';
          end loop;

          finbits <= '1';
        end loop;
  
      end process;   

END ; 

