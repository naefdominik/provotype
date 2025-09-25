import qwiic_vl53l5cx 
import sys
from math import sqrt
import time
 
def runExample():
    print("\nQwiic VL53LCX Example 1 - DistanceArray\n")
 
    myVL53L5CX = qwiic_vl53l5cx.QwiicVL53L5CX() 
 
    if myVL53L5CX.is_connected() == False:
        print("The device isn't connected to the system. Please check your connection", file=sys.stderr)
        return
 
    print ("Initializing sensor board. This can take up to 10s. Please wait.")
    if myVL53L5CX.begin() == False:
        print("Sensor initialization unsuccessful. Exiting...", file=sys.stderr)
        sys.exit(1)
 
    myVL53L5CX.set_resolution(8*8) # enable all 64 pads
    image_resolution = myVL53L5CX.get_resolution()  # Query sensor for current resolution - either 4x4 or 8x8
 
    image_width = int(sqrt(image_resolution)) # Calculate printing width
    myVL53L5CX.start_ranging()
 
    while True:
        if myVL53L5CX.check_data_ready():
            measurement_data = myVL53L5CX.get_ranging_data()
            for y in range (0, (image_width * (image_width - 1) )+ 1, image_width):
                for x in range (image_width - 1, -1, -1):
                    print("\t", end="")
                    print(measurement_data.distance_mm[x + y], end = "")
                print("\n")
            print("\n")
        
        time.sleep(0.005)
    
if __name__ == '__main__':
    try:
        runExample()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example")
        sys.exit(0)
