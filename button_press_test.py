from gpiozero import Button

button = Button(4)

print("Start")
button.wait_for_press()
print("Pandey Tharki")
    # results={}
    # results["yolo"]=result_yolo
    # results["ell"]=result_ell
