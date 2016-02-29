import serial
import time

DEVICE_PATH = "/dev/ttyACM*"

ports = {}

def initialize():
  global ports
  for port in ports:
    close(port)
  ports = {}

def discover(request):
  initialize()
  import glob
  for device in glob.glob(DEVICE_PATH):
    open(device)
    type = SerialAPI.cmd(device, "getType")

def open(port):
  global ports
  ports[port] = serial.Serial(port=port, baudrate=9600)
  time.sleep(3)

def close(port):
  global ports
  ports[port].close()

class SerialAPI:

  def cmd(port, cmd):
    global ports
    ports[port].reset_input_buffer()
    ports[port].reset_output_buffer()
    ports[port].write((cmd+"\n").encode())
    return ports[port].readline().decode().rstrip('\n').rstrip('\r')

