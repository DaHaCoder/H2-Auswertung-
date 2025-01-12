### matplotlib package -- https://matplotlib.org/4.5.0/index.html ###
from matplotlib import pyplot as plt        #   for plots -- https://matplotlib.org/3.5.0/api/pyplot_summary.html
from matplotlib import rc                   #   for rcParams -- https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.pyplot.rc.html 
from matplotlib.patches import Rectangle    #   for plotting a rectangle -- https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html

### numpy package -- https://numpy.org/doc/stable/ ###
import numpy as np                          #   for general scientific computing
 
### scipy package -- https://docs.scipy.org/doc/scipy/reference/index.html ###
from scipy import constants as const        #   for physical constants -- https://docs.scipy.org/doc/scipy/reference/constants.html 
from scipy import optimize as opt           #   for optimization and fit -- https://docs.scipy.org/doc/scipy/reference/tutorial/optimize.html
from scipy import special as sp             #   for special mathematical functions -- https://docs.scipy.org/doc/scipy/reference/tutorial/special.html

#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'],'size':'20'})
## for 'Latin Modern' and other serif fonts use:
rc('font',**{'family':'serif','serif':['Latin Modern'], 'size':'16'})
rc('text', usetex=True)
plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]

def find_local_maxima(thresh: float, time: np.ndarray, voltage: np.ndarray) -> np.ndarray:
    local_maxima = []
    new_maximum = True

    for i, v in enumerate(voltage):
        if new_maximum and v > thresh:
            local_maxima.append(i)
            new_maximum = False
        elif not new_maximum:
            if v > voltage[local_maxima[-1]]:
                local_maxima[-1] = i
            elif v <= thresh:
                new_maximum = True

    return local_maxima

def gauss_2_fit_func(nu, u_0_1, nu_0_1, delta_nu_1, u_0_2, nu_0_2, delta_nu_2, u_y):
    return u_0_1*np.exp(-((nu - nu_0_1)/(delta_nu_1/(2.0*np.sqrt(np.log(2.0)))))**2.0) + u_0_2*np.exp(-((nu - nu_0_2)/(delta_nu_2/(2.0*np.sqrt(np.log(2.0)))))**2.0) + u_y

def gauss_1_fit_func(nu, I_0, nu_0, delta_nu, I_y):
    return I_0*np.exp(-((nu - nu_0)/(delta_nu/(2.0*np.sqrt(np.log(2.0)))))**2.0) + I_y

def lorentz_2_fit_func(nu, v_0_1, nu_0_1, gamma_1, v_0_2, nu_0_2, gamma_2, v_0_3, nu_0_3, gamma_3, v_0_4, nu_0_4, gamma_4, v_0_5, nu_0_5, gamma_5, v_0_6, nu_0_6, gamma_6, v_y):
    return v_0_1/np.pi*(gamma_1/2.0)/((nu - nu_0_1)**2.0 + (gamma_1/2.0)**2.0) + v_0_2/np.pi*(gamma_2/2.0)/((nu - nu_0_2)**2.0 + (gamma_2/2.0)**2.0) + v_0_3/np.pi*(gamma_3/2.0)/((nu - nu_0_3)**2.0 + (gamma_3/2.0)**2.0) + v_0_4/np.pi*(gamma_4/2.0)/((nu - nu_0_4)**2.0 + (gamma_4/2.0)**2.0) + v_0_5/np.pi*(gamma_5/2.0)/((nu - nu_0_5)**2.0 + (gamma_5/2.0)**2.0) + v_0_6/np.pi*(gamma_6/2.0)/((nu - nu_0_6)**2.0 + (gamma_6/2.0)**2.0) + v_y

def lorentz_1_fit_func(nu, I_0, nu_0, gamma, I_y):
    return I_0/np.pi*(gamma/2.0)*1.0/((nu - nu_0)**2.0 + (gamma/2.0)**2.0) + I_y

def time_to_freq(t, c, d, mean_delta_t):
    return c/(4.0*d)*1.0/mean_delta_t*t

def freq_to_time(nu, c, d, mean_delta_t):
    return (4.0*d)/c*mean_delta_t*nu

def main():
    DATA_DIR = "../data/data20-gain30-01.csv"
    data = np.loadtxt(DATA_DIR, delimiter=",", skiprows=2)

    time = np.array(data[:,0])
    voltage_1 = np.array(data[:,1])
    voltage_3 = np.array(data[:,3])
    
    local_maxima = find_local_maxima(3e-2, time, voltage_1)
    time_distances = []
    
    for i in range(len(time[local_maxima])-1):
        t1 = time[local_maxima][i]
        t2 = time[local_maxima][i+1]

        delta_t = t2 - t1
        time_distances.append(delta_t)
    
    mean_delta_t = 1/len(time_distances)*np.sum(np.array(time_distances))

    d = 0.1
    c = const.c
    kB = const.k
    mass_Rb_85 = 1.409993199*10**(-25)              #   atomic mass of Rb85 in kg -- https://www.steck.us/alkalidata/rubidium85numbers.pdf
    mass_Rb_87 = 1.443160648*10**(-25)              #   atomic mass of Rb87 in kg -- https://www.steck.us/alkalidata/rubidium87numbers.pdf

    LIST_nu_0_dip_1 = []
    LIST_delta_nu_dip_1 = []
    LIST_gamma_dip_1 = []

    LIST_nu_0_dip_2 = []
    LIST_delta_nu_dip_2 = []
    LIST_gamma_dip_2 = []

    LIST_both_dips_parameters_guess = []
    LIST_both_dips_parameters = []
    
    LIST_all_peaks_dip_1_parameters_guess = []
    LIST_all_peaks_dip_1_parameters = []

    LIST_all_peaks_dip_2_parameters_guess = []
    LIST_all_peaks_dip_2_parameters = []

    ### =============== ###
    ### INITIAL GUESSES ###
    ### =============== ###

    #   FOR DIP #1
    #   ==========

    #   initial guess and mask for peak #1
    #   ==================================
    p0_1_dip_1 = [1.0, 0.01121, 1e-6, 0.98]              #   I_0, nu_0, gamma, I_y
    t_init_1_dip_1 = 0.01118
    t_end_1_dip_1 = 0.01123
    mask_1_dip_1 = (time > t_init_1_dip_1) & (time < t_end_1_dip_1)

    #   initial guess and mask for peak #2
    #   ==================================
    p0_2_dip_1 = [1.0, 0.011275, 1e-6, 0.98]             #   I_0, nu_0, gamma, I_y
    t_init_2_dip_1 = 0.01125
    t_end_2_dip_1 = 0.01129
    mask_2_dip_1 = (time > t_init_2_dip_1) & (time < t_end_2_dip_1)

    #   initial guess and mask for peak #3
    #   ==================================
    p0_3_dip_1 = [1.0, 0.011355, 1e-6, 1.0]              #   I_0, nu_0, gamma, I_y
    t_init_3_dip_1 = 0.01134
    t_end_3_dip_1 = 0.011367
    mask_3_dip_1 = (time > t_init_3_dip_1) & (time < t_end_3_dip_1)

    #   initial guess and mask for peak #4
    #   ==================================
    p0_4_dip_1 = [1.0, 0.0114, 1e-6, 1.0]                #   I_0, nu_0, gamma, I_y
    t_init_4_dip_1 = 0.011395
    t_end_4_dip_1 = 0.01141
    mask_4_dip_1 = (time > t_init_4_dip_1) & (time < t_end_4_dip_1)

    #   initial guess and mask for peak #5
    #   ==================================
    p0_5_dip_1 = [1.0, 0.01147, 1e-6, 1.0]               #   I_0, nu_0, gamma, I_y
    t_init_5_dip_1 = 0.01145
    t_end_5_dip_1 = 0.01149
    mask_5_dip_1 = (time > t_init_5_dip_1) & (time < t_end_5_dip_1)

    #   initial guess and mask for peak #6
    #   ==================================
    p0_6_dip_1 = [1.0, 0.011615, 1e-6, 1.0]              #   I_0, nu_0, gamma, I_y
    t_init_6_dip_1 = 0.011605
    t_end_6_dip_1 = 0.01162
    mask_6_dip_1 = (time > t_init_6_dip_1) & (time < t_end_6_dip_1)
    

    #   initial guess and mask for dip #1
    #   =================================
    p0_dip_1 = [-1.0, 0.0115, 0.00001, 0.06]             #   I_0, nu_0, delta_nu, I_y 
    t_init_dip_1 = 0.0111
    t_end_dip_1 = 0.0120 
    mask_dip_1 = (time > t_init_dip_1) & (time < t_end_dip_1)


    #   FOR DIP #2
    #   ==========

    #   initial guess and mask for peak #1
    #   ==================================
    p0_1_dip_2 = [1.0, 0.01243, 1e-7, 1.0]               #   I_0, nu_0, gamma, I_y
    t_init_1_dip_2 = 0.01241
    t_end_1_dip_2 = 0.01244
    mask_1_dip_2 = (time > t_init_1_dip_2) & (time < t_end_1_dip_2)

    #   initial guess and mask for peak #2
    #   ==================================
    p0_2_dip_2 = [1.0, 0.012462, 1e-6, 1.0]              #   I_0, nu_0, gamma, I_y
    t_init_2_dip_2 = 0.012455
    t_end_2_dip_2 = 0.01247
    mask_2_dip_2 = (time > t_init_2_dip_2) & (time < t_end_2_dip_2)

    #   initial guess and mask for peak #3
    #   ==================================
    p0_3_dip_2 = [1.0, 0.012495, 1e-6, 1.0]              #   I_0, nu_0, gamma, I_y
    t_init_3_dip_2 = 0.01248
    t_end_3_dip_2 = 0.01250
    mask_3_dip_2 = (time > t_init_3_dip_2) & (time < t_end_3_dip_2)

    #   initial guess and mask for peak #4
    #   ==================================
    p0_4_dip_2 = [1.0, 0.012518, 1e-6, 1.0]              #   I_0, nu_0, gamma, I_y
    t_init_4_dip_2 = 0.012505
    t_end_4_dip_2 = 0.01253
    mask_4_dip_2 = (time > t_init_4_dip_2) & (time < t_end_4_dip_2)

    #   initial guess and mask for peak #5
    #   ==================================
    p0_5_dip_2 = [1.0, 0.012543, 1e-5, 1.0]              #   I_0, nu_0, gamma, I_y
    t_init_5_dip_2 = 0.012535
    t_end_5_dip_2 = 0.012555
    mask_5_dip_2 = (time > t_init_5_dip_2) & (time < t_end_5_dip_2)

    #   initial guess and mask for peak #6
    #   ==================================
    p0_6_dip_2 = [1.0, 0.01259, 1e-6, 1.0]               #   I_0, nu_0, gamma, I_y
    t_init_6_dip_2 = 0.012585
    t_end_6_dip_2 = 0.012595
    mask_6_dip_2 = (time > t_init_6_dip_2) & (time < t_end_6_dip_2)
    

    #   initial guess and mask for dip #2
    #   =================================
    p0_dip_2 = [-1.0, 0.0126, 0.00001, 0.03]             #   I_0, nu_0, delta_nu, I_y 
    t_init_dip_2 = 0.01215
    t_end_dip_2 = 0.01298 
    mask_dip_2 = (time > t_init_dip_2) & (time < t_end_dip_2)


    ### ==== ###
    ### FITS ###
    ### ==== ###   


    #   gauss fit for dip #1
    #   ====================
    popt, pcov = opt.curve_fit(gauss_1_fit_func, time[mask_dip_1], voltage_3[mask_dip_1], p0_dip_1)
    I_0, nu_0, delta_nu, I_y = popt

    LIST_both_dips_parameters_guess.append(popt[0])
    LIST_both_dips_parameters_guess.append(popt[1])
    LIST_both_dips_parameters_guess.append(popt[2])

    print("\n=== PARAMETERS FOR GAUSS FIT - DIP #1 ===")
    print("=========================================")
    print("I_0, nu_0, delta_nu, I_y = ", popt)
    voltage_3_dip_1_gauss_1_fit = gauss_1_fit_func(time, *popt)

    voltage_3_dip_1_normalized_1 = voltage_3/voltage_3_dip_1_gauss_1_fit


    #   gauss fit for dip #2
    #   ====================
    popt, pcov = opt.curve_fit(gauss_1_fit_func, time[mask_dip_2], voltage_3[mask_dip_2], p0_dip_2)
    I_0, nu_0, delta_nu, I_y = popt

    LIST_both_dips_parameters_guess.append(popt[0])
    LIST_both_dips_parameters_guess.append(popt[1])
    LIST_both_dips_parameters_guess.append(popt[2])
    LIST_both_dips_parameters_guess.append(popt[3])

    print("\n=== PARAMETERS FOR GAUSS FIT - DIP #2 ===")
    print("=========================================")
    print("I_0, nu_0, delta_nu, I_y = ", popt)
    voltage_3_dip_2_gauss_1_fit = gauss_1_fit_func(time, *popt)

    voltage_3_dip_2_normalized_1 = voltage_3/voltage_3_dip_2_gauss_1_fit

    
    #   fit for dip #1 and dip #2 together
    #   ==================================

    popt_both_dips, pcov_both_dips = opt.curve_fit(gauss_2_fit_func, time, voltage_3, LIST_both_dips_parameters_guess)
    u_1, nu_0_1, delta_nu_1, u_2, nu_0_2, delta_nu_2, u_0 = popt_both_dips

    print("\n=== PARAMETERS FOR BOTH DIPS, DIP #1 AND DIP #2 ===")
    print("===================================================")
    print("u_1, nu_0_1, delta_nu_1, u_2, nu_0_2, delta_nu_2, u_0 = ", popt_both_dips)
    LIST_both_dips_parameters.append(popt_both_dips.tolist())

    voltage_3_gauss_2_fit = gauss_2_fit_func(time, *popt_both_dips)
    
    voltage_3_normalized_2 = voltage_3/voltage_3_gauss_2_fit


    #   FOR DIP #1
    #   ==========
    
    #   fit for peak #1
    #   ================
    popt_1, pcov_1 = opt.curve_fit(lorentz_1_fit_func, time[mask_1_dip_1], voltage_3_dip_1_normalized_1[mask_1_dip_1], p0_1_dip_1)
    I_0, nu_0, gamma, I_y = popt_1

    print("\n=== PARAMETERS FOR PEAK #1 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_1)
    LIST_nu_0_dip_1.append(popt_1[1])
    LIST_gamma_dip_1.append(popt_1[2])

    LIST_all_peaks_dip_1_parameters_guess.append(popt_1[0])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_1[1])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_1[2])
    
    time_new_1_dip_1 = np.linspace(t_init_1_dip_1, t_end_1_dip_1, 1000)
    voltage_3_fit_peak_1_dip_1 = lorentz_1_fit_func(time_new_1_dip_1, *popt_1)

    #   fit for peak #2
    #   ================
    popt_2, pcov_2 = opt.curve_fit(lorentz_1_fit_func, time[mask_2_dip_1], voltage_3_dip_1_normalized_1[mask_2_dip_1], p0_2_dip_1)
    I_0, nu_0, gamma, I_y = popt_2

    print("\n=== PARAMETERS FOR PEAK #2 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_2)
    LIST_nu_0_dip_1.append(popt_2[1])
    LIST_gamma_dip_1.append(popt_2[2])

    LIST_all_peaks_dip_1_parameters_guess.append(popt_2[0])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_2[1])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_2[2])
    
    time_new_2_dip_1 = np.linspace(t_init_2_dip_1, t_end_2_dip_1, 1000)
    voltage_3_fit_peak_2_dip_1 = lorentz_1_fit_func(time_new_2_dip_1, *popt_2)

    #   fit for peak #3
    #   ================
    popt_3, pcov_3 = opt.curve_fit(lorentz_1_fit_func, time[mask_3_dip_1], voltage_3_dip_1_normalized_1[mask_3_dip_1], p0_3_dip_1)
    I_0, nu_0, gamma, I_y = popt_3

    print("\n=== PARAMETERS FOR PEAK #3 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_3)
    LIST_nu_0_dip_1.append(popt_3[1])
    LIST_gamma_dip_1.append(popt_3[2])

    LIST_all_peaks_dip_1_parameters_guess.append(popt_3[0])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_3[1])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_3[2])

    time_new_3_dip_1 = np.linspace(t_init_3_dip_1, t_end_3_dip_1, 1000)
    voltage_3_fit_peak_3_dip_1 = lorentz_1_fit_func(time_new_3_dip_1, *popt_3)

    #   fit for peak #4
    #   ================
    popt_4, pcov_4 = opt.curve_fit(lorentz_1_fit_func, time[mask_4_dip_1], voltage_3_dip_1_normalized_1[mask_4_dip_1], p0_4_dip_1)
    I_0, nu_0, gamma, I_y = popt_4

    print("\n=== PARAMETERS FOR PEAK #4 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_4)
    LIST_nu_0_dip_1.append(popt_4[1])
    LIST_gamma_dip_1.append(popt_4[2])

    LIST_all_peaks_dip_1_parameters_guess.append(popt_4[0])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_4[1])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_4[2])

    time_new_4_dip_1 = np.linspace(t_init_4_dip_1, t_end_4_dip_1, 1000)
    voltage_3_fit_peak_4_dip_1 = lorentz_1_fit_func(time_new_4_dip_1, *popt_4)
    
    #   fit for peak #5
    #   ================
    popt_5, pcov_5 = opt.curve_fit(lorentz_1_fit_func, time[mask_5_dip_1], voltage_3_dip_1_normalized_1[mask_5_dip_1], p0_5_dip_1)
    I_0, nu_0, gamma, I_y = popt_5

    print("\n=== PARAMETERS FOR PEAK #5 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_5)
    LIST_nu_0_dip_1.append(popt_5[1])
    LIST_gamma_dip_1.append(popt_5[2])
    
    LIST_all_peaks_dip_1_parameters_guess.append(popt_5[0])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_5[1])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_5[2])

    time_new_5_dip_1 = np.linspace(t_init_5_dip_1, t_end_5_dip_1, 1000)
    voltage_3_fit_peak_5_dip_1 = lorentz_1_fit_func(time_new_5_dip_1, *popt_5)

    #   fit for peak #6
    #   ================
    popt_6, pcov_6 = opt.curve_fit(lorentz_1_fit_func, time[mask_6_dip_1], voltage_3_dip_1_normalized_1[mask_6_dip_1], p0_6_dip_1)
    I_0, nu_0, gamma, I_y = popt_6

    print("\n=== PARAMETERS FOR PEAK #6 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_6)
    LIST_nu_0_dip_1.append(popt_6[1])
    LIST_gamma_dip_1.append(popt_6[2])

    LIST_all_peaks_dip_1_parameters_guess.append(popt_6[0])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_6[1])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_6[2])
    LIST_all_peaks_dip_1_parameters_guess.append(popt_6[3])

    time_new_6_dip_1 = np.linspace(t_init_6_dip_1, t_end_6_dip_1, 1000)
    voltage_3_fit_peak_6_dip_1 = lorentz_1_fit_func(time_new_6_dip_1, *popt_6)

    #   fit for all peaks in dip #1
    #   ===========================

    popt_all_peaks_dip_1, pcov_all_peaks_dip_1 = opt.curve_fit(lorentz_2_fit_func, time, voltage_3_normalized_2, LIST_all_peaks_dip_1_parameters_guess)
    v_0_1, nu_0_1, gamma_1, v_0_2, nu_0_2, gamma_2, v_0_3, nu_0_3, gamma_3, v_0_4, nu_0_4, gamma_4, v_0_5, nu_0_5, gamma_5, v_0_6, nu_0_6, gamma_6, v_y = popt_all_peaks_dip_1

    print("\n=== PARAMETERS FOR ALL PEAKS - DIP #1 ===")
    print("==========================================")
    print("v_0_1, nu_0_1, gamma_1, v_0_2, nu_0_2, gamma_2, v_0_3, nu_0_3, gamma_3, v_0_4, nu_0_4, gamma_4, v_0_5, nu_0_5, gamma_5, v_0_6, nu_0_6, gamma_6, v_y = ", popt_all_peaks_dip_1)

    voltage_3_fit_all_peaks_dip_1 = lorentz_2_fit_func(time, *popt_all_peaks_dip_1)

    
    #   FOR DIP #2
    #   ==========
    
    #   fit for peak #1
    #   ================
    popt_1, pcov_1 = opt.curve_fit(lorentz_1_fit_func, time[mask_1_dip_2], voltage_3_dip_2_normalized_1[mask_1_dip_2], p0_1_dip_2)
    I_0, nu_0, gamma, I_y = popt_1

    print("\n=== PARAMETERS FOR PEAK #1 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_1)
    LIST_nu_0_dip_2.append(popt_1[1])
    LIST_gamma_dip_2.append(popt_1[2])
    
    LIST_all_peaks_dip_2_parameters_guess.append(popt_1[0])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_1[1])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_1[2])
    
    time_new_1_dip_2 = np.linspace(t_init_1_dip_2, t_end_1_dip_2, 1000)
    voltage_3_fit_peak_1_dip_2 = lorentz_1_fit_func(time_new_1_dip_2, *popt_1)

    #   fit for peak #2
    #   ================
    popt_2, pcov_2 = opt.curve_fit(lorentz_1_fit_func, time[mask_2_dip_2], voltage_3_dip_2_normalized_1[mask_2_dip_2], p0_2_dip_2)
    I_0, nu_0, gamma, I_y = popt_2

    print("\n=== PARAMETERS FOR PEAK #2 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_2)
    LIST_nu_0_dip_2.append(popt_2[1])
    LIST_gamma_dip_2.append(popt_2[2])

    LIST_all_peaks_dip_2_parameters_guess.append(popt_2[0])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_2[1])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_2[2])

    time_new_2_dip_2 = np.linspace(t_init_2_dip_2, t_end_2_dip_2, 1000)
    voltage_3_fit_peak_2_dip_2 = lorentz_1_fit_func(time_new_2_dip_2, *popt_2)

    #   fit for peak #3
    #   ================
    popt_3, pcov_3 = opt.curve_fit(lorentz_1_fit_func, time[mask_3_dip_2], voltage_3_dip_2_normalized_1[mask_3_dip_2], p0_3_dip_2)
    I_0, nu_0, gamma, I_y = popt_3

    print("\n=== PARAMETERS FOR PEAK #3 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_3)
    LIST_nu_0_dip_2.append(popt_3[1])
    LIST_gamma_dip_2.append(popt_3[2])

    LIST_all_peaks_dip_2_parameters_guess.append(popt_3[0])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_3[1])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_3[2])
    
    time_new_3_dip_2 = np.linspace(t_init_3_dip_2, t_end_3_dip_2, 1000)
    voltage_3_fit_peak_3_dip_2 = lorentz_1_fit_func(time_new_3_dip_2, *popt_3)

    #   fit for peak #4
    #   ================
    popt_4, pcov_4 = opt.curve_fit(lorentz_1_fit_func, time[mask_4_dip_2], voltage_3_dip_2_normalized_1[mask_4_dip_2], p0_4_dip_2)
    I_0, nu_0, gamma, I_y = popt_4

    print("\n=== PARAMETERS FOR PEAK #4 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_4)
    LIST_nu_0_dip_2.append(popt_4[1])
    LIST_gamma_dip_2.append(popt_4[2])

    LIST_all_peaks_dip_2_parameters_guess.append(popt_4[0])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_4[1])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_4[2])

    time_new_4_dip_2 = np.linspace(t_init_4_dip_2, t_end_4_dip_2, 1000)
    voltage_3_fit_peak_4_dip_2 = lorentz_1_fit_func(time_new_4_dip_2, *popt_4)
    
    #   fit for peak #5
    #   ================
    popt_5, pcov_5 = opt.curve_fit(lorentz_1_fit_func, time[mask_5_dip_2], voltage_3_dip_2_normalized_1[mask_5_dip_2], p0_5_dip_2)
    I_0, nu_0, gamma, I_y = popt_5

    print("\n=== PARAMETERS FOR PEAK #5 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_5)
    LIST_nu_0_dip_2.append(popt_5[1])
    LIST_gamma_dip_2.append(popt_5[2])

    LIST_all_peaks_dip_2_parameters_guess.append(popt_5[0])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_5[1])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_5[2])
    
    time_new_5_dip_2 = np.linspace(t_init_5_dip_2, t_end_5_dip_2, 1000)
    voltage_3_fit_peak_5_dip_2 = lorentz_1_fit_func(time_new_5_dip_2, *popt_5)

    #   fit for peak #6
    #   ================
    popt_6, pcov_6 = opt.curve_fit(lorentz_1_fit_func, time[mask_6_dip_2], voltage_3_dip_2_normalized_1[mask_6_dip_2], p0_6_dip_2)
    I_0, nu_0, gamma, I_y = popt_6

    print("\n=== PARAMETERS FOR PEAK #6 ===")
    print("==============================")
    print("I_0, nu_0, gamma, I_y = ", popt_6)
    LIST_nu_0_dip_2.append(popt_6[1])
    LIST_gamma_dip_2.append(popt_6[2])

    LIST_all_peaks_dip_2_parameters_guess.append(popt_6[0])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_6[1])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_6[2])
    LIST_all_peaks_dip_2_parameters_guess.append(popt_6[3])

    time_new_6_dip_2 = np.linspace(t_init_6_dip_2, t_end_6_dip_2, 1000)
    voltage_3_fit_peak_6_dip_2 = lorentz_1_fit_func(time_new_6_dip_2, *popt_6)

    #   fit for all peaks in dip #2
    #   ===========================

    popt_all_peaks_dip_2, pcov_all_peaks_dip_2 = opt.curve_fit(lorentz_2_fit_func, time, voltage_3_normalized_2, LIST_all_peaks_dip_2_parameters_guess)
    v_0_1, nu_0_1, gamma_1, v_0_2, nu_0_2, gamma_2, v_0_3, nu_0_3, gamma_3, v_0_4, nu_0_4, gamma_4, v_0_5, nu_0_5, gamma_5, v_0_6, nu_0_6, gamma_6, v_y = popt_all_peaks_dip_2

    print("\n=== PARAMETERS FOR ALL PEAKS - DIP #2 ===")
    print("==========================================")
    print("v_0_1, nu_0_1, gamma_1, v_0_2, nu_0_2, gamma_2, v_0_3, nu_0_3, gamma_3, v_0_4, nu_0_4, gamma_4, v_0_5, nu_0_5, gamma_5, v_0_6, nu_0_6, gamma_6, v_y = ", popt_all_peaks_dip_2)

    voltage_3_fit_all_peaks_dip_2 = lorentz_2_fit_func(time, *popt_all_peaks_dip_2)

    
    #   fit for dip #1 and dip #2 together
    #   ==================================

    popt_both_dips, pcov_both_dips = opt.curve_fit(gauss_2_fit_func, time, voltage_3, LIST_both_dips_parameters_guess)
    u_1, nu_0_1, delta_nu_1, u_2, nu_0_2, delta_nu_2, u_0 = popt_both_dips

    print("\n=== PARAMETERS FOR BOTH DIPS, DIP #1 AND DIP #2 ===")
    print("===================================================")
    print("u_1, nu_0_1, delta_nu_1, u_2, nu_0_2, delta_nu_2, u_0 = ", popt_both_dips)
    LIST_both_dips_parameters.append(popt_both_dips.tolist())

    voltage_3_fit_dip_1_dip_2 = gauss_2_fit_func(time, *popt_both_dips)


    ### =============== ###
    ### ESTIMATED ERROR ###
    ### =============== ###

    print("\n=================================")
    print("=== ESTIMATED ERROR FOR GAMMA ===")
    print("=================================")
    
    #   FOR DIP #1
    #   ==========
    
    mean_gamma_dip_1 = 1/len(LIST_gamma_dip_1)*np.sum(np.array(LIST_gamma_dip_1))
    standard_dev_gamma_dip_1 = np.sqrt(1/len(LIST_gamma_dip_1)*np.sum((np.array(LIST_gamma_dip_1) - mean_gamma_dip_1)**2.0))

    print("\n=== FOR DIP #1 ===")
    print("===================")
    print("time_to_freq(np.array(LIST_gamma_dip_1), c, d, mean_delta_t) in MHz = ", time_to_freq(np.array(LIST_gamma_dip_1), c, d, mean_delta_t)*10**(-6))
    print("mean_gamma in MHz = ", time_to_freq(mean_gamma_dip_1, c, d, mean_delta_t)*10**(-6))
    print("standard_dev_gamma in MHz = ", time_to_freq(standard_dev_gamma_dip_1, c, d, mean_delta_t)*10**(-6))

    #   FOR DIP #2
    #   ==========
    
    mean_gamma_dip_2 = 1/len(LIST_gamma_dip_2)*np.sum(np.array(LIST_gamma_dip_2))
    standard_dev_gamma_dip_2 = np.sqrt(1/len(LIST_gamma_dip_2)*np.sum((np.array(LIST_gamma_dip_2) - mean_gamma_dip_2)**2.0))

    print("\n=== FOR DIP #2 ===")
    print("===================")
    print("time_to_freq(np.array(LIST_gamma_dip_2), c, d, mean_delta_t) in MHz = ", time_to_freq(np.array(LIST_gamma_dip_2), c, d, mean_delta_t)*10**(-6))
    print("mean_gamma in MHz = ", time_to_freq(mean_gamma_dip_2, c, d, mean_delta_t)*10**(-6))
    print("standard_dev_gamma in MHz = ", time_to_freq(standard_dev_gamma_dip_2, c, d, mean_delta_t)*10**(-6))


    ### ===== ###
    ### PLOTS ###
    ### ===== ###

    fig, ax = plt.subplots()

    #   plot raw data
    #   =============
    ax.plot(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3, color = 'tab:blue', label = 'Rohdaten')
    #ax.plot(time, voltage_3, color = 'tab:blue', label = 'Rohdaten')

    #   plot gauss fit for dip #1
    #   =========================
    ax.plot(time_to_freq(time, c, d, mean_delta_t)[mask_dip_1]*10**(-9), voltage_3_dip_1_gauss_1_fit[mask_dip_1], color = 'tab:cyan', linestyle = '--', linewidth = 1.0, label = 'Gauß-Fit (einzelnd)')
    #ax.plot(time[mask_dip_1], voltage_3_dip_1_gauss_fit[mask_dip_1], color = 'tab:cyan', label = 'Gauß-Fit (einzelnd)')

    #   plot gauss fit for dip #2
    #   =========================
    ax.plot(time_to_freq(time, c, d, mean_delta_t)[mask_dip_2]*10**(-9), voltage_3_dip_2_gauss_1_fit[mask_dip_2], color = 'tab:cyan', linestyle = '--', linewidth = 1.0)
    #ax.plot(time[mask_dip_2], voltage_3_dip_2_gauss_fit[mask_dip_2], color = 'tab:cyan')

    #   plot fit for both dips, dip #1 and dip #2
    #   =========================================
    ax.plot(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_fit_dip_1_dip_2, color = 'tab:orange', label = 'Gauß-Fit (zusammen)')
    #ax.plot(time, voltage_3_fit_dip_1_dip_2, color = 'tab:orange', label = 'Gauß-Fit (zusammen)')

    #   draw rectangles around peaks in dips
    #   ====================================
    x_rectangle_dip_1 = 0.01115
    y_rectangle_dip_1 = 0.065

    x_rectangle_to_dip_1 = 0.00050
    y_rectangle_to_dip_1 = 0.03

    x_rectangle_dip_2 = 0.0124
    y_rectangle_dip_2 = 0.032

    x_rectangle_to_dip_2 = 0.00022
    y_rectangle_to_dip_2 = 0.013

    ax.add_patch(Rectangle((time_to_freq(x_rectangle_dip_1, c, d, mean_delta_t)*10**(-9), y_rectangle_dip_1), time_to_freq(x_rectangle_to_dip_1, c, d, mean_delta_t)*10**(-9), y_rectangle_to_dip_1, edgecolor = 'tab:red', facecolor = 'none', linestyle = '--'))
    #ax.add_patch(Rectangle((x_rectangle_dip_1, y_rectangle_dip_1), x_rectangle_to_dip_1, y_rectangle_to_dip_1, edgecolor = 'tab:red', facecolor = 'none', linestyle = '--'))
    ax.add_patch(Rectangle((time_to_freq(x_rectangle_dip_2, c, d, mean_delta_t)*10**(-9), y_rectangle_dip_2), time_to_freq(x_rectangle_to_dip_2, c, d, mean_delta_t)*10**(-9), y_rectangle_to_dip_2, edgecolor = 'tab:green', facecolor = 'none', linestyle = '--'))
    #ax.add_patch(Rectangle((x_rectangle_dip_2, y_rectangle_dip_2), x_rectangle_to_dip_2, y_rectangle_to_dip_2, edgecolor = 'tab:green', facecolor = 'none', linestyle = '--'))
    
    ax.set_xlabel(r'Frequenz $\nu$ in GHz')
    #ax.set_xlabel(r'Zeit $t$ in s')
    ax.set_ylabel(r'Spannung $U$ in mV')
    #ax.set_title('Gain 30 in dB (01)')
   
    ymin = 0.025
    ymax = 0.11
    ax.set_ylim(ymin, ymax)

    ax.legend(loc = 'lower left')
    
    ax.grid(True)
    
    #plt.show()

    #   save figure with raw data and gauss fit
    #   =======================================
    fig.savefig("../report/figures/plots/PNG/plot-data20-gain30-01-rubidium.png", format = 'png', bbox_inches = 'tight', dpi = 400)
    #fig.savefig("../report/figures/plots/EPS/plot-data20-gain30-01-rubidium.eps", format = 'eps', bbox_inches = 'tight')
    fig.savefig("../report/figures/plots/PDF/plot-data20-gain30-01-rubidium.pdf", format = 'pdf', bbox_inches = 'tight')
    #tikplotlib.save("../report/figures/tikz/plot-data20-gain30-01-rubidium.tex")



    #   PEAKS IN DIP #1
    #   ===============

    fig, ax = plt.subplots()

    #   plot normalized data for peaks around dip #1
    #   ============================================
    ax.scatter(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_dip_1_normalized_1, color = 'blue', s = 0.1)  
    #ax.scatter(time, voltage_3_dip_1_normalized_1, color = 'blue', s = 0.1) 
    
    
    #   plot fit for peak #1
    #   ====================
    ax.plot(time_to_freq(time_new_1_dip_1, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_1_dip_1, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_1[0], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_1_dip_1, voltage_3_fit_peak_1_dip_1, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_1[0], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)

    #   plot fit for peak #2
    #   ====================
    ax.plot(time_to_freq(time_new_2_dip_1, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_2_dip_1, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_1[1], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_2_dip_1, voltage_3_fit_peak_2_dip_1, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_1[1], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)

    #   plot fit for peak #3
    #   ====================
    ax.plot(time_to_freq(time_new_3_dip_1, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_3_dip_1, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_1[2], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_3_dip_1, voltage_3_fit_peak_3_dip_1, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_1[2], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    
    #   plot fit for peak #4
    #   ====================
    ax.plot(time_to_freq(time_new_4_dip_1, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_4_dip_1, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_1[3], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_4_dip_1, voltage_3_fit_peak_4_dip_1, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_1[3], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    
    #   plot fit for peak #5
    #   ====================
    ax.plot(time_to_freq(time_new_5_dip_1, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_5_dip_1, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_1[4], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_5_dip_1, voltage_3_fit_peak_5_dip_1, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_1[4], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    
    #   plot fit for peak #6
    #   ====================
    ax.plot(time_to_freq(time_new_6_dip_1, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_6_dip_1, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_1[5], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_6_dip_1, voltage_3_fit_peak_6_dip_1, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_1[5], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    

    ax.set_xlabel(r'Frequenz $\nu$ in GHz')
    #ax.set_xlabel(r'Zeit $t$ in s')
    ax.set_ylabel(r'Spannungsverhältnis $U/U_{\text{fit}}$')
    
    xmin = 0.01115
    xmax = 0.01165
    ax.set_xlim(time_to_freq(xmin, c, d, mean_delta_t)*10**(-9), time_to_freq(xmax, c, d, mean_delta_t)*10**(-9))
    #ax.set_xlim(xmin, xmax)
    
    ymin = 0.96
    ymax = 1.14
    ax.set_ylim(ymin, ymax)
    
    ax.grid(True)
    #plt.show()


    #   save figure with normalized data and peak fits around dip #1
    #   ============================================================
    
    fig.savefig("../report/figures/plots/PNG/plot-data20-gain30-01-dip-1-rubidium-normalized-1-fit.png", format = 'png', bbox_inches = 'tight', dpi = 400)
    #fig.savefig("../report/figures/plots/EPS/plot-data20-gain30-dip-1-rubidium-normalized-1-fit.eps", format = 'eps', bbox_inches = 'tight')
    fig.savefig("../report/figures/plots/PDF/plot-data20-gain30-01-dip-1-rubidium-normalized-1-fit.pdf", format = 'pdf', bbox_inches = 'tight')
    #tikzplotlib.save("../report/figures/tikz/plot-data20-gain30-01-dip-1-rubidium-normalized-1-fit.tex")
   

    fig, ax = plt.subplots()

    #   plot normalized_2 data for peaks around dip #1
    #   ==============================================
    ax.scatter(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_normalized_2, color = 'blue', s = 0.1)
    #ax.scatter(time, voltage_3_normalized_2, color = 'blue', s = 0.1)

    #   plot fit for all peaks in dip #1
    #   ================================
    ax.plot(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_fit_all_peaks_dip_1, color = 'tab:orange')
    #ax.plot(time, voltage_3_fit_all_peaks_dip_1, color = 'tab:orange')
    
    ax.set_xlabel(r'Frequenz $\nu$ in GHz')
    #ax.set_xlabel(r'Zeit $t$ in s')
    ax.set_ylabel(r'Spannungsverhältnis $U/U_{\text{fit}}$')
    
    xmin = 0.01115
    xmax = 0.01165
    ax.set_xlim(time_to_freq(xmin, c, d, mean_delta_t)*10**(-9), time_to_freq(xmax, c, d, mean_delta_t)*10**(-9))
    #ax.set_xlim(xmin, xmax)
    
    ymin = 0.96
    ymax = 1.15
    ax.set_ylim(ymin, ymax)
    
    ax.grid(True)
    #plt.show()


    #   save figure with normalized_2 data and all peaks around dip #1
    #   ==============================================================
    
    fig.savefig("../report/figures/plots/PNG/plot-data20-gain30-01-dip-1-rubidium-normalized-2-fit.png", format = 'png', bbox_inches = 'tight', dpi = 400)
    #fig.savefig("../report/figures/plots/EPS/plot-data20-gain30-dip-1-rubidium-normalized-2-fit.eps", format = 'eps', bbox_inches = 'tight')
    fig.savefig("../report/figures/plots/PDF/plot-data20-gain30-01-dip-1-rubidium-normalized-2-fit.pdf", format = 'pdf', bbox_inches = 'tight')
    #tikzplotlib.save("../report/figures/tikz/plot-data20-gain30-01-dip-1-rubidium-normalized-2-fit.tex")



    #   PEAKS IN DIP 2
    #   ==============

    fig, ax = plt.subplots()

    #   plot normalized_1 data for peaks around dip #2
    #   ==============================================
    
    ax.scatter(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_dip_2_normalized_1, color = 'blue', s = 0.1)  
    #ax.scatter(time, voltage_3_dip_2_normalized_1, color = 'blue', s = 0.1) 
    
    
    #   plot fit for peak #1
    #   ====================
    ax.plot(time_to_freq(time_new_1_dip_2, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_1_dip_2, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_2[0], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_1_dip_2, voltage_3_fit_peak_1_dip_2, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_2[0], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)

    #   plot fit for peak #2
    #   ====================
    ax.plot(time_to_freq(time_new_2_dip_2, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_2_dip_2, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_2[1], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_2_dip_2, voltage_3_fit_peak_2_dip_2, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_2[1], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)

    #   plot fit for peak #3
    #   ====================
    ax.plot(time_to_freq(time_new_3_dip_2, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_3_dip_2, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_2[2], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_3_dip_2, voltage_3_fit_peak_3_dip_2, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_2[2], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    
    #   plot fit for peak #4
    #   ====================
    ax.plot(time_to_freq(time_new_4_dip_2, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_4_dip_2, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_2[3], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_4_dip_2, voltage_3_fit_peak_4_dip_2, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_2[3], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    
    #   plot fit for peak #5
    #   ====================
    ax.plot(time_to_freq(time_new_5_dip_2, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_5_dip_2, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_2[4], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_5_dip_2, voltage_3_fit_peak_5_dip_2, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_2[4], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    
    #   plot fit for peak #6
    #   ====================
    ax.plot(time_to_freq(time_new_6_dip_2, c, d, mean_delta_t)*10**(-9), voltage_3_fit_peak_6_dip_2, color = 'tab:orange')
    ax.vlines(time_to_freq(LIST_nu_0_dip_2[5], c, d, mean_delta_t)*10**(-9), 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    #ax.plot(time_new_6_dip_2, voltage_3_fit_peak_6_dip_2, color = 'tab:orange')
    #ax.vlines(LIST_nu_0_dip_2[5], 0, 1, transform = ax.get_xaxis_transform(), color = 'tab:green', linestyles = 'dashed', linewidth = 1)
    

    ax.set_xlabel(r'Frequenz $\nu$ in GHz')
    #ax.set_xlabel(r'Zeit $t$ in s')
    ax.set_ylabel(r'Spannungsverhältnis $U/U_{\text{fit}}$')
   
    xmin = 0.0124
    xmax = 0.01262
    ax.set_xlim(time_to_freq(xmin, c, d, mean_delta_t)*10**(-9), time_to_freq(xmax, c, d, mean_delta_t)*10**(-9))
    #ax.set_xlim(xmin, xmax)
    
    ymin = 0.95
    ymax = 1.3
    ax.set_ylim(ymin, ymax)
    
    ax.grid(True)
    #plt.show()


    #   save figure with normalized data and peak fits around dip #2
    #   ============================================================
    
    fig.savefig("../report/figures/plots/PNG/plot-data20-gain30-01-dip-2-rubidium-normalized-1-fit.png", format = 'png', bbox_inches = 'tight', dpi = 400)
    #fig.savefig("../report/figures/plots/EPS/plot-data20-gain30-dip-2-rubidium-normalized-1-fit.eps", format = 'eps', bbox_inches = 'tight')
    fig.savefig("../report/figures/plots/PDF/plot-data20-gain30-01-dip-2-rubidium-normalized-1-fit.pdf", format = 'pdf', bbox_inches = 'tight')
    #tikzplotlib.save("../report/figures/tikz/plot-data20-gain30-01-dip-2-rubidium-normalized-1-fit.tex")

    fig, ax = plt.subplots()

    #   plot normalized_2 data for peaks around dip #2
    #   ==============================================
    ax.scatter(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_normalized_2, color = 'blue', s = 0.1)
    #ax.scatter(time, voltage_3_normalized_2, color = 'blue', s = 0.1)

    #   plot fit for all peaks in dip #1
    #   ================================
    ax.plot(time_to_freq(time, c, d, mean_delta_t)*10**(-9), voltage_3_fit_all_peaks_dip_2, color = 'tab:orange')
    #ax.plot(time, voltage_3_fit_all_peaks_dip_1, color = 'tab:orange')
    
    ax.set_xlabel(r'Frequenz $\nu$ in GHz')
    #ax.set_xlabel(r'Zeit $t$ in s')
    ax.set_ylabel(r'Spannungsverhältnis $U/U_{\text{fit}}$')
    
    xmin = 0.0124
    xmax = 0.01262
    ax.set_xlim(time_to_freq(xmin, c, d, mean_delta_t)*10**(-9), time_to_freq(xmax, c, d, mean_delta_t)*10**(-9))
    #ax.set_xlim(xmin, xmax)
    
    ymin = 0.95
    ymax = 1.4
    ax.set_ylim(ymin, ymax)
    
    ax.grid(True)
    #plt.show()


    #   save figure with normalized_2 data and all peaks around dip #2
    #   ==============================================================
    
    fig.savefig("../report/figures/plots/PNG/plot-data20-gain30-01-dip-2-rubidium-normalized-2-fit.png", format = 'png', bbox_inches = 'tight', dpi = 400)
    #fig.savefig("../report/figures/plots/EPS/plot-data20-gain30-dip-2-rubidium-normalized-2-fit.eps", format = 'eps', bbox_inches = 'tight')
    fig.savefig("../report/figures/plots/PDF/plot-data20-gain30-01-dip-2-rubidium-normalized-2-fit.pdf", format = 'pdf', bbox_inches = 'tight')
    #tikzplotlib.save("../report/figures/tikz/plot-data20-gain30-01-dip-2-rubidium-normalized-2-fit.tex")



    ### ============================= ###
    ### CALCULATE FREQUENCY DISTANCES ### 
    ### ============================= ###

    print("\n=============================")
    print("CALCULATE FREQUENCY DISTANCES")
    print("=============================")
    
    #   DIP #1
    #   ======

    print("\n======")
    print("DIP #1")
    print("======")

    #   distance to peak #1
    #   ===================

    print("\n=== PEAK 1, 2 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[1] - LIST_nu_0_dip_1[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 3 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[2] - LIST_nu_0_dip_1[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 4 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[3] - LIST_nu_0_dip_1[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[4] - LIST_nu_0_dip_1[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[5] - LIST_nu_0_dip_1[0]), c, d, mean_delta_t)*10**(-6))
    
    #   distance to peak #2
    #   ===================
    
    print("\n=== PEAK 2, 3 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[2] - LIST_nu_0_dip_1[1]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 2, 4 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[3] - LIST_nu_0_dip_1[1]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 2, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[4] - LIST_nu_0_dip_1[1]), c, d, mean_delta_t)*10**(-6))

    print("\n=== PEAK 2, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[5] - LIST_nu_0_dip_1[1]), c, d, mean_delta_t)*10**(-6))
    
    #   distance to peak #3
    #   ===================
    
    print("\n=== PEAK 3, 4 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[3] - LIST_nu_0_dip_1[2]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 3, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[4] - LIST_nu_0_dip_1[2]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 3, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[5] - LIST_nu_0_dip_1[2]), c, d, mean_delta_t)*10**(-6))
    
    #   distance to peak #4
    #   ===================

    print("\n=== PEAK 4, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[4] - LIST_nu_0_dip_1[3]), c, d, mean_delta_t)*10**(-6))
   
    print("\n=== PEAK 4, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[5] - LIST_nu_0_dip_1[3]), c, d, mean_delta_t)*10**(-6))

    #   distance to peak #5
    #   ===================

    print("\n=== PEAK 5, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_1[5] - LIST_nu_0_dip_1[4]), c, d, mean_delta_t)*10**(-6))

    #   DIP #2
    #   ======

    print("\n======")
    print("DIP #2")
    print("======")

    #   distance to peak #1
    #   ===================

    print("\n=== PEAK 1, 2 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[1] - LIST_nu_0_dip_2[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 3 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[2] - LIST_nu_0_dip_2[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 4 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[3] - LIST_nu_0_dip_2[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[4] - LIST_nu_0_dip_2[0]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 1, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[5] - LIST_nu_0_dip_2[0]), c, d, mean_delta_t)*10**(-6))
    
    #   distance to peak #2
    #   ===================
    
    print("\n=== PEAK 2, 3 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[2] - LIST_nu_0_dip_2[1]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 2, 4 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[3] - LIST_nu_0_dip_2[1]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 2, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[4] - LIST_nu_0_dip_2[1]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 2, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[5] - LIST_nu_0_dip_2[1]), c, d, mean_delta_t)*10**(-6))

    #   distance to peak #3
    #   ===================
    
    print("\n=== PEAK 3, 4 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[3] - LIST_nu_0_dip_2[2]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 3, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[4] - LIST_nu_0_dip_2[2]), c, d, mean_delta_t)*10**(-6))
    
    print("\n=== PEAK 3, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[5] - LIST_nu_0_dip_2[2]), c, d, mean_delta_t)*10**(-6))
    
    #   distance to peak #4
    #   ===================

    print("\n=== PEAK 4, 5 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[4] - LIST_nu_0_dip_2[3]), c, d, mean_delta_t)*10**(-6))

    print("\n=== PEAK 4, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[5] - LIST_nu_0_dip_2[3]), c, d, mean_delta_t)*10**(-6))

    #   distance to peak #5
    #   ===================

    print("\n=== PEAK 5, 6 ===")
    print("=================")
    print("freq_dist in MHz = ", time_to_freq((LIST_nu_0_dip_2[5] - LIST_nu_0_dip_2[4]), c, d, mean_delta_t)*10**(-6))


if __name__ == "__main__":
    main()
