#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 01:37:15 2018

@author: hank
"""
# built-in
import time
import struct

# pip install numpy, spidev
import spidev
import numpy as np

# from ./
import gpio4

# ADS1299 Pin mapping
PIN_DRDY        = 6 # pin PA06
PIN_PWRDN       = 2 # pin PA02
PIN_START       = 3 # pin PA03
PIN_RESET       = 7 # pin PA07
# ADS1299 Registers
REG_CONFIG1     = 0x01
REG_CONFIG2     = 0x02
REG_CONFIG3     = 0x03
REG_CHnSET_BASE = 0x05
REG_BIAS_SENSP  = 0x0D
REG_BIAS_SENSN  = 0x0E
REG_MISC        = 0x15
# ADS1299 Commands
WAKEUP          = 0x02
STANDBY         = 0x04
RESET           = 0x06
START           = 0x08
STOP            = 0x0A
RDATAC          = 0x10
SDATAC          = 0x11
RDATA           = 0x12
WREG            = 0x40
RREG            = 0x20
# ADS1299 Sample data rate dict, set REG_CONFIG1 to this value
DR_DICT = {
    250:          0b10010110,
    500:          0x10010101,
    1000:         0x10010100,
    2000:         0x10010011,
    4000:         0x10010010,
    8000:         0x10010001,
    16000:        0x10010000,
}


class ADS1299_API(object):
    '''
    There is a module named RaspberryPiADS1299 to communicate will ADS1299 
    within Python through spidev. But it is not well written. Actually it's
    un-pythonic at all. Hard to understand, hard to use.
    So I rewrite it with spidev and SysfsGPIO(Unlike RPi.GPIO, SysfsGPIO
    works on both RaspberryPI, BananaPi, OrangePi and any hardware running 
    Linux, theoretically).
    
    Methods
    -------
        open: open device
        start: start Read DATA Continuously mode, you must call open first
        close: close device
        read_raw: return raw 8-channel * 3 = 24 bytes data
        read: return parsed np.ndarray data with shape of (8,)
        write: transfer one byte to ads1299
        write_register: write one register with index and value
        write_registers: write series registers with start index and values
    '''
    def __init__(self,
                 sample_rate=500,
                 bias_enabled=False,
                 test_mode=False,
                 scale=5.0/24/2**24):
        self.spi = spidev.SpiDev()
        
        self.scale = float(scale)
        self.sample_rate = sample_rate
        self._bias_enabled = bias_enabled
        self._test_mode = test_mode
#        self.last_time = time.time()
        self._DRDY = gpio4.SysfsGPIO(PIN_DRDY)
#        self._PWRDN = gpio4.SysfsGPIO(PIN_PWRDN)
#        self._RESET = gpio4.SysfsGPIO(PIN_RESET)
#        self._START = gpio4.SysfsGPIO(PIN_START)
        self._opened = False
        self._started = False
        
    def open(self, dev, max_speed_hz=1000000):
        '''
        connect to user space SPI interface `/dev/spidev*.*`
        param `dev` must be tuple/list, e.g. (1, 0) means `/dev/spidev1.0`
        '''
        self.spi.open(dev[0], dev[1])
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = 2
#        self._START.export = True
#        self._START.direction = 'out'
#        self._START.value = 0
        self._DRDY.export = True
        self._DRDY.direction = 'in'
        self._opened = True
        return dev
        
    def start(self):
        '''
        Before device power up, all digital and analog inputs must be low. 
        At the time of power up, keep all of these signals low until the 
        power supplies have stabilized.
        '''
        assert self._opened
        if self._started:
            return
        #======================================================================
        # power up
        #======================================================================
        # self._PWRDN.value=1 # we pull it up to high
        
        #self._RESET.value=1
        self.write(RESET)
        
        # wait for tPOR(2**18*666.0/1e9 = 0.1746) and tBG(assume 0.83)
        time.sleep(0.17+0.83)
        
        # device wakes up in RDATAC mode, send SDATAC 
        # command so registers can be written
        self.write(SDATAC)
        
        #======================================================================
        # configure_registers_before_streaming
        #======================================================================
        # common setting
        self.write_register(REG_CONFIG1, DR_DICT[self.sample_rate])
        self.write_register(REG_CONFIG2, 0b11010000)
        self.write_register(REG_MISC, 0b00100000)
        
        if self._bias_enabled:
            self.write_register(REG_BIAS_SENSP, 0b11111111)
            self.write_register(REG_BIAS_SENSN, 0b11111111)
            self.write_register(REG_CONFIG3, 0b11101100)
        else:
            self.write_register(REG_BIAS_SENSP, 0b00000000)
            self.write_register(REG_BIAS_SENSN, 0b00000000)
            self.write_register(REG_CONFIG3, 0b11100000)
        
        if self._test_mode:
            self.write_registers(REG_CHnSET_BASE, [0b01100101] * 8)
        else:
            self.write_registers(REG_CHnSET_BASE, [0b01100000] * 8)
        
        # self._START.value = 1
        self.write(START)
        time.sleep(1)
        
        #======================================================================
        # start streaming data
        #======================================================================
        self.write(RDATAC)
        
        self._started = True
        
    def close(self):
        if self._opened:
            self.write(SDATAC)
            self.write(STOP)
            self.spi.close()
#            self._START.value = 0
#            self._START.export = False
            self._DRDY.export = False
#            self._PWRDN.export = False
#            self._RESET.export = False
    
    def read(self):
#        while (time.time() - self.last_time) < 1.0/self.sample_rate:
#            pass
#        self.last_time = time.time()
        assert self._started
        while self._DRDY.value:
            pass
        num = self.spi.xfer2( [0x00]*27 )[3:]
        byte = ''
        for i in range(8):
#            tmp = chr(num[3*i+2]) + chr(num[3*i+1]) + chr(num[3*i]) # 4.3us
            tmp = struct.pack('3B', num[3*i+2], num[3*i+1], num[3*i]) # 1.3us
            byte += tmp + ('\xff' if num[3*i] > 127 else '\x00')
        return np.frombuffer(byte, np.int32) * self.scale
    
    def write(self, byte):
        self.spi.xfer2([byte])
        
    def write_register(self, reg, byte):
        self.spi.xfer2([reg|WREG, 0x00, byte])
        
    def write_registers(self, start_reg, byte_array):
        self.spi.xfer2([start_reg|WREG, len(byte_array) - 1] + byte_array)

    def read_register(self, reg):
        self.write(SDATAC)
        value = self.spi.xfer2([RREG|reg, 0x00, 0x00])[2]
        self.write(RDATAC)
        return value
    
    def read_registers(self, start_reg, num):
        self.write(SDATAC)
        value = self.spi.xfer2([RREG|start_reg, num - 1] + [0] * num)[2:]
        self.write(RDATAC)
        return value
    