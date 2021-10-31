#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 21:04:00 2021

@author: owen
contact: owenthompson098@gmail.com
"""

# This is a console interface program which drastically increases processing speeds.
# Code should not be directly changed, with the exceptions of filepaths (lines 107 to 133).
# I used the filepaths:
#
# Desktop
# - Analysis
# -- Python
# --- ClassicData
# ---- DATE
# ----- TARGET (e.g. W51)
# ------ ON-TARGET (Scans of W51)
# ------ OFF-TARGET (Scans with sufficient time for the target to pass out of the radio's view)
# ------ PROCESSED DATA (Noise-undistorted data)
# ------ PROCESSED PLOTS (Plots of the on-target, off-target and processed data)
#
# This program was written on macOS. Windows users may experience operating system related bugs when running.
# Feel free to contact me via my email if you have any questions.

import os
import codecs

import numpy as np
import math
import matplotlib.pyplot as plt

class Spectrum():
    DELIMITER = '  '
    HEADER_LENGTH = 1  # First line of each .txt file
    POS_INDEX = 1  # Where the position data is in the header

    def __init__(self, filepath):
        self.filepath = filepath

        self.raw_data = self.extract_data()
        self.header = self.remove_header()
        self.data = self.convert_raw_data()

        self.num_channels = len(self.data[0])

    def extract_data(self):
        with codecs.open(self.filepath, encoding='ASCII') as f:
            data = np.array([i.strip('\n').strip('\r').strip(self.DELIMITER)
                             for i in f])
        return data

    def remove_header(self):
        '''
        Note that this also alters self.raw_data by removing the header
        '''
        header = self.raw_data[:self.HEADER_LENGTH]
        self.raw_data = self.raw_data[self.HEADER_LENGTH:-1]  # Drop EOF
        return header

    def convert_raw_data(self):
        data = [[float(i) for i in row.split(self.DELIMITER)]
                for row in self.raw_data]
        return np.array(data)


# Variables to determine the type of scan performed
do_singlegraphs = 0
do_enlarged_single_graphs = 0
do_solarcal = 0
print('----------------------------------------')
print('This program has 3 analysis modes:\n - Single spectrum analysis.\n - Enlarged single spectrum analysis.\n - Solar calibration.')
print('----------------------------------------')
do_singlegraphs = int(input('Perform analysis of individual spectra? (1/0) '))
if(do_singlegraphs == 1):
    do_enlarged_single_graphs = int(input('Perform analysis of enlarged individual spectra? (1/0) ')) 
    running = True
elif(do_singlegraphs == 0):
    do_solarcal = int(input('Perform analysis of Solar calibration? (1/0) '))
    if(do_solarcal == 0):
        print('\nNo other analysis modes are available')
        running = False
    elif(do_solarcal == 1):
        running = True
            
            
HEADER_LENGTH = 1
POS_INDEX = 1
while running == True:
    # Variables to determine whether the plots/data should be saved
    do_savegraphs = int(input('Save any graphs produced? (1/0) '))
    do_savefiles = int(input('Save any noise-reduced data produced? (1/0) '))
    # Establish the files to be processed
    TARGET = input('Input target observed (e.g. Cep A - 1): ')
    DATE = input('Input date (e.g. 17-03-2021): ') # Date of observations
    TIMEZONE = 'GMT'
    date_info = DATE.split('-')
    if int(date_info[1]) >= 4 and int(date_info[1]) <= 10:
        # If month is April to October, TIMEZONE set to BST
        TIMEZONE = 'BST'
    elif int(date_info[1]) == 3:
        # If month is March and day is 28th or higher, TIMEZONE set to BST
        if int(date_info[0]) >= 28:
            TIMEZONE = 'BST'
    
    # Set filepaths for the data files and noise files to be processed
    path = r'/Users/owen/Desktop/Analysis/Python/ClassicData/'+DATE+'/'+TARGET+'/Raw Data/'
    print('Data path set to '+path)
    
    noisepath = r'/Users/owen/Desktop/Analysis/Python/ClassicData/'+DATE+'/'+TARGET+'/Noise/'
    print('Noise path set to '+noisepath)
    
    # If the plot directory does not exist, create the appropriate folders
    processedpath = r'/Users/owen/Desktop/Analysis/Python/ClassicData/'+DATE+'/'+TARGET+'/Processed Data/'
    print('Processed path set to '+processedpath)
    if not os.path.exists(processedpath):
        os.makedirs(processedpath)
        print('Directory path created for '+processedpath)
    
    # If the plot directory does not exist, create the appropriate folders
    plotpath = r'/Users/owen/Desktop/Analysis/Python/ClassicData/'+DATE+'/'+TARGET+'/Plots/'
    print('Plot path set to '+plotpath)
    if not os.path.exists(plotpath):
        os.makedirs(plotpath)
        print('Directory path created for '+plotpath)
        
    # If the plot directory does not exist, create the appropriate folders
    enplotpath = r'/Users/owen/Desktop/Analysis/Python/ClassicData/'+DATE+'/'+TARGET+'/EnlargedPlots/'
    print('Plot path set to '+enplotpath)
    if not os.path.exists(enplotpath):
        os.makedirs(enplotpath)
        print('Directory path created for '+enplotpath)
    
    
    # Create a list containing all raw split data files
    files = []
    print(sorted(os.listdir(path)))
    for filenames in sorted(os.listdir(path)):
        if not filenames.startswith('.'):
            # Split the file name into two parts: 'Name YYYY-MM-DD HH MM SS' and '###'
            # The second part (###) can be one, two, or three digits.
            # However, this leads to sorting errors (100 sorting before 20 and 30!)
            # SpectraCyber records up to .999, so the only files that need to be altered are single and double digit
            filenamearray = filenames.split('UTC.')
            fna = filenamearray
            if len(fna[1]) == 3:
                print('File formatted well.')
            elif len(fna[1]) == 2:
                print('File is double digit, adding 0.')
                os.rename(path+filenames, path+filenamearray[0]+'UTC.0'+filenamearray[1])
            elif len(fna[1]) == 1:
                print('File is single digit, adding 00.')
                os.rename(path+filenames, path+filenamearray[0]+'UTC.00'+filenamearray[1])
    for filenames in sorted(os.listdir(path)):
        if filenames.startswith('.'):
            # If the file starts with a '.', such as .DS_Store, it will be ignored
            print('    File ignored: ')
            print(filenames)
        else:
            files.extend([filenames])
            print('    File added: ')
            print(filenames)
    # Print the list of filtered files
    print('    Filtered files: ')
    print(files)
        
    
    # Input information on the files to plot the data
    gain = 0 # In the future, gain and offset could be used to calibrate this program.
    offset = 0 # e.g. a gain/offset value of 5/0.7 will yield a very different graph to values of 20/1.5. 
    # And so these two values should be calibrated accordingly (ONLY IF YOU WANT TO CONVERT TO JY).
    f_lower = int(input('Input lower frequency limit (e.g. -1000): '))
    f_upper = int(input('Input upper frequency limit (e.g. +1000): '))
    
    # Determine what x and y scales will be used
    ylab1 = "Intensity (Volts)" # y-axis output for SpectraCyber
    yscale1const = 1
        
    ylab2 = "Flux density (Jy)" # Solar calibration for the methanol receiver is still required for this feature to work as intended
    yscale2const = 0 # Change this value for whatever the conversion rate is
    
    ylab3 = "Mean intensity (Volts)" # Used for Solar calibration plots
    
    YSCALE = input('Input y scale (v/j): ')
    if YSCALE == 'v' or YSCALE == 'V':
        yscaleconst = yscale1const
    elif YSCALE == 'j' or YSCALE == 'J':
        gain = float(input('Input gain (e.g. 10): '))
        offset = float(input('Input offset (e.g. 1.05): '))
        yscaleconst = yscale2const
        
    if do_singlegraphs == 1:
        XSCALE = input('Input x scale (f/v): ')
        if XSCALE == 'f' or XSCALE == 'F':
            if f_lower == -1000 and f_upper == 1000:
                xTicks = np.arange(-1000, 1200, 200)
                f_step = 5
            elif f_lower == -2000 and f_upper == 0:
                xTicks = np.arange(-2000, 200, 200)
                f_step = 5
            elif f_lower == 0 and f_upper == 2000:
                xTicks = np.arange(-0, 2200, 200)
                f_step = 5
            elif f_lower == -2000 and f_upper == 2000:
                xTicks = np.arange(-2000, 2400, 400)  
                f_step = 10
            else:
                xTicks = np.arange(-2000, 2400, 400)
                f_step = int(input('Input frequency shift in kHz (e.g. 5): '))
        elif XSCALE == 'v' or XSCALE == 'V':
            if f_lower == -1000 and f_upper == 1000:
                xTicks = np.arange(-45, 50, 10)
                f_step = 5
            elif f_lower == -2000 and f_upper == 0:
                xTicks = np.arange(0, 95, 10)
                f_step = 5
            elif f_lower == 0 and f_upper == 2000:
                xTicks = np.arange(-90, 5, 10)
                f_step = 5
            elif f_lower == -2000 and f_upper == 2000:
                xTicks = np.arange(-90, 95, 20)
                f_step = 10
            else:
                xTicks = np.arange(-90, 95, 20)
                f_step = int(input('Input frequency shift in kHz (e.g. 5): '))
    
    if do_solarcal == 1:
        f_step = int(input('Input frequency shift in kHz (e.g. 5): '))
    
    xlab = "Default x label"
    
    xlab1 = "Doppler-shifted frequency (kHz)"
    xscale1 = np.transpose(np.arange(f_lower, f_upper-f_step, f_step))
    xscale1 = np.expand_dims(xscale1, axis = 1)
    
    xlab2 = "LSR velocity (km/s)"
    xscale2 = (300000000/1000)*(1-(((xscale1*1000) + 1420406000)/(1420406000)))
    
    xlab3 = "LSR velocity (km/s)"
    xscale3 = (300000000/1000)*(1-(((xscale1*1000) + 6668518000)/(6668518000)))
    
    xlab4 = "Scan number"

    
    if do_singlegraphs == 1:
        if XSCALE == 'f' or XSCALE == 'F':
            xscale = xscale1
            xlab = xlab1
        elif XSCALE == 'v' or XSCALE == 'V':
            # Determine x-scale to be used
            receiver = input('Input receiver used (h/m): ')
            if receiver == 'h' or receiver == 'H':
                xlab = xlab2
                xscale = xscale2
            elif receiver == 'm' or receiver == 'M':
                xlab = xlab3
                xscale = xscale3
            # Calculate velocity shifts for Earth rotation speed, heliocentric motion, Solar peculiar motion
            azimuth = float(input('Input azimuth in degrees (e.g. 248.75): '))
            altitude = float(input('Input altitude in degrees (e.g. 31.83): '))
            latitude = math.radians(53.9436) # Convert Astrocampus latitude from degrees to radians
            earthRotationVelocityMax = float(0.46388889 * math.cos(latitude))
            print('\n\tLatitude gives a Max Earth Rotation Velocity of ' + str(earthRotationVelocityMax))
            earthRotationVelocityTowardsTarget = float(earthRotationVelocityMax * math.cos(math.radians(azimuth-90)) * math.cos(math.radians(altitude)))
            print('\nTarget has an Earth Rotation Velocity of ' + str(earthRotationVelocityTowardsTarget))
            daysPassed = int(input('Input days passed since 21st December (e.g. 131): '))
            galacticLongitude = float(input('Input Galactic Longitude of target observed (e.g. 49.5): '))
            galacticLatitude = float(input('Input Galactic Latitude of target observed (e.g. -0.4): '))
            earthVelocityTowardsTarget = 29.78 * math.sin(math.radians(90 + galacticLongitude + (90-((360/365)*131))))
            print('\n\tEarth velocity towards target is ' + str(earthVelocityTowardsTarget))
            solarVelocityOne = 9 * math.cos(math.radians(galacticLongitude)) * math.cos(math.radians(galacticLatitude))
            solarVelocityTwo = 12 * math.sin(math.radians(galacticLongitude)) * math.cos(math.radians(galacticLatitude))
            solarVelocityThree = 7 * math.sin(math.radians(galacticLatitude))
            solarPeculiarMotion = solarVelocityOne + solarVelocityTwo + solarVelocityThree
            print('\n\tSolar perculiar motion is ' + str(solarPeculiarMotion))
            print('\nVelocity shift is: ' + str(earthRotationVelocityTowardsTarget + earthVelocityTowardsTarget + solarPeculiarMotion))
            velocityShift = earthRotationVelocityTowardsTarget + earthVelocityTowardsTarget + solarPeculiarMotion
            xscale = xscale + velocityShift
            tensRemainder = math.floor(velocityShift / 10)
            tickShift = (tensRemainder*10)
            remainder = velocityShift % 10
            if remainder < 5:
                tickShift += 5
            elif remainder > 5:
                tickShift += 10
            print('Tick shift is: ' + str(tickShift))
            xTicks += tickShift
            
            
    datapoint_lower = int((f_lower/f_step)+200)
    datapoint_upper = int(((f_upper-5)/f_step)+200)
    # datapoint_upper subtracts 5 to account for range skipping the last data point
    # e.g. a range of ±250 actually records from -250 to +245, the rest of the data points will be 0.0
    print('\nRanging from data point '+str(datapoint_lower+1)+' to data point '+str(datapoint_upper+1))
    
    
    # If noise scans were taken, they will be averaged and the sum will be subtracted from the on-target scans
    NOISE = input('Were noise scans taken for the target? (Y/N) ')
    alphaValue = 1
    if NOISE == 'Y' or NOISE == 'y':
        alphaValue = 0.5
        # Scan through files in the noise folder
        noisefiles = []
        print(sorted(os.listdir(noisepath)))
        for noisefilenames in sorted(os.listdir(noisepath)):
            if not noisefilenames.startswith('.'):
                # Split the file name into two parts: 'Name YYYY-MM-DD HH MM SS' and '###'
                # The second part (###) can be one, two, or three digits.
                # However, this leads to sorting errors (100 sorting before 20 and 30!)
                # SpectraCyber records up to .999, so the only files that need to be altered are single and double digit
                noisefilenamearray = noisefilenames.split('UTC.')
                nfna = noisefilenamearray
                if len(nfna[1]) == 3:
                    print('File formatted well.')
                elif len(nfna[1]) == 2:
                    print('File is double digit, adding 0.')
                    os.rename(noisepath+noisefilenames, noisepath+nfna[0]+'UTC.0'+nfna[1])
                elif len(nfna[1]) == 1:
                    print('File is single digit, adding 00.')
                    os.rename(noisepath+noisefilenames, noisepath+nfna[0]+'UTC.00'+nfna[1])
        for noisefilenames in sorted(os.listdir(noisepath)):
            if noisefilenames.startswith('.'):
                # If the file starts with a '.', such as .DS_Store, it will be ignored
                print('    File ignored: ')
                print(noisefilenames)
            else:
                noisefiles.extend([noisefilenames])
                print('    File added: ')
                print(noisefilenames)
        count = 0
        print(noisefiles)
        noisedata = np.zeros([399, 1], dtype = np.float64)
        for x in noisefiles:
            print(x)
            data_below = 0
            data_above = 0
            noiseplot = Spectrum(noisepath+x)
            with codecs.open(noisepath+x, encoding='ASCII') as f:
                data = np.array([i.strip('\n').strip('\r') for i in f])
                for i in range(noiseplot.num_channels):
                    noisedata[:,i] += noiseplot.data[:,i]
                    if str(i) == '0.000000':
                        data_below += 1
                    if str(i) == str(10.000000):
                        data_above += 1
                    if data_below > 0:
                        print('\tData below data limits: '+str(data_below))
                    if data_above > 0:
                        print('\tData below data limits: '+str(data_above))
            count += 1
        noisedata /= count
        mean_noise = np.mean(noisedata[datapoint_lower:(datapoint_upper+1)], dtype=np.float64)
        print('Mean noise: '+str(mean_noise))
        if do_singlegraphs == 1:
            plt.plot(xscale, noisedata+offset)
            plt.yticks(np.arange(-1, 12, 1))
            plt.xlabel(xlab)
            plt.xticks(xTicks)  
            plt.grid(True)
            plt.show()
    
    
    # Plot graphs for all files in selected folder
    if do_singlegraphs == 1:
        scan_no = 1
        for x in files:
            print(x)
            plot = Spectrum(path+x)
            with codecs.open(path+x, encoding='ASCII') as f:
                data = np.array([i.strip('\n').strip('\r') for i in f])
                scaninfo = str(plot.header).split(' ')
                month_modifier = ''
                day_modifier = ''
                hour_modifier = ''
                minute_modifier = ''
                second_modifier = ''
                if int(scaninfo[1]) < 10:
                    month_modifier = '0'
                if int(scaninfo[2]) < 10:
                    day_modifier = '0'
                if TIMEZONE == 'BST':
                    hour = int(scaninfo[4]) + 1
                if TIMEZONE == 'GMT':
                    hour = int(scaninfo[4]) 
                if hour < 10:
                    hour_modifier = '0'
                if int(scaninfo[5]) < 10:
                    minute_modifier = '0'
                if int(scaninfo[6]) < 10:
                    second_modifier = '0'
                title = TARGET+' - Scan number '+str(scan_no) + ' - '+day_modifier+str(scaninfo[2])+'/'+month_modifier+str(scaninfo[1])+'/'+str(scaninfo[3])+' '+hour_modifier+str(hour)+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
                for i in range(plot.num_channels):
                    plt.plot(xscale, (plot.data[:,i]+offset), label = 'Noise-distorted methanol-line spectrum', alpha = alphaValue)
                    if NOISE == 'Y' or NOISE == 'y':
                        plt.plot(xscale, noisedata[:,i]+offset, label = 'Noise profile', alpha = alphaValue)
                        plt.plot(xscale, plot.data[:,i]/noisedata[:,i]+offset-1, label = 'Undistorted methanol-line spectrum')
                plt.xticks(xTicks)
                plt.yticks(np.arange(-1, 12, 1))
                plt.grid(True)
                plt.tick_params(direction ='in')
                font = 'arial'
                plt.rc('font', size=9)
                plt.rc('axes', labelsize=11)
                plt.rc('axes', titlesize=11)
                plt.ylabel(ylab1, family=font) 
                plt.xlabel(xlab, family=font)
                plt.title(title, family=font)
                plt.rcParams["figure.dpi"] = 1000
                plt.legend()
                filename = day_modifier+str(scaninfo[2])+'-'+month_modifier+str(scaninfo[1])+'-'+str(scaninfo[3])+' '+hour_modifier+str(scaninfo[4])+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
                # Save figures as high resolution .png files ~ 0.5 MB each file
                if (do_savegraphs == 1):
                    plt.savefig(plotpath+filename+'.png', dpi = 1000)
                plt.show()
                if NOISE == 'Y' or NOISE == 'y':
                    sumdata = plot.data/noisedata+offset-1
                    savedata = np.hstack([sumdata, (xscale)])
                else:
                    savedata = np.hstack([plot.data, (xscale)])
                print('Filename - '+filename) 
                if (do_savefiles == 1):
                    np.savetxt(processedpath+filename+'.txt', savedata, '%s')
                    print('File saved - '+filename+'.txt')
                scan_no += 1
                
    # Plot graphs for all files in selected folder
    if do_enlarged_single_graphs == 1:
        f_lower = int(input('Input lower frequency limit (e.g. -1600): '))
        f_upper = int(input('Input upper frequency limit (e.g. -600): '))
        dataPointLower = int((f_lower / f_step) + 400)
        dataPointUpper = int(((f_upper) / f_step) + 400)
        print(dataPointLower)
        print(dataPointUpper)
        xscale1 = np.transpose(np.arange(f_lower, f_upper, f_step))
        xscale1 = np.expand_dims(xscale1, axis = 1)
        xscale = xscale1
        if XSCALE == 'v' or XSCALE == 'V':
            xscale3 = (300000000/1000)*(1-(((xscale1*1000) + 6668518000)/(6668518000))) + velocityShift
            xscale = xscale3
        # Display a temporary graph
        scan_no = 1
        plot = Spectrum(path+x)
        with codecs.open(path+x, encoding='ASCII') as f:
            data = np.array([i.strip('\n').strip('\r') for i in f])
            scaninfo = str(plot.header).split(' ')
            month_modifier = ''
            day_modifier = ''
            hour_modifier = ''
            minute_modifier = ''
            second_modifier = ''
            if int(scaninfo[1]) < 10:
                month_modifier = '0'
            if int(scaninfo[2]) < 10:
                day_modifier = '0'
            if TIMEZONE == 'BST':
                hour = int(scaninfo[4]) + 1
            if TIMEZONE == 'GMT':
                hour = int(scaninfo[4]) 
            if hour < 10:
                hour_modifier = '0'
            if int(scaninfo[5]) < 10:
                minute_modifier = '0'
            if int(scaninfo[6]) < 10:
                second_modifier = '0'
            title = TARGET+' Scan number '+str(scan_no) + ' - '+day_modifier+str(scaninfo[2])+'/'+month_modifier+str(scaninfo[1])+'/'+str(scaninfo[3])+' '+hour_modifier+str(hour)+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
            for i in range(plot.num_channels):
                print(plot.data[dataPointLower:dataPointUpper,i])
                plt.plot(xscale, (plot.data[dataPointLower:dataPointUpper,i]+offset), label = 'Noise-distorted methanol-line spectrum', alpha = alphaValue)
                if NOISE == 'Y' or NOISE == 'y':
                    plt.plot(xscale, noisedata[dataPointLower:dataPointUpper,i]+offset, label = 'Noise profile', alpha = alphaValue)
                    plt.plot(xscale, plot.data[dataPointLower:dataPointUpper,i]/noisedata[dataPointLower:dataPointUpper,i]+offset-1, label = 'Undistorted methanol-line spectrum')
            plt.xticks(xTicks)
            plt.yticks(np.arange(-1, 12, 1))
            plt.grid(True)
            plt.tick_params(direction ='in')
            font = 'arial'
            plt.rc('font', size=9)
            plt.rc('axes', labelsize=11)
            plt.rc('axes', titlesize=11)
            plt.ylabel(ylab1, family=font) 
            plt.xlabel(xlab, family=font)
            plt.title(title, family=font)
            plt.rcParams["figure.dpi"] = 1000
            plt.legend()
            filename = day_modifier+str(scaninfo[2])+'-'+month_modifier+str(scaninfo[1])+'-'+str(scaninfo[3])+' '+hour_modifier+str(scaninfo[4])+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
            plt.show()
        # Ask what the lower and upper x axis should be
        graphLowerTickX = int(input('Input the x lower tick (e.g. 30): '))
        graphUpperTickX = int(input('Input the x upper tick (e.g. 75): '))
        graphStepsX = int(input('Input the x increment (e.g. 5): '))
        xTicks = np.arange(graphLowerTickX, graphUpperTickX, graphStepsX)
        scan_no = 1
        for x in files:
            print(x)
            plot = Spectrum(path+x)
            with codecs.open(path+x, encoding='ASCII') as f:
                data = np.array([i.strip('\n').strip('\r') for i in f])
                scaninfo = str(plot.header).split(' ')
                month_modifier = ''
                day_modifier = ''
                hour_modifier = ''
                minute_modifier = ''
                second_modifier = ''
                if int(scaninfo[1]) < 10:
                    month_modifier = '0'
                if int(scaninfo[2]) < 10:
                    day_modifier = '0'
                if TIMEZONE == 'BST':
                    hour = int(scaninfo[4]) + 1
                if TIMEZONE == 'GMT':
                    hour = int(scaninfo[4]) 
                if hour < 10:
                    hour_modifier = '0'
                if int(scaninfo[5]) < 10:
                    minute_modifier = '0'
                if int(scaninfo[6]) < 10:
                    second_modifier = '0'
                title = TARGET+' Scan number '+str(scan_no) + ' - '+day_modifier+str(scaninfo[2])+'/'+month_modifier+str(scaninfo[1])+'/'+str(scaninfo[3])+' '+hour_modifier+str(hour)+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
                for i in range(plot.num_channels):
                    plt.plot(xscale, (plot.data[dataPointLower:dataPointUpper,i]+offset), label = 'Noise-distorted methanol-line spectrum', alpha = alphaValue)
                    if NOISE == 'Y' or NOISE == 'y':
                        plt.plot(xscale, noisedata[dataPointLower:dataPointUpper,i]+offset, label = 'Noise profile', alpha = alphaValue)
                        plt.plot(xscale, plot.data[dataPointLower:dataPointUpper,i]/noisedata[dataPointLower:dataPointUpper,i]+offset-1, label = 'Undistorted methanol-line spectrum')
                plt.xlabel(xlab)
                plt.xticks(xTicks)
                plt.yticks(np.arange(-1, 12, 1))
                plt.grid(True)
                plt.legend()
                plt.ylabel(ylab1) 
                plt.title(title)
                filename = day_modifier+str(scaninfo[2])+'-'+month_modifier+str(scaninfo[1])+'-'+str(scaninfo[3])+' '+hour_modifier+str(scaninfo[4])+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
                # Save figures as high resolution .png files ~ 0.5 MB each file
                if (do_savegraphs == 1):
                    plt.savefig(enplotpath+filename+'.png', dpi = 1000)
                plt.show()
                if (do_savefiles == 1):
                    np.savetxt(processedpath+filename+'.txt', savedata, '%s')
                    print('File saved - '+filename+'.txt')
                scan_no += 1
                
                
    # Plot graph for Solar calibration of one folder - WIP
    if do_solarcal == 1:
        scan_no = 0
        for x in files:
            print(x)
            scan_no += 1
        mean_data_no = int(scan_no)
        mean_data = np.zeros(scan_no)
        scan_no = 1
        for x in files:
            print(scan_no)
            print('\t'+x)
            plot = Spectrum(path+x)
            with codecs.open(path+x, encoding='ASCII') as f:
                data = np.array([i.strip('\n').strip('\r') for i in f])
                scaninfo = str(plot.header).split(' ')
                month_modifier = ''
                day_modifier = ''
                hour_modifier = ''
                minute_modifier = ''
                second_modifier = ''
                if int(scaninfo[1]) < 10:
                    month_modifier = '0'
                if int(scaninfo[2]) < 10:
                    day_modifier = '0'
                if int(scaninfo[4]) < 10:
                    hour_modifier = '0'
                if int(scaninfo[5]) < 10:
                    minute_modifier = '0'
                if int(scaninfo[6]) < 10:
                    second_modifier = '0'
                print('\t'+str(np.mean(plot.data[datapoint_lower:datapoint_upper,:], dtype=np.float64)))
                mean_data[scan_no-1] = np.mean(plot.data[datapoint_lower:datapoint_upper,:], dtype=np.float64)
            scan_no += 1
        mean_data = np.expand_dims(mean_data, axis = 1)
        noise_x = np.arange(1, mean_data_no+1, 1)
        noise_x = np.expand_dims(noise_x, axis = 1)
        plt.plot(noise_x, mean_data[0:(len(mean_data)),:]+offset, label = 'Noise-distorted mean intensity')
        if NOISE == 'Y' or NOISE == 'y':
            noise_y = np.zeros(mean_data_no)
            noise_y.fill(mean_noise)
            plt.plot(noise_x, noise_y+offset, label = 'Mean noise')
            plt.plot(noise_x, mean_data[0:(len(mean_data)),:]-mean_noise+offset, label = 'Undistorted mean intensity')
        title = TARGET+' - Solar calibration - '+day_modifier+str(scaninfo[2])+'/'+month_modifier+str(scaninfo[1])+'/'+str(scaninfo[3])
        plt.grid(True)
        plt.tick_params(direction ='in')
        font = 'arial'
        plt.ylabel(ylab3, family=font) 
        plt.xlabel(xlab4, family=font)
        plt.title(title, family=font)
        plt.rc('font', size=9)
        plt.rc('axes', labelsize=11)
        plt.rc('axes', titlesize=11)
        plt.rcParams["figure.dpi"] = 1000
        filename = day_modifier+str(scaninfo[2])+'-'+month_modifier+str(scaninfo[1])+'-'+str(scaninfo[3])+' '+hour_modifier+str(scaninfo[4])+':'+minute_modifier+str(scaninfo[5])+':'+second_modifier+str(scaninfo[6])
        # Save figures as high resolution .png files ~ 0.5 MB each file
        if (do_savegraphs == 1):
            plt.savefig(plotpath+filename+'.png', dpi = 1000)
        plt.show()
        if NOISE == 'Y' or NOISE == 'y':
            sumdata = mean_data[0:len(mean_data),:]-mean_noise+offset
            savedata = np.hstack([sumdata, (noise_x)])
        else:
            savedata = np.hstack([mean_data[0:len(mean_data),:], (noise_x)])
        print('Filename - '+filename) 
        if (do_savefiles == 1):
            np.savetxt(processedpath+filename+'.txt', savedata, '%s')
            print('File saved - '+filename+'.txt')
            

    # Quit program if no further scans to be analysed
    QUIT = input('Analyse another set of data (Y/N)? ')
    if QUIT == 'Y' or QUIT == 'y':
        running = True
    if QUIT == 'N' or QUIT == 'n':
        running = False   
        
        