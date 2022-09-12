import numpy as np
from utils.functions import mjd_to_met, met_to_mjd

def run_conversion_check():
    time = 51910
    ssdc = 0.
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(mjd_to_met(time))-ssdc)
    time = 54683
    ssdc = 239587201.
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(mjd_to_met(time))-ssdc)
    time = 56426
    ssdc = 390182403.
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(mjd_to_met(time))-ssdc)
    time = 57000
    ssdc = 439776003.
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(mjd_to_met(time))-ssdc)
    time = 58700
    ssdc = 586656005.
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(mjd_to_met(time))-ssdc)
    time = 59091
    ssdc = 620438405.
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(mjd_to_met(time))-ssdc)

    diff_met = 5
    diff_mjd = diff_met / (59091 - 51910)
    print(diff_mjd)

    time = 0.
    ssdc = 51910
    print('check conversion:', time, 'MJD = ', np.around(met_to_mjd(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(met_to_mjd(time))-ssdc)
    time = 239587201.
    ssdc = 54683
    print('check conversion:', time, 'MJD = ', np.around(met_to_mjd(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(met_to_mjd(time))-ssdc)
    time = 390182403.
    ssdc = 56426
    print('check conversion:', time, 'MJD = ', np.around(mjd_to_met(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(met_to_mjd(time))-ssdc)
    time = 439776003.
    ssdc = 57000
    print('check conversion:', time, 'MJD = ', np.around(met_to_mjd(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(met_to_mjd(time))-ssdc)
    time = 586656005.
    ssdc = 58700
    print('check conversion:', time, 'MJD = ', np.around(met_to_mjd(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(met_to_mjd(time))-ssdc)
    time = 620438405.
    ssdc = 59091
    print('check conversion:', time, 'MJD = ', np.around(met_to_mjd(time)), 'MET = ', ssdc, 'SSDC') 
    print('diff:', np.around(met_to_mjd(time))-ssdc)
