import numpy as np

def get_lc_data(file_path, period):
    lc_data = np.loadtxt(file_path)
    mjd, mag, err = lc_data[:, 0], lc_data[:, 1], lc_data[:, 2]
    phi1 = np.mod(mjd, period)/period
    I1 = np.argsort(phi1)
    phi2 = np.mod(mjd, 2.*period)/(2.*period)
    I2 = np.argsort(phi2)
    return np.hstack((phi1[I1], phi1[I1]+1., phi2[I2]+2, phi2[I2]+3)), \
            np.hstack((mag[I1], mag[I1], mag[I2], mag[I2])), \
            np.hstack((err[I1], err[I1], err[I2], err[I2]))
