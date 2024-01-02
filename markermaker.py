
    # file1 = open('shelters_m.txt', 'r')  # read mode

from lib2to3.pgen2.token import EQUAL
from pickle import FALSE, TRUE


file = open("shelters_m.txt", "r",encoding="utf-8")

fsize = len(file.read(-1))
file = open("shelters_m.txt", "r",encoding="utf-8")

c = file.read(-1)
lat1 = 0
lat2 = 0
lat = FALSE
long1 = 0
long2 = 0
longb= FALSE
for i in range(fsize):
    if c[i]=="l" and (c[i+3])==":":
        lat1 = i+4
        lat=TRUE
    if lat and c[i]=="l" and (c[i+4])==":":
        lat2 = i-1
        long1=i+5
        lat=FALSE
        longb=TRUE
    if longb and c[i]=="\n":
        long2=i-1
        print(c[lat1:lat2])
        print(c[long1:long2])
        longb=FALSE
        

        

filet = open("test.txt", "w")  # write mode
filet.write("test file \n")
    #this is a simple test file incase the agents file doesnt work either.
filet.close()
