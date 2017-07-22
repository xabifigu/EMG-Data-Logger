LIBRARY ieee  ; 
USE ieee.NUMERIC_STD.all  ; 
USE ieee.std_logic_unsigned.all  ;
USE ieee.std_logic_1164.all  ;
use ieee.math_real.all; 
ENTITY adc_controller_tb  IS 
END ; 
 
ARCHITECTURE adc_controller_tb_arch OF adc_controller_tb IS
  -- seÃ±ales de salida
  SIGNAL oVALUE     :  std_logic_vector (11 downto 0)  ;   
  SIGNAL oSCLK      :  STD_LOGIC  ; 
  SIGNAL oCURR_CH   :  std_logic_vector (2 downto 0)  ; 
  SIGNAL oCS_OUT_n  :  STD_LOGIC  ; 
  SIGNAL oDIN       :  STD_LOGIC  ; 

  -- seÃ±ales de entrada
  SIGNAL iRESET     :  STD_LOGIC := '1' ; 
  SIGNAL iDOUT      :  STD_LOGIC := '0' ; 
  SIGNAL iNEXT_CH   :  std_logic_vector (2 downto 0) := (others => '0') ; 
  SIGNAL iCLK       :  STD_LOGIC := '0'  ; 

  -- seÃ±ales internas
  SIGNAL rand_num   : integer := 0;
  SIGNAL rand_vector: std_logic_vector (11 downto 0) := (others => '0');

  COMPONENT adc_controller  
    PORT ( 
      oVALUE      : out std_logic_vector (11 downto 0) ; 
      oSCLK       : out STD_LOGIC ; 
      iRESET      : in STD_LOGIC ; 
      oCURR_CH    : out std_logic_vector (2 downto 0) ; 
      oCS_OUT_n   : out STD_LOGIC ; 
      iDOUT       : in STD_LOGIC ; 
      iNEXT_CH    : in std_logic_vector (2 downto 0) ; 
      oDIN        : out STD_LOGIC ; 
      iCLK        : in STD_LOGIC ); 
  END COMPONENT ; 
BEGIN
  DUT  : adc_controller  
    PORT MAP ( 
      oVALUE      => oVALUE  ,
      oSCLK       => oSCLK  ,
      iRESET      => iRESET  ,
      oCURR_CH    => oCURR_CH  ,
      oCS_OUT_n   => oCS_OUT_n  ,
      iDOUT       => iDOUT  ,
      iNEXT_CH    => iNEXT_CH  ,
      oDIN        => oDIN  ,
      iCLK        => iCLK   ) ; 

      -- Generador de señal de reloj
      iCLK <= not iCLK after 20 ns;

      -- Proceso para cambio de canal
      process
      begin
        for I in 0 to 15 loop
          wait for 2000 ns;
          iNEXT_CH <= iNEXT_CH + "001";
        end loop;
        wait;
      end process;   

      -- Control de reset
      process
      begin
        wait for 100 ns;
        iRESET <= '0';
        wait for 5000 ns;
        iRESET <= '1';
        wait for 100 ns;
        iRESET <= '0';
      end process;   
      
      -- Proceso para generar la seï¿½al recibida desde
      -- el ADC
      process
      begin
        -- Se espera la mitad de ciclo de reloj, ya
        -- que la seï¿½al procedente del ADC cambia 
        -- durante el ciclo descendente (datasheet ADC128s022)
        wait for 10 ns; 
        while True loop
          wait for 40 ns;
          -- iDOUT <= not iDOUT; 
          iDOUT <= rand_vector(0);
          -- iDOUT <= std_logic_vector(rand_num mod 2);
        end loop ;

      end process;
      
      -- Generador de números random
      -- Para este Test sólo se necesitas booleanos
      process
      variable seed1, seed2: positive;               -- seed values for random generator
      variable rand: real;   -- random real-number value in range 0 to 1.0  
      variable range_of_rand : real := 1000.0;    -- the range of random values created will be 0 to +1000.
      begin
        uniform(seed1, seed2, rand);   -- generate random number
        rand_num <= integer(rand*range_of_rand);  -- rescale to 0..1000, convert integer part 
        rand_vector <= std_logic_vector(to_unsigned(rand_num,12));
        wait for 10 ns;
      end process;

END ; 

