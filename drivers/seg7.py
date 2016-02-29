from pyb import I2C
from time import sleep
import time

# Constants
# Commands
DEFAULT_ADDRESS  = 0x70
BLINK_CMD        = 0x80
DISPLAYON        = 0x01
OFF              = 0x00
HZ2              = 0x02
HZ1              = 0x04
HZ05             = 0x06
SETUP            = 0x20
OSCILLATOR       = 0x01
BRIGHT_CMD       = 0xE0

# Digits
DOT = 0b10000000

# Align
LEFT  = 0
RIGHT = 1

DIGITS = {
".": 0b10000000,
" ": 0b0000000,
"_": 0b0001000,
"0": 0b0111111,
"1": 0b0000110,
"2": 0b1011011,
"3": 0b1001111,
"4": 0b1100110,
"5": 0b1101101,
"6": 0b1111101,
"7": 0b0000111,
"8": 0b1111111,
"9": 0b1101111,
"A": 0b1110111,
"B": 0b1111111,
"C": 0b0111001,
"D": 0b0111111,
"E": 0b1111001,
"F": 0b1110001,
"G": 0b1111101,
"H": 0b1110110,
"I": 0b0000110,
"J": 0b0011110,
"L": 0b0111000,
"O": 0b0111111,
"P": 0b1110011,
"S": 0b1101101,
"U": 0b0111110,
"a": 0b1011111,
"b": 0b1111100,
"c": 0b1011000,
"d": 0b1011110,
"h": 0b1110100,
"-": 0b1000000,
"=": 0b1001000,
}

class SEG7(object):
    def __init__(self, bus=1, address = DEFAULT_ADDRESS):
        """Initialize driver with LEDs enabled and all turned off."""
        self._dev = I2C(bus)
        self._dev.init()
        self._addr = address
        self.inverted = False
        self._buffer = bytearray([0,0,0,0])
        self._write_buffer()
        # Turn on the oscillator.
        self._dev.send(SETUP | OSCILLATOR, self._addr)
        # Turn display on with no blinking.
        self.set_blink(OFF)
        # Set display to full brightness.
        self.set_brightness(15)

    def set_blink(self, frequency):
        """Blink display at specified frequency.  Note that frequency must be a
        value allowed by the HT16K33, specifically one of: OFF,
        HZ2, HZ1, or HZ05.
        """
        if frequency not in [OFF, HZ2, 
                             HZ1, HZ05]:
            raise ValueError('Frequency must be one of OFF, HZ2, HZ1, or HZ05.')
        self._dev.send(BLINK_CMD | DISPLAYON | frequency, self._addr)

    def set_brightness(self, brightness):
        """Set brightness of entire display to specified value (16 levels, from
        0 to 15).
        """
        if brightness < 0 or brightness > 15:
            raise ValueError('Brightness must be a value of 0 to 15.')
        self._dev.send(BRIGHT_CMD | brightness, self._addr)

    def write_byte(self, pos, val):
        if pos < 0 or pos > 3:
            raise  ValueError("Position must be between 0 and 3.")
        self._buffer[pos]=val
        self._write_buffer()
        
    def write_string(self, s, align=LEFT):
        # Sanity check
        for car in s:
            if car not in DIGITS.keys():
                raise ValueError("String contains non printable chars")
        if len(s)-s.count(".") > 4 :
            raise ValueError("String is too long")
        if s.startswith("."):
            raise ValueError("String cannot start with a dot")
        # Build buffer and write
        digits = []
        for c in s:
            if c == ".":
                digits[-1] |= DOT
            else:
                digits.append(DIGITS[c])
        # Process alignment
        if len(digits)<4:
            if align==RIGHT:
                digits = [0]*(4-len(digits)) + digits
        for pos, digit in enumerate(digits):
            self._buffer[pos] = digit
        
        self._write_buffer()

    def write_long_string(self, chaine, speed=1):
        chaine += "    "
        cursor = 0
        longueur = 1
        while cursor < len(chaine)-3:
            self.write_string(chaine[cursor:longueur], align=RIGHT)
            if longueur > 3:
                cursor += 1
            longueur += 1
            time.sleep(1/speed) 
                
    def _write_buffer(self):
        for pos, val in zip([0,2,6,8],self._buffer):
            self._dev.mem_write(val, self._addr, pos)
        
        
led = SEG7()
chaine = "OUI AU CAFE"
led.write_long_string(chaine, speed=3)