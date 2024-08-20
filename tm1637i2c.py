from periphery import I2C

class TM1637I2C:

    BRIGHTNESS_LEVEL_1 = 0x00
    BRIGHTNESS_LEVEL_2 = 0x40
    BRIGHTNESS_LEVEL_3 = 0x20
    BRIGHTNESS_LEVEL_4 = 0x60
    BRIGHTNESS_LEVEL_5 = 0x50
    BRIGHTNESS_LEVEL_6 = 0x70

    '''
      
     --a--
    |     |
    f     b
    |     |
     --g--  
    |     |
    e     c
    |     |
     --d--   (dp)
      
    '''

    SEGMENT_A = 0b1000_0000
    SEGMENT_B = 0b0100_0000
    SEGMENT_C = 0b0010_0000
    SEGMENT_D = 0b0001_0000
    SEGMENT_E = 0b0000_1000
    SEGMENT_F = 0b0000_0100
    SEGMENT_G = 0b0000_0010
    SEGMENT_DECIMAL_POINT = 0b0000_0001

    DISPLY_BLANK = 0x00
    
    DIGIT_0 = 0xfc
    DIGIT_1 = 0x60
    DIGIT_2 = 0xda
    DIGIT_3 = 0xf2
    DIGIT_4 = 0x66
    DIGIT_5 = 0xb6
    DIGIT_6 = 0xbe
    DIGIT_7 = 0xe0
    DIGIT_8 = 0xfe
    DIGIT_9 = 0xf6

    DIGITS = [DIGIT_0, DIGIT_1, DIGIT_2, DIGIT_3, DIGIT_4, 
             DIGIT_5, DIGIT_6, DIGIT_7, DIGIT_8, DIGIT_9, ]
    
    
    def __init__(self, devpath):
        """Instantiate an TM1637I2C object and open the TM1637 4-Digit 7-Segment Display
        device at the specified path.
        TM1637 uses a protocol similar to I2C, but it doesn't support addressing. Therefore,
        the addressing information transmitted using the I2C protocol is interpreted as part
        of the incoming command ( this address bit is parsed with the least significant bit 
        first ).   When initializing or setting the brightness for TM1637, an end signal is 
        required to make the command take effect. Here, the rising edge generated when reading
        data using the I2C protocol is used to make the command effective. As a result, when 
        initializing or setting brightness, all display data will be reset to 0xff.        

        Args:
            devpath (str): i2c-dev device path.

        Returns:
            TM1637I2C: TM1637I2C object.

        Raises:
            I2CError: if an I/O or OS error occurs.

        """
        
        self.i2c = I2C(devpath)
        self.brightness_level = self.BRIGHTNESS_LEVEL_1
        self.i2c.transfer(0x08,[I2C.Message([0x00,0x00,0x00,0x00,0x00,0x00], read=True)])
        self.digits = [0xff,0xff,0xff,0xff] # when initializing or setting brightness, all display data will be reset to 0xff.       


    def brightness(self, brightness_level = BRIGHTNESS_LEVEL_1):
        """Adjust the brightness of the digital tube display. TM1637 can modify the display
        brightness by setting the pulse width, with a total of 6 levels. Controlled through 
        constants BRIGHTNESS_LEVEL_1 to BRIGHTNESS_LEVEL_6.

        Args:
            brightness_level (byte): constants BRIGHTNESS_LEVEL_1 to BRIGHTNESS_LEVEL_6.

        Raises:
            I2CError: if an I/O or OS error occurs.

        """
        
        self.brightness_level = brightness_level
        command = self.brightness_level | 0x08
        self.i2c.transfer(command,[I2C.Message([0x00,0x00,0x00,0x00,0x00,0x00], read=True)])
        self.display(self.digits[0],self.digits[1],self.digits[2],self.digits[3]) # Bring back the displayed content
        
    
    def display(self, display_positon_0, display_positon_1, dsiplay_positon_2, display_positon_3):
        """Set display content. The 4-Digit 7-Segment Display has 4 digit positions available for display. 
        Numbers can be shown using constants DIGIT_0 to DIGIT_9, or by freely combining SEGMENT_A to SEGMENT_G. 
        The colon in the middle of the display is controlled by the decimal point of the second digit position, 
        which can be activated by performing an OR operation with SEGMENT_DECIMAL_POINT.

        Args:
            display_positon_0 (byte): first 7-Segment to Display.
            display_positon_1 (byte): second 7-Segment to Display.
            display_positon_2 (byte): third 7-Segment to Display.
            display_positon_3 (byte): fourth 7-Segment to Display.

        Raises:
            I2CError: if an I/O or OS error occurs.

        """
        
        self.digits = [display_positon_0, display_positon_1, dsiplay_positon_2, display_positon_3]
        self.i2c.transfer(0x40,[I2C.Message(self.digits + [0x00,0x00])]) # Four-digit display, with the last two digits not shown


    def show(self, number, colon=False):
        """Display numbers. This is a simplified method to display incoming integer numbers. When the number 
        exceeds 4 digits, only the last four digits are shown. The colon is controlled by a separate variable.

        Args:
            number (int): integer numbers to Display.
            colon (boolean): Whether to display the colon.

        Raises:
            I2CError: if an I/O or OS error occurs.

        """
        number = abs(int(number)) # Ensure that number is a positive integer
        
        ones = number % 10
        tens = (number // 10) % 10
        hundreds = (number // 100) % 10
        thousands = (number // 1000) % 10
        
        self.display(self.DIGITS[thousands], 
                     self.DIGITS[hundreds] | self.SEGMENT_DECIMAL_POINT if colon else self.DIGITS[hundreds] , 
                     self.DIGITS[tens], 
                     self.DIGITS[ones])
