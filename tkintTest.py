import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading
import numpy as np
import argparse
from argcomplete.completers import ChoicesCompleter
from src.plot_event import plotEvent
from src.plot_histos import plotHistograms
from src.read_config import readConfig
from src.unscrambler import trigIdSort, bufferSort
from analyzer import applyCuts, averageADC
from src.read_file import getEventsTail
import tkinter as tk
from tkinter import ttk
from tkinter import * 
import PIL.Image
from time import sleep

import warnings
warnings.simplefilter("ignore", UserWarning)

seconds = 0
spillID = 1
spillPath = ''
working = False

# Button is clicked
def sync():
        print('Reset')
        global seconds
        seconds = 0

def findNextSpillID(outputDir):
        nextSpillID = 1
        while (f'Spill{nextSpillID}' in os.listdir(outputDir)):
                nextSpillID +=1
        return nextSpillID

# Get input from the text box
def getInputBoxValue():
	userInput = secondsBack.get()
	return userInput

def readSpill(inputFilename, config, outputDir, labelList, root):
    allEvents = getEventsTail(inputFilename, config, timeWindow = 60)
    passedEvents = applyCuts(allEvents, config)
    averageEvent = averageADC(passedEvents)
    runNumber = inputFilename.split('Run')[1].split('_')[0]
    global spillPath
    global working
    
    plotEvent(averageADC(passedEvents), outputDir, runNumber, len(allEvents), config, avg=True, passingEvents = len(passedEvents)) 
    plotHistograms(passedEvents, config, runNumber, outputDir)

    avgADC = makeImage(f'{outputDir}/average_ADC.png', 250, 400, root)
    labelList[2].configure(image=avgADC)
    labelList[2].image = avgADC
    labelList[2].place(x=54, y=34)

    sumHist = makeImage(f'{outputDir}/channel_sum_histogram.png', 400, 250, root)
    labelList[3].configure(image=sumHist)
    labelList[3].image = sumHist
    labelList[3].place(x=54, y=480)

    working = False
    
def loop(inputFilename, config, outputDir, labelList, root):
        global seconds
        global spillID
        global spillPath
        global working
        
        seconds +=1
        labelList[4].config(command=(sync))

        labelList[1].config(text=f'Update in {60 - seconds} seconds.')
        if seconds % 15 == 0:
                labelList[1].config(text=f'Update in {60 - seconds} seconds. Producing last spill plots...')
                spillID = findNextSpillID(outputDir)
                spillPath = f'{outputDir}/Spill{spillID}'
                os.mkdir(spillPath)
                labelList[0].config(text=f'Spill: {spillID}')
                seconds = 0

                #taskThread = threading.Thread(target=periodicTask, args=(inputFilename, config, outputDir))
                #taskThread.daemon = True
                #taskThread.start()
                if not working:
                        working = True
                        readSpill(inputFilename, config, f'{outputDir}/Spill{spillID}', labelList, root)
        root.after(1000, loop, inputFilename, config, outputDir, labelList, root) 

def startGUI(inputFilename, config, outputDir):
        root = Tk()
        global seconds
        global spillID
        
        # Create tkinter window
        root.geometry('1200x900')
        root.configure(background='#A9A9A9')
        root.title('DarkQuest Testbeam DQM')
        
        canvas = tk.Canvas(root, width=1200, height=900, background='#A9A9A9')
        canvas.pack()
        
        labelList = []

        runNumber = inputFilename.split('Run')[1].split('_')[0]              
        Label(root, text=f'Run: {runNumber}', bg='#A9A9A9', font=('arial', 22, 'normal')).place(x=324, y=224)
        
        spillTag = Label(root, text=f'Spill: XX', bg='#A9A9A9', font=('arial', 16, 'normal'))
        spillTag.place(x=324, y=254)

        updateTag = Label(root, text=f'Reading Janus file. One moment...', bg='#A9A9A9', font=('arial', 16, 'normal'))
        updateTag.place(x=324, y=274)

        Label(root, text='secs.', bg='#A9A9A9', font=('arial', 12, 'normal')).place(x=374, y=400)                
        secondsBack=Entry(root)
        secondsBack.place(x=264, y=400)

        avgADCL = Label(root, text='Last spill average ADCs', bg='#A9A9A9', font=('arial', 12, 'normal'),compound='bottom')
        histogramL = Label(root, text='Histogram of channel summed ADC', bg='#A9A9A9', font=('arial', 12, 'normal'), compound='bottom')
        button = Button(root, text='read', bg='#A9A9A9', font=('arial', 12, 'normal'))

        labelList.append(spillTag) # [0]
        labelList.append(updateTag) # [1]
        labelList.append(avgADCL) # [2]
        labelList.append(histogramL) # [3]

        # Generate first plot set
        readSpill(inputFilename, config, f'{outputDir}/Spill{spillID}', labelList ,root)
        labelList[0].config(text=f'Spill: {spillID}')
        
        # Create a button
        button.place(x=424, y=400)
        labelList.append(button) # [4]

        root.after(1000, loop, inputFilename, config, outputDir, labelList, root)  # Schedule first check.        
        root.mainloop()        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Janus event list')
    parser.add_argument('-c', '--configFile', dest='configFile', type=str, help='The name of the .cfg file for the input run file', default=None)
    args = parser.parse_args()
    inputFilename = args.filename

    global spillID
    
    config = {}
    if args.configFile is None:
        config = {
            'triggerThresh': 400,
            'vetoThresh': 400,
            'sumThresh': -1,
            'sumMax': 120000,
            'emcalCfg': [
                ['o', 'o', 'o', 'o'],
                ['o', 'o', 'o', 'o'],
                ['o', 'o', 'o', 'o'],
                ['o', 'o', 'o', 'o']
            ],
            'topHodoCfg': ['x', 'x','x', 'x'],
            'bottomHodoCfg': ['x', 'x','x', 'x'],
            'topHodoEnabled': False,
            'botHodoEnabled': False,
            'name': 'allChannel',
            'tag' : 'allChannel'
        }
    else:
        config = readConfig(args.configFile)

    runNumber = args.filename.split('Run')[1].split('_')[0]        
    outputDir = f'output/run{runNumber}_{config["name"]}_live'
    os.makedirs(outputDir, exist_ok=True)

    spillID = findNextSpillID(outputDir)
    os.makedirs(f'{outputDir}/Spill{spillID}', exist_ok=True)
    
    startGUI(inputFilename, config, outputDir)


def makeImage(imagePath, xscale, yscale, root):
        # Show average ADC
        img = PIL.Image.open(imagePath)
        img = img.resize((xscale, yscale), PIL.Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img, master=root)
        print(imagePath)
        return img_tk

if __name__ == "__main__":
    main()
