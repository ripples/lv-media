from os import listdir, mkdir, remove
from os.path import isdir
from shutil import copyfile, rmtree
from random import randint

rmtree("whiteboard") if isdir("whiteboard") else None
rmtree("computer") if isdir("computer") else None
mkdir("whiteboard")
mkdir("computer")

i = 1467865665
for file in listdir("."):
    if not (file == "rename.py" or file == "computer" or file == "whiteboard"):
        i1 = i + randint(0, 10)
        i2 = i + randint(0, 10)
        copyfile(file, "computer/computer-0-" + str(i1) + ".png")
        copyfile(file, "computer/computer-1-" + str(i1) + ".png")
        copyfile(file, "computer/computer-0-" + str(i1) + "-thumb.png")
        copyfile(file, "computer/computer-1-" + str(i1) + "-thumb.png")
        copyfile(file, "whiteboard/whiteboard-0-" + str(i2) + ".png")
        copyfile(file, "whiteboard/whiteboard-1-" + str(i2) + ".png")
        copyfile(file, "whiteboard/whiteboard-0-" + str(i2) + "-thumb.png")
        copyfile(file, "whiteboard/whiteboard-1-" + str(i2) + "-thumb.png")
        remove(file)
        i += 5
