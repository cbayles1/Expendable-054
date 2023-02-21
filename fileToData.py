import base64
import os
from os import path

main_folder = path.dirname(__file__)
img_folder = path.join(main_folder, 'img')
audio_folder = path.join(main_folder, 'audio')
data_folder = path.join(main_folder, 'data')
images = os.listdir(img_folder)
audios = os.listdir(audio_folder)
imgDataList = []
audioDataList = []


for image in images:
    inFile = open(path.join(img_folder, image), 'rb')
    imgDataList.append(base64.b64encode(inFile.read()))
    inFile.close()

for audio in audios:
    inFile = open(path.join(audio_folder, audio), 'rb')
    audioDataList.append(base64.b64encode(inFile.read()))
    inFile.close()

inFile = open(path.join(main_folder, 'vt323.ttf'), 'rb')
font1Data = base64.b64encode(inFile.read())
inFile.close()


if len(imgDataList) != len(images) or len(audioDataList) != len(audios): 
    print("WARNING! INCONSISTENT LIST LENGTH DETECTED!")


for i in range(len(imgDataList)):
    outFile = open(path.join(data_folder, str(images[i][:-4] + '.dat')), 'wb')
    outFile.write(imgDataList[i])
    outFile.close()

for i in range(len(audioDataList)):
    outFile = open(path.join(data_folder, str(audios[i][:-4] + '.dat')), 'wb')
    outFile.write(audioDataList[i])
    outFile.close()

outFile = open(path.join(data_folder, 'vt323.dat'), 'wb')
outFile.write(font1Data)
outFile.close()