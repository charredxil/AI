import sys, os.path, PIL.Image
if not os.path.isfile(sys.argv[1]): print("FILE NONEXISTANT")
else:
    try:
        im = PIL.Image.open(sys.argv[1])
        print(im.size)
    except IOError:
        print("NOT AN IMAGE FILE")