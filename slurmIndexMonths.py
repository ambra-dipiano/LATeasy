import sys
from os import listdir, system
from os.path import isfile, join

if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    folder = 'YEARS5h'
path = '/data01/projects/IGRJ17354-3255/FERMI/LC/' + folder
logs = [f for f in listdir(path) if 'slurm' in f and 'index' not in f and 'M' not in f and isfile(join(path, f))]

# write index
indexfile = join(path, 'slurm-index.txt')
print(indexfile)
hdr = 'slurm-id.out month tstart tstop\n'
with open(indexfile, 'w+') as f:
    f.write(hdr)
for f in logs:
    line = open(join(path,f), 'r').readlines()[0]
    month = line[31:-7]
    tstart = month[5:14]
    tstop = month[15:]
    print(f, month, tstart, tstop)
    with open(indexfile, 'a') as index:
        index.write(str(str(f) + ' ' + month + ' ' + tstart + ' ' + tstop + '\n'))

# rename slurm
for i, f in enumerate(logs):
    if i == len(logs)-1:
        break
    else:
        line = open(join(path,f), 'r').readlines()[0]
        month = line[31:-7]
        system('mv ' + str(join(path,f)) + ' ' + str(join(path, 'slurm-%s.out' %month)))

logs = [f for f in listdir(path) if 'slurm' in f and 'index' not in f and 'M' in f and isfile(join(path, f))]
# write index
indexfile = join(path.replace(folder, ''), 'igrMonthsIndex.out')
print(indexfile)
hdr = 'slurm-id.out month tstart tstop\n'
with open(indexfile, 'w+') as f:
    f.write(hdr)
for f in logs:
    line = open(join(path,f), 'r').readlines()[0]
    month = line[31:-7]
    tstart = month[5:14]
    tstop = month[15:]
    print(f, month, tstart, tstop)
    with open(indexfile, 'a') as index:
        index.write(str(str(f) + ' ' + month + ' ' + tstart + ' ' + tstop + '\n'))
