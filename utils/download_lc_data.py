import os

filename = 'igrj17354-3255_lightcurve*'
abspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/'
store = os.path.join(abspath, 'store_lc_data')
if os.path.isdir(store):
    os.system('rm -r ' + str(store))
os.mkdir(store)
# list of subdir in abspath
for year in os.listdir(abspath):
    if 'YEARS5' in year and '.old' not in year:
        print('create folder in store:', year)
        os.mkdir(os.path.join(store, year))
        print('copy fullLC.')
        os.system('cp ' + str(os.path.join(abspath, year, filename)) + ' ' + str(os.path.join(store, year)))
        for month in os.listdir(os.path.join(abspath, year)):
            if '.' not in month and 'README' not in month and 'M' in month:
                print('create subfolder in store:',  month)
                os.mkdir(os.path.join(store, year, month))
                print('copy month LC')
                os.system('cp ' + str(os.path.join(abspath, year, month, filename)) + ' ' + str(os.path.join(store, year, month)))
                print('copy month npy')
                os.system('cp ' + str(os.path.join(abspath, year, month, '*.npy')) + ' ' + str(os.path.join(store, year, month)))
                for day in os.listdir(os.path.join(abspath, year, month)):
                    if '.' not in day and 'lightcurve_' in day:
                        print('create subfolder in store:',  day)
                        os.mkdir(os.path.join(store, year, month, day))
                        print('copy day xml')
                        os.system('cp ' + str(os.path.join(abspath, year, month, day, '*.xml')) + ' ' + str(os.path.join(store, year, month, day)))

