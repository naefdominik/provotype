import qwiic_vl53l5cx 
import sys
from math import sqrt
import time
 
def runExample():
    print("\nQwiic VL53LCX Distance Test\n")
 
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

            # extract all distances into a list
            distances = [measurement_data.distance_mm[i] for i in range(image_resolution)]

            # test 1: minimum distance (closest object)
            #distance_value = min(distances)

            # test 2: average distance
            #distance_value = sum(distances) / len(distances)

            # test 3: center pixel only (row 4, col 4 in 8x8 mode)
            center_index = (image_width // 2) * image_width + (image_width // 2)
            distance_value = measurement_data.distance_mm[center_index]

            #for y in range (0, (image_width * (image_width - 1) )+ 1, image_width):
            #    for x in range (image_width - 1, -1, -1):
            #        print("\t", end="")
            #        print(measurement_data.distance_mm[x + y], end = "")
            #    print("\n")
            #print("\n")

            print("Distance (mm): %d" % distance_value)

            # TODO: feedback logic
            if distance_value < 300:  # closer than 30 cm
                print("Object is very close!")
                pass
            elif distance_value < 1000:  # closer than 1 m
                print("Object is at a moderate distance.")
                pass
            else:
                print("Object is far away.")
                pass
        
        time.sleep(0.005)
    
if __name__ == '__main__':
    try:
        runExample()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example")
        sys.exit(0)
