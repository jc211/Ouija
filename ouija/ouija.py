from typing import Optional
import serial
import time

class OuijaBoard:
    """This class is used to control the Ouija Board."""

    locked: bool = True
    """Whether the machine is locked. If it is locked, it will not move."""
    calibrated: bool = False
    """Whether the machine is calibrated. If it is not calibrated, it will not move."""
    absolute_mode: bool = True
    """Whether the machine is in absolute mode. If it is in absolute mode, it will move to the absolute position. If it is in relative mode, it will move relative to the current position."""
    workspace_width: float = 140.0
    """The width of the workspace in mm."""
    workspace_height: float = 140.0
    """The height of the workspace in mm."""
    max_speed: float = 15000.0
    """The maximum speed of the machine in mm/min""" 

    def __init__(self, port:str="/dev/ttyACM0", print_lines: bool = False):
        self._c = Controller(port, print_lines=print_lines)
        self.locked = True
        self.calibrated = False
        self.set_unit_to_mm()
        self.absolute()
        self.last_commanded_position = [0.0, 0.0]

    def unlock(self):
        """This will unlock the machine without moving it."""
        assert False, "Calibrate the machine first or it will crash. Don't do this"
        self.set_unit_to_mm()
        self._c.send("$X\n")
        self.locked = False

    def set_unit_to_mm(self):
        self._c.send("G21\n")

    def unlock_and_calibrate(self):
        """This will move the machine to the top left corner of the board and set that as the origin."""
        self.set_unit_to_mm()
        self.absolute()
        self._c.send("$H\n")
        self.calibrated = True
        self.locked = False
        self.move(0, 0)
        # self.unlock()
    
    def move(self, x: float, y: float, speed: Optional[float] = None):
        """Move to a coordinate in mm. Relative and absolute set separately by absolute() and relative()"""
        assert not self.locked, "The machine is locked. Please unlock it first."
        assert self.absolute_mode, "Only absolute mode is supported at the moment."
        assert self.calibrated, "The machine is not calibrated. Please calibrate it first."
        assert 0 <= x <= self.workspace_width, f"x must be between 0 and {self.workspace_width}"
        if speed is not None:
            assert speed <= self.max_speed and speed > 0, f"Speed must be less than {self.max_speed} and more than 0"
            self._c.send(f"G01 F{speed:.5f} X{x:5f} Y{y:5f}\n")
        else:
            self._c.send(f"G0 X{x:5f} Y{y:5f}\n")
        
        self.last_commanded_position = [x, y]
    
    def absolute(self):
        """Set the machine to absolute mode."""
        self._c.send("G90\n")
    
    def relative(self):
        """Set the machine to relative mode."""
        self._c.send("G91\n")

class Controller:
    def __init__(self, port: str, print_lines: bool = False):
        self.port = port
        self.print_lines = print_lines
        self.serial = serial.Serial(port, 115200, timeout=1)
        time.sleep(1) # Wait for serial to initialise
        self._wait_for_ok()
    
    
    def _wait_for_ok(self):
        while 1:
            recv = self.serial.readline()
            if not recv:
                break
    
    def send(self, cmds: str):
        for cmd in cmds.split("\n"):
            if self.print_lines:
                print(f"Serial sending: {cmd}")
            self.serial.write(bytes(cmd +"\n", "utf-8"))

if __name__ == "__main__":
    b = OuijaBoard()
    b.unlock_and_calibrate()
    time.sleep(10)
    b.move(0, 100, speed=100)
    # b.move(100, 0)
