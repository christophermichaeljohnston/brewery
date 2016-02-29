import serial
import time

PORT_PATH = "/dev/ttyACM*"

ports = {}

def initialize():
  global ports
  for port in ports:
    close(port)
  ports = {}

def discover(request):
  initialize()
  import glob
  for port in glob.glob(PORT_PATH):
    open(port)
  time.sleep(3)

def open(port):
  global ports
  ports[port] = serial.Serial(port=port, baudrate=9600, timeout=1.0, write_timeout=1.0)

def close(port):
  global ports
  ports[port].close()

class PortAPI:

  def cmd(port, cmd):
    global ports
    ports[port].reset_input_buffer()
    ports[port].reset_output_buffer()
    ports[port].write((cmd+"\n").encode())
    return ports[port].readline().decode().rstrip('\n').rstrip('\r')

