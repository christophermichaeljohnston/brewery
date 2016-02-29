import serial
import time

DEVICE_PATH = "/dev/ttyACM*"

devices = {}
stuff = 0

class SerialAPI:

  def discover(request):
    initialize()
    import glob
    for device in glob.glob(DEVICE_PATH):
      open(device)
      type = cmd(device, "getType")
      if type == "FERMENTER":
        open(dev)
      else:
        close(dev)

  def initialize():
    global devices
    for device in devices:
      close(device)
    devices = {}

  def open(device):
    global devices
    devices[device] = serial.Serial(port=device, baudrate=9600)
    time.sleep(3)

  def close(dev):
    global devices
    devices[device].close()

  def cmd(device, cmd):
    global devices
    devices[device].flushInput()
    devices[device].flushOutput()
    devices[device].write((cmd+"\n").encode())
    return devices[device].readline().decode().rstrip('\n').rstrip('\r')
