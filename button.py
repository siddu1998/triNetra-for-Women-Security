from flask import Flask, jsonify
from gpiozero import Button
import cv2
##Yolo Imports
from darkflow.net.build import TFNet
import numpy as np
from datetime import datetime as dt
import tensorflow as tf

##Send messages GSM and GPS imports
import serial
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

import string
import pynmea2

# Enable Serial Communication
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)



#imports for sms
import time
from time import sleep
from sinchsms import SinchSMS

##ELL Imports
import tutorial_helpers as helpers
import model



options = {
    'model': 'cfg/tiny-yolo-voc.cfg',
    'load': 'bin/tiny-yolo-voc.weights',
    'threshold': 0.2,
    'gpu': 0
}
tfnet = TFNet(options)

date = datetime.datetime.now()
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]


##Codes
def capture_image():
    capture=cv2.VideoCapture(0)
    ret,frame=capture.read()
    capture.release()
    return frame,ret

def get_results_yolo(frame,ret):
    results = tfnet.return_predict(frame)
    count=0
    gun=0
    if ret:
        for color, result in zip(colors, results):
            label = result['label']
            if label=='person':
                count = count + 1
            if label=='gun':
                gun = gun + 1
    return count


def get_results_ell(frame):
    with open("categories.txt", "r") as categories_file:
        categories = categories_file.read().splitlines()
    input_shape = model.get_default_input_shape()
    input_data = helpers.prepare_image_for_model(
            frame, input_shape.columns, input_shape.rows)
    predictions = model.predict(input_data)
    top_5 = helpers.get_top_n(predictions, 5)
    header_text = ", ".join(["({:.0%}) {}".format(
            element[1], categories[element[0]]) for element in top_5])
    print("Printing header_text")
    print(header_text)
    return str(header_text)


def sendSMS(ell,yolo,coordinates):
    # enter all the details
    # get app_key and app_secret by registering
    # a app on sinchSMS
    port.write('AT+CMGS="+918437593296"'+'\r\n')
    rcv = port.read(10)
    number = '+918437593296'
    app_key = '23e0f50a-749b-4e91-b567-6b39ca381854'
    app_secret = 'GHgxRvVaNEC9B2J0RXGI+g=='
    results_of_yolo_ell=str(yolo)+" people carrying "+ str(ell)+" number of weapons"

    # enter the message to be sent
    message = " '%s' : I am feeling unsafe at '%s', there are '%s' around me"%(date,location_cords,results_of_yolo_ell)

    client = SinchSMS(app_key, app_secret)
    print("Sending '%s' to %s" % (message, number))

    response = client.send_message(number, message)
    message_id = response['messageId']
    response = client.check_status(message_id)

    # keep trying unless the status retured is Successful
    while response['status'] != 'Successful':
        print(response['status'])
        time.sleep(1)
        response = client.check_status(message_id)

    print(response['status'])


def get_coordinates():
    gpio.setmode(gpio.BCM)
    ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)

    co-ordinates={}

    while 1:
    try:
        data = ser.readline()
    except:
        exit()
    #wait for the serial port to churn out data

    if data[0:6] == '$GPGGA': # the long and lat data are always contained in the GPGGA string of the NMEA data
        msg = pynmea2.parse(data)

    #parse the latitude and print
    latval = msg.lat
    concatlat = "lat:" + str(latval)
    coordinates['latitude'] = concatlat

    #parse the longitude and print
    longval = msg.lon
    concatlong = "long:"+ str(longval)

    coordinates['longitude'] = concatlong

    return coordinates




def create_report(result_yolo, result_ell, coordinates):
    time = str(dt.now())
    file_name = 'reports/report'+time+'.pdf'
    doc = SimpleDocTemplate(file_name,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)
    Story=[]
    cv2.imwrite("frame%d.jpg" % ret, frame)
    image = "frame1.jpg"
    im = Image(image, 2*inch, 2*inch)
    Story.append(im)

    formatted_time = tm.ctime()

    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    ptext = 'TIME:<font size=12>%s</font>' % formatted_time
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))

    ptext = 'Location Co-Ordinates:<font size=12>%s</font>' % location_cords
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))

    ptext = 'Details:<font size=12></font>'
    Story.append(Paragraph(ptext, styles["Normal"]))
    ptext = 'Number of persons=<font size=12>%s</font>' % result_yolo
    Story.append(Paragraph(ptext, styles["Normal"]))
    ptext = 'Number of guns=<font size=12>%s</font>' % result_ell
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))
    doc.build(Story)

button = Button(4)
while True:
    button.wait_for_press()
    print("triNetra scanning your surrounding")
    frame,ret=capture_image()
    result=[]
    result_ell=get_results_ell(frame)
    result_yolo=get_results_yolo(frame,ret)
    coordinates = get_coordinates()
    # results["ell"]=result_ell

    print(result_ell)
    print("ELL Complete")
    print(result_yolo)
    sendSMS(result_ell, result_yolo, coordinates)
    create_report(result_yolo, result_ell, coordinates)
    print("Report Generated Successfully")
