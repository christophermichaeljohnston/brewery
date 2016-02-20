from django.shortcuts import render


# Create your views here.
def index(request):
  return render(request, 'equipment/index.html')

def discover(request):
  import glob
  for file in glob.glob("/dev/ttyACM*"):
    print(file)
  return render(request, 'equipment/discover.html')
