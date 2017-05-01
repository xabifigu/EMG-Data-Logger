LIBRARY ieee  ; 
USE ieee.NUMERIC_STD.all  ; 
USE ieee.std_logic_unsigned.all  ;
USE ieee.std_logic_1164.all  ; 
ENTITY main_block_tb  IS 
END ; 
 
ARCHITECTURE main_block_tb_arch OF main_block_tb IS
	-- señales de salida
  SIGNAL oNEXT_CH   :  std_logic_vector (2 downto 0)  ; 
	SIGNAL oBYTE   		:  std_logic_vector (7 downto 0)  ; 
  SIGNAL oTX_ON   	:  STD_LOGIC 	; 
	
	-- señales de entrada
  SIGNAL iRESET   	:  STD_LOGIC := '1' ; 
  SIGNAL iVALUE  		:  std_logic_vector (11 downto 0) := (others=>'0') ; 
  SIGNAL iTX_ACK   	:  STD_LOGIC := '0' ; 
  SIGNAL iCLK   		:  STD_LOGIC := '0' ; 
	SIGNAL iADC_CH		:	 std_logic_vector (2 downto 0) := (others=>'0') ;
	
	-- señales internas
	SIGNAL TEMP 			: integer;
	
  COMPONENT main_block  
    PORT ( 
      oNEXT_CH  : out std_logic_vector (2 downto 0) ; 
      iRESET  	: in STD_LOGIC ; 
      iVALUE  	: in std_logic_vector (11 downto 0) ; 
			iADC_CH		:	in std_logic_vector (2 downto 0)	;
      oBYTE  		: out std_logic_vector (7 downto 0) ; 
      oTX_ON  	: out STD_LOGIC ; 
      iTX_ACK  	: in STD_LOGIC ; 
      iCLK  		: in STD_LOGIC ); 
  END COMPONENT ; 
BEGIN
  DUT  : main_block  
    PORT MAP ( 
      oNEXT_CH		=> oNEXT_CH  ,
      iRESET   		=> iRESET  ,
      iVALUE   		=> iVALUE  ,
			iADC_CH			=> iADC_CH	,
      oBYTE   		=> oBYTE  ,
      oTX_ON   		=> oTX_ON  ,
      iTX_ACK   	=> iTX_ACK  ,
      iCLK   			=> iCLK   ) ; 
			
			
			iCLK <= not iCLK after 20 ns;

      process
        begin
				
        wait for 100 ns;
        iRESET	<= '0';
				TEMP 		<= 123;
				-- -- wait for 100 ns;
				-- -- iVALUE <= X"123";	
				
				 wait for 140 ns;	
		
        for I in 0 to 15 loop   
					iVALUE	<= std_logic_vector(to_unsigned(TEMP,12));
					iADC_CH <= iADC_CH + "001";					
					TEMP		<= TEMP + 234;	
          wait for 100 ns;
          iTX_ACK	<= '1';
          wait for 40 ns;
					iTX_ACK	<= '0';
        end loop;

				wait;		-- wait forever   
				
      end process;   
			
END ; 

