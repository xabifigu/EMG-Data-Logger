LIBRARY ieee  ; 
USE ieee.NUMERIC_STD.all  ; 
USE ieee.std_logic_1164.all  ; 
ENTITY uart_tx_tb  IS 
END ; 
 
ARCHITECTURE uart_tx_tb_arch OF uart_tx_tb IS
  -- señales de entrada
  SIGNAL iRESET     :  STD_LOGIC := '1' ; 
  SIGNAL iSTART_TX  :  STD_LOGIC := '0' ; 
  SIGNAL iDATA      :  std_logic_vector (7 downto 0) := "00110011"; -- := (others=>'0') ; 
  SIGNAL iCLK       :  STD_LOGIC := '0' ; 

  -- señales de salida
  SIGNAL oTX_ACK    :  STD_LOGIC  ; 
  SIGNAL oTX_OUT    :  STD_LOGIC  ; 

	-- señales internas
	SIGNAL TEMP 			: integer;

  COMPONENT uart_tx  
    PORT ( 
      iRESET      : in STD_LOGIC ; 
      oTX_ACK     : out STD_LOGIC ; 
      oTX_OUT     : out STD_LOGIC ; 
      iSTART_TX   : in STD_LOGIC ; 
      iDATA       : in std_logic_vector (7 downto 0) ; 
      iCLK        : in STD_LOGIC ); 
  END COMPONENT ; 
BEGIN
  DUT  : uart_tx  
    PORT MAP ( 
      iRESET      => iRESET  ,
      oTX_ACK     => oTX_ACK  ,
      oTX_OUT     => oTX_OUT  ,
      iSTART_TX   => iSTART_TX  ,
      iDATA       => iDATA  ,
      iCLK        => iCLK   ) ; 

    iCLK <= not iCLK after 20 ns;

    process
    begin
--      TEMP 		<= 35;
--      iDATA	<= std_logic_vector(to_unsigned(TEMP,8));	
            
      wait for 100 ns;
      iRESET	<= '0';
      TEMP 		<= 35;
      
      for I in 0 to 15 loop
        wait for 400 ns;   
        iDATA	<= std_logic_vector(to_unsigned(TEMP,8));			
        TEMP		<= TEMP + 13;	-- se añade un valor aleatorio
      end loop;
      
      wait;		-- wait forever   
    end process;
  
    process
    begin
      while True loop
        wait for 130 ns;
        iSTART_TX	<= '1';
        wait for 40 ns;
        iSTART_TX	<= '0';
      end loop;

    end process;

END ; 

