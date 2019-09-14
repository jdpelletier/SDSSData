import os
import re
import argparse
from SDSSData import SDSSData

parser = argparse.ArgumentParser(description="This program sees what's up at your favorite observatory!",
                         usage="python WhatsUp.py -d [path to directory] -l [observatory name]",
                         epilog="see astropy doc for available observatory locations")

parser.add_argument("-d", "--directory", required = True,
                    help="path to directory you want to scan")

parser.add_argument("-l", "--location", required = True,
                    help="location of observation")


args = parser.parse_args()


#directory = '/Users/johnpelletier/Desktop/SciCoder-2019-Keck/Data Files/spectra/'
starlist = list()
starlistNames = list()
directory = os.fsencode(args.directory)
os.system('clear')
i = 1
######Print header
print("\n\n\n\n")
print("--------------------------------")
print("Welcome to SDSS Target Finder!")
print("--------------------------------")
print("\n\n\n")
print(f"\n\n")
print("STAR             COORDINATES                   EL/AZ                      Is it up?\n\n")


for file in os.listdir(directory):
     filename = os.fsdecode(file)
     tempDir = os.fsdecode(directory)
     trunc_name = re.match("([\w-]+)-[\w.]+$", filename).group(1) #ignore repeat stars
     if filename.endswith(".fits") and trunc_name not in starlist:
         starlist.append(trunc_name)
         starlistNames.append(tempDir+filename)
         star = SDSSData(f'{tempDir}{filename}', args.location)
         print(f"{i}.", end=" ")
         print(star.hdr['NAME'], end=" ")
         print(star.displayCoordinates(), end="  ")
         print(star.is_up()+"\n")
         star.close_fits_file()
         i+=1

yesno = input("\n\nWould you like to plot a star? ")
if yesno in ['yes', 'Yes', 'YES', 'y', 'Y']:
    number = int(input("Wich one? (pick a number): "))
    star = SDSSData(starlistNames[number - 1], args.location)
    star.plot_star()
    star.close_fits_file()

print('\n\n\n------------')
print("Clear skies!")
print('------------\n\n\n')
