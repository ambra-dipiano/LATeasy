import numpy as np
import os
import sys

def collect_data(name, source):
    source = str(source)
    for entry in os.listdir("."):
        #if os.path.isdir(entry) and name+"_" in entry:
        if os.path.isdir(entry):
            print(entry)
            if os.path.exists(entry + "/roi2.npy"):
                #print(entry + "/roi2.npy")
                data = np.load(entry + "/roi2.npy").flat[0]
                #print(data["sources"][source]["ts"])
                #file.write(entry + " " + source + " " + str(data['sources'][source]['ts']))
                #if data['sources'][source]['ts'] > 6:
                #    file.write("\n\n")
                sens3=0
                sens35=0
                sens4=0
                sens5=0
                if os.path.exists(entry + "/sens3.txt"):
                    f = open(entry + "/sens3.txt", "r")
                    sens3 = f.read().strip()
                if os.path.exists(entry + "/sens35.txt"):
                    f = open(entry + "/sens35.txt", "r")
                    sens35 = f.read().strip()
                if os.path.exists(entry + "/sens4.txt"):
                    f = open(entry + "/sens4.txt", "r")
                    sens4 = f.read().strip()
                if os.path.exists(entry + "/sens5.txt"):
                    f = open(entry + "/sens5.txt", "r")
                    sens5 = f.read().strip()
                res=entry + " " + source + " " + str(data['sources'][source]['ts']) + " " + str(data['sources'][source]['npred']) + " " + str(data['sources'][source]['flux']) + " " + str(data['sources'][source]['flux_err']) + " " + str(data['sources'][source]['flux_ul95']) + " " + str(data['sources'][source]['flux100_ul95']) + " " + str(data['sources'][source]['eflux']) + " " + str(data['sources'][source]['eflux_err']) + " " + str(data['sources'][source]['eflux100']) + " " + str(data['sources'][source]['eflux100_err']) + " " + str(data['sources'][source]['eflux_ul95']) + " " + str(sens3) + " " + str(sens35) + " " + str(sens4) + " " + str(sens5)
                file.write(res + "\n")
                if(data['sources'][source]['ts'] > 8.5):
                     print(res)
 
if __name__ == "__main__":
    name = sys.argv[1]
    source = str(sys.argv[2])
    print(source)
    file = open(name+"_"+source+".txt", "w")
    collect_data(name, source)
    file.close()
    ###ordering data###
    file = open(name+"_"+source+".txt", "r")
    lines = file.readlines()
    file.close
    file = open(name+"_"+source+".txt", "w")
    file.write("folder sources ts npred flux flux_err flux_ul95 flux100_ul95 eflux eflux_err eflux100 eflux100_err eflux_ul95 sens3 sens35 sens4 sens5\n")
    lines.sort()
    for line in lines:
        file.write(line)
    file.close()

