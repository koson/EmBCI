#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 19:27:13 2018

@author: hank
"""
# built-in
from __future__ import print_function
import os, sys, time, threading
sys.path += ['./src', './utils']
from functools import partial

# pip install ipython, numpy, scipy, pillow
import IPython
import numpy as np
from scipy import signal
from PIL import Image, ImageDraw

# from ./utils
from common import check_input, mapping
# from gpio4 import SysfsGPIO
from preprocessing import Signal_Info
# from visualization import Serial_Screen_GUI as Screen_GUI
from visualization import SPI_Screen_GUI as Screen_GUI
# from IO import ADS1299_reader as Reader
from IO import ESP32_SPI_reader as Reader
from IO import Socket_server

ILI9341_BLUE        = [0x00, 0x1F] #   0   0 255
ILI9341_GREEN       = [0x07, 0xE0] #   0 255   0
ILI9341_CYAN        = [0x07, 0xFF] #   0 255 255
ILI9341_RED         = [0xF8, 0x00] # 255   0   0
ILI9341_MAGENTA     = [0xF8, 0x1F] # 255   0 255
ILI9341_YELLOW      = [0xFF, 0xE0] # 255 255   0
ILI9341_WHITE       = [0xFF, 0xFF] # 255 255 255
ILI9341_PURPLE      = [0x41, 0x2B] # 128   0 128
ILI9341_ORANGE      = [0xFD, 0xC0] # 255 160  10
ILI9341_GREY        = [0x84, 0x10] # 128 128 128

RGB_BLUE            = (  0,   0, 255)
RGB_GREEN           = (  0, 255,   0)
RGB_CYAN            = (  0, 255, 255)
RGB_RED             = (255,   0,   0)
RGB_MAGENTA         = (255,   0, 255)
RGB_YELLOW          = (255, 255,   0)
RGB_WHITE           = (255, 255, 255)
RGB_PURPLE          = (128,   0, 128)
RGB_ORANGE          = (255, 160,  10)
RGB_GREY            = (128, 128, 128)

ILI9341_COLOR = [
    ILI9341_BLUE, ILI9341_YELLOW, ILI9341_MAGENTA, ILI9341_CYAN,
    ILI9341_GREEN, ILI9341_RED, ILI9341_PURPLE, ILI9341_ORANGE, ILI9341_GREY]
RGB_COLOR = [
    RGB_BLUE, RGB_YELLOW, RGB_MAGENTA, RGB_CYAN,
    RGB_GREEN, RGB_RED, RGB_PURPLE, RGB_ORANGE, RGB_GREY]

def shutdown(*a, **k):
    for flag in flag_list:
        flag[0].set()
        flag[1].set()
    s.close()
    reader.close()
    os.system('shutdown now')

def reboot(*a, **k):
    s.close()
    os.system('reboot')

def generate_pdf(*a, **k):
    # TODO: generate pdf using python-reportlab
    print('pdf saved!')


# def range_callback(r, operate, element, id=None, fm=None, *a, **k):
#     if operate == 'plus':
#         r['n'] += r['step']
#         if r['n'] > r['r'][1]:
#             r['n'] = r['r'][0]
#     elif operate == 'minus':
#         r['n'] -= r['step']
#         if r['n'] < r['r'][0]:
#             r['n'] = r['r'][1]
#     else:
#         return
#     if None not in [element, id]:
#         e = s.widget[element, id]
#         if e is not None:
#             if fm is not None:
#                 e['s'] = fm.format(e['n'])
#             else:
#                 e['s'] = str(e['n'])
#             s.render(element, id)

# def list_callback(l, operate, element, id=None, fm=None, cb=False, *a, **k):
#     if operate == 'next':
#         l['i'] += 1
#     elif operate == 'prev':
#         l['i'] -= 1
#     else:
#         return
#     l['i'] %= len(l['a'])
#     if None not in [element, id]:
#         e = s.widget[element, id]
#         if e is not None:
#             if fm is not None:
#                 e['s'] = fm.format(l['a'][l['i']])
#             else:
#                 e['s'] = str(l['a'][l['i']])
#             s.render(element, id)
#             if cb:
#                 e['callback'] = l['callback'][l['i']]

# def display_waveform(*args, **kwargs):
#     s.freeze_frame()
#     # start and stop flag
#     flag_close = threading.Event()
#
#     # construct reader
#     sample_rate = rate_list['a'][rate_list['i']]
#     sample_time = time_range['n']
#     n_channel = channel_range['n']
#     if not hasattr(s, 'reader'):
#         s.reader = Reader(sample_rate, sample_time, n_channel, send_to_pylsl=False)
#     s.reader.start()
#     n_channel = min(n_channel, s.reader.n_channel)
#     current_ch_range = {'r': (0, n_channel-1), 'n': 0, 'step': 1}
#     color = np.arange(1, 9)
#     area = [0, 40, 219, 175]
#
#     # plot page widgets
#     s.draw_text(5, 1, '波形显示', c=2) # 0
#     s.draw_text(4, 1, '波形显示', c=2) # 1
#     s.draw_button(5, 19, '返回上层', callback=lambda *a, **k: flag_close.set())
#     s.draw_rect(72, 0, 219, 35, c=5)
#     s.draw_text(74, 1, '幅度') # 2
#     s.draw_button(112, 2, '－', partial(list_callback, l=scale_list, fm='{:8d}',
#                                         element='text', id=3, operate='prev'))
#     s.draw_text(134, 1, '%8d' % scale_list['a'][scale_list['i']]) # 3
#     s.draw_button(202, 2, '＋', partial(list_callback, l=scale_list, fm='{:8d}',
#                                         element='text', id=3, operate='next'))
#     s.draw_text(74, 18, '通道') # 4
#     s.draw_button(112, 19, '－', partial(range_callback, r=current_ch_range,
#                                          element='text', operate='minus',
#                                          fm='  ch{:2d}  ', id=5))
#     s.draw_text(134, 18, '  ch%2d  ' % current_ch_range['n']) # 5
#     s.draw_button(202, 19, '＋', partial(range_callback, r=current_ch_range,
#                                          element='text', operate='plus',
#                                          fm='  ch{:2d}  ', id=5))
#     center = area[1] + (area[3] - area[1])/2
#     data = np.repeat(center, area[2] - area[0])
#     DC = 0
#     step = 1
#     # start plotting!
#     try:
#         while 1:
#             for x in range(step, area[2] - area[0], step):
#                 assert not flag_close.is_set()
#                 d = s.reader.channel_data  # raw data
#                 server.send(d)
#                 ch = current_ch_range['n']
#                 d = d[ch] * scale_list['a'][scale_list['i']]  # pick one channel and re-scale this data
#                 DC = d * 0.1 + DC * 0.9  # real-time remove DC
#                 data[x] = np.clip(center - (d - DC), area[1], area[3]).astype(np.int)  # get screen position
#                 with s.write_lock:
#                     s.send('line', x1=x, y1=area[1], x2=x, y2=area[3], c=0)  # first clear current line
#                     if data[x] != data[x-step]:  # then draw current point
#                         s.send('line', x1=x, x2=x, y1=data[x-step], y2=data[x], c=color[ch])
#                     else:
#                         s.send('point', x=x, y=data[x], c=color[ch])
#             data[0] = data[x]
#     except AssertionError:
#         pass
#     except Exception as e:
#         print('[Display Waveform] {}: '.format(type(e)), end='')
#         print(e)
#     finally:
#         print('[Display Waveform] terminating...')
#         s.recover_frame()
#         s.reader.pause()

# def display_info(x, y, bt):
#     s.freeze_frame()
#     # start and stop flag
#     flag_close = threading.Event()
#
#     # construct reader
#     sample_rate = rate_list['a'][rate_list['i']]
#     sample_time = time_range['n']
#     n_channel = channel_range['n']
#     scale_list['i'] = 6
#     if not hasattr(s, 'reader'):
#         s.reader = Reader(sample_rate, sample_time, n_channel, send_to_pylsl=False)
#     s.reader.start()
#     n_channel = min(n_channel, s.reader.n_channel)
#     sample_rate, sample_time = s.reader.sample_rate, s.reader.sample_time
#     current_ch_range = {'r': (0, n_channel-1), 'n': 0, 'step': 1}
#     si = Signal_Info()
#     p = Processer(sample_rate, sample_time)
#     global cx, draw_fft
#     draw_fft = True
#     area = [0, 70, 182, 175]
#     f_max = 1
#     f_min = 0
#     cx = 0
#     def change_plot(*a, **k):
#         global cx, draw_fft
#         with s.write_lock:
#             cx = 0
#             draw_fft = not draw_fft
#             s.clear(*area)
#         for bt in s.widget['button']:
#             if bt['id'] == 9:
#                 bt['s'] = '\xbb\xad\xcd\xbc' if draw_fft else '\xbb\xad\xcf\xdf'
#         s.render('button', 9)
#
#     # plot page widgets
#     s.draw_button(187, 1, '返回', callback=lambda *a, **k: flag_close.set())
#     s.draw_button(2, 0, '↑', partial(range_callback, r=f1_range, fm='{:2d}'
#                                      element='text', id=0, operate='plus'))
#     s.draw_text(0, 17, ' 4', c=3) # 0
#     s.draw_button(2, 36, '↓', partial(range_callback, r=f1_range, fm='{:2d}',
#                                       element='text', id=0, operate='minus'))
#     s.draw_text(16, 17, '-') # 1
#     s.draw_button(26, 0, '↑', partial(range_callback, r=f2_range, fm='{:2d}',
#                                       element='text', id=2, operate='plus'))
#     s.draw_text(24, 17, ' 6', c=3) # 2
#     s.draw_button(26, 36, '↓', partial(range_callback, r=f2_range, fm='{:2d}',
#                                        element='text', id=2, operate='minus'))
#     s.draw_text(44, 0, '幅度') # 3
#     s.draw_button(78, 1, '－', partial(list_callback, l=scale_list, fm='{:8d}',
#                                        element='text', id=4, operate='prev'))
#     s.draw_text(95, 0, '%8d' % scale_list['a'][scale_list['i']]) # 4
#     s.draw_button(169, 1, '＋', partial(list_callback, l=scale_list, fm='{:8d}',
#                                         element='text', id=4, operate='next'))
#     s.draw_text(40, 18, '最大峰值') # 5
#     s.draw_text(104, 18, '       ', c=1) # 6 7*8=56
#     s.draw_text(163, 18, '     ', c=1) # 7 5*8=40
#     s.draw_text(203, 18, 'Hz') # 8
#     s.draw_text(43, 34, '2-30Hz能量和') # 9
#     s.draw_text(139, 34, '          ', c=1) # 10 10*8=80
#     s.draw_text(0, 53, '2-125最大峰值') # 11
#     s.draw_text(104, 53, '       ', c=1) # 12 7*8=56
#     s.draw_text(163, 53, '     ', c=1) # 13 5*8=40
#     s.draw_text(203, 53, 'Hz') # 14
#     s.draw_text(185, 70, '通道') # 15
#     s.draw_button(185, 88, '－', partial(range_callback, r=current_ch_range,
#                                         element='text', id=16, fm='ch{:2d}',
#                                         operate='minus'))
#     s.draw_text(185, 106, 'ch%2d' % current_ch_range['n']) # 16
#     s.draw_button(203, 88, '＋', partial(range_callback, r=current_ch_range,
#                                          element='text', id=16, fm='ch{:2d}',
#                                          operate='plus'))
#     s.draw_button(185, 125, '画图' if draw_fft else '画线', change_plot)
#
#     r_amp = s.widget['text'][6]
#     r_fre = s.widget['text'][7]
#     egy30 = s.widget['text'][10]
#     a_amp = s.widget['text'][12]
#     a_fre = s.widget['text'][13]
#
#     # start display!
#     last_time = time.time()
#     try:
#         while 1:
#             while (time.time() - last_time) < 0.5:
#                 time.sleep(0)
#             last_time = time.time()
#
#             assert not flag_close.is_set()
#             data = s.reader.buffer['channel%d' % current_ch_range['n']]
#             x, y = si.fft(p.notch(p.detrend(data)), sample_rate)
#             # get peek of specific duration of signal
#             f, a = si.peek_extract((x, y),
#                                    min(f1_range['n'], f2_range['n']),
#                                    max(f1_range['n'], f2_range['n']),
#                                    sample_rate)[0]
#             r_amp['s'] = '%.1e' % a
#             r_fre['s'] = '%5.2f' % f
#             # get peek of all
#             f, a = si.peek_extract((x, y), 2, sample_rate/2, sample_rate)[0]
#             a_amp['s'] = '%.1e' % a
#             a_fre['s'] = '%5.1f' % f
#             a_f_m = int(f*2.0*(x.shape[0] - 1)/sample_rate)
#             # get energy info
#             e = si.energy((x ,y), 3, 30, sample_rate)[0]
#             egy30['s'] = '%.4e' % e
#
#             if draw_fft:  # draw amp-freq graph
#                 step = 1
#                 s.clear(*area)
#                 y = y[0][:area[2] - area[0]]
#                 server.send(y)  # raw data
#                 y = np.clip(area[3] - y * scale_list['a'][scale_list['i']],
#                             area[1], area[3]).astype(np.int)
#                 for x in range(step, len(y), step):
#                     if not draw_fft:
#                         break
#                     with s.write_lock:
#                         if y[x] != y[x-step]:
#                             s.send('line', x1=x, x2=x, y1=y[x-step], y2=y[x], c=3)
#                         else:
#                             s.send('point', x=x, y=y[x], c=3)
#                 # render elements
#                 s.render('text', 6)
#                 s.render('text', 7)
#                 s.render('text', 10)
#                 s.render('text', 12)
#                 s.render('text', 13)
#                 s.send('line', x1=a_f_m, y1=area[1], x2=a_f_m, y2=area[3], c=1)
#                 time.sleep(0.5)
#             else:
#                 y = np.log10(y[0][:int(60.0*(x.shape[0] - 1)/sample_rate)])
#                 f_max = max(f_max, int(y.max()))
#                 f_min = min(f_min, int(y.min()))
#                 y = np.round(mapping(y, f_min, f_max,
#                                      0, len(s.rainbow))).astype(np.int)
#                 with s.write_lock:
#                     for i, v in enumerate(y):
#                         s.send('point', x=cx, y=area[1] + i, c=s.rainbow[v])
#                 cx += 1
#                 if cx > area[2]:
#                     cx = area[0]
#                     s.clear(*area)
#                 s.render('text', 6)
#                 s.render('text', 7)
#                 s.render('text', 10)
#                 s.render('text', 12)
#                 s.render('text', 13)
#     except AssertionError:
#         pass
#     except Exception as e:
#         print('[Display Info] {}: '.format(type(e)), end='')
#         print(e)
#     finally:
#         print('[Display Info] terminating...')
#         # recover old widget
#         s.recover_frame()
#         s.reader.pause()
#
# def energy_time_duration(self, reader, low, high, duration):
#     '''
#     calculate energy density of time duration
#     '''
#     import time, threading
#     energy_sum = np.zeros(reader.n_channel)
#     sample_rate = reader.sample_rate
#     stop_flag = threading.Event()
#     def _sum(flag, eng):
#         start_time = time.time()
#         while not flag.isSet():
#             if (time.time() - start_time) > duration:
#                 break
#             eng += self.energy(reader.data_frame, low, high,  sample_rate)
#         eng /= (sample_rate * (time.time() - start_time))
#     threading.Thread(target=_sum, args=(stop_flag, energy_sum)).start()
#     return stop_flag, energy_sum

# rate_list = {'a': [250, 500, 1000], 'i': 0}

# time_range = {'r': (0.5, 5.0), 'n': 3.0, 'step': 0.1}

# jobs_list = {'a': ['\xb2\xa8\xd0\xce\xcf\xd4\xca\xbe',
#                    '\xcf\xd4\xca\xbe\xd0\xc5\xcf\xa2'],
#              'i': 0,
#              'callback': [display_waveform, display_info]}

# f1_range = {'r': (1, 30), 'n': 4, 'step': 1}

# f2_range = {'r': (1, 30), 'n': 6, 'step': 1}

scale_list = {'a': [1000, 2000, 5000, 10000, 50000,
                    100000, 1000000, 5000000],
              'i': 1}

channel_range = {'r': (0, 7), 'n': 0, 'step': 1}

page_list = {'a': ['./files/layouts/layout-DBS-page%d.pcl' % i \
                   for i in range(1, 6)],
             'i': 0}

def range_callback(r, operate, prev=None, after=None, *a, **k):
    if prev is not None:
        prev(*a, **k)
    if operate == 'plus':
        r['n'] += r['step']
        if r['n'] > r['r'][1]:
            r['n'] = r['r'][0]
    elif operate == 'minus':
        r['n'] -= r['step']
        if r['n'] < r['r'][0]:
            r['n'] = r['r'][1]
    else:
        return
    if after is not None:
        after(*a, **k)

def list_callback(l, operate, prev=None, after=None, *a, **k):
    if prev is not None:
        prev(*a, **k)
    if operate == 'next':
        l['i'] += 1
    elif operate == 'prev':
        l['i'] -= 1
    else:
        return
    l['i'] %= len(l['a'])
    if after is not None:
        after(*a, **k)

#                    flag_pause         flag_close
flag_list = [(threading.Event(), threading.Event()),  # page1
             (threading.Event(), threading.Event()),  # page2
             (threading.Event(), threading.Event()),  # page3
             (threading.Event(), threading.Event()),  # page4
             (threading.Event(), threading.Event())]  # page5

def change_page(*a, **k):
    time.sleep(0.5)
    page_num = page_list['i']
    s.load_layout(page_list['a'][page_num], extend=False)
    for id in callback_list[page_num]:
        s.widget['button', id]['callback'] = callback_list[page_num][id]
    flag_list[page_num][0].set()
    flag_list[page_num][1].clear()
    threading.Thread(target=globals()['page%d_daemon' % (page_num + 1)],
                     args=flag_list[page_num]).start()

def change_channel(*a, **k):
    s.widget['text', 15]['s'] = 'CH%d' % channel_range['n']
    s.render('text', 15)

test_dict = dict.fromkeys([(1, i) for i in range(2, 10)] +
                          [(4, i) for i in range(2,  8)])

def reverse_status(*a, **k):
    name = (page_list['i']+1, k['bt']['id'])
    test_dict[name] = not test_dict[name]

prev = partial(list_callback, l=page_list, operate='prev', after=change_page,
               prev=lambda *a, **k: flag_list[page_list['i']][1].set())
next = partial(list_callback, l=page_list, operate='next', after=change_page,
               prev=lambda *a, **k: flag_list[page_list['i']][1].set())

callback_list = [
    # page1
    # id of button: callback function
    {0: shutdown, 1: next,
     2: reverse_status, 3: reverse_status, 4: reverse_status, 5: reverse_status,
     6: reverse_status, 7: reverse_status, 8: reverse_status, 9: reverse_status},
    # page2
    {0: prev, 1: next,
     2: partial(range_callback, r=channel_range,
                operate='minus', after=change_channel),
     3: partial(range_callback, r=channel_range,
                operate='plus', after=change_channel),
     4: partial(list_callback, l=scale_list, operate='next'),
     5: partial(list_callback, l=scale_list, operate='prev')},
    # page3
    {0: prev, 1: next},
    # page4
    {0: prev, 1: next,
     2: reverse_status, 3: reverse_status, 4: reverse_status,
     5: reverse_status, 6: reverse_status, 7: reverse_status},
    # page5
    {0: prev, 1: generate_pdf}]

def page1_daemon(flag_pause, flag_close, fps=1, thres=0):
    print('turn to page1')
    img_red = Image.open('./files/icons/4@300x-8.png').resize((21, 21))
    img_red = np.array(img_red.convert('RGBA'))
    img_green = Image.open('./files/icons/5@300x-8.png').resize((21, 21))
    img_green = np.array(img_green.convert('RGBA'))
    reader._esp.do_measure_impedance = True
    reader.data_channel
    last_time = time.time()
    last_status = [False] * 8
    while not flag_close.isSet():
        while (time.time() - last_time) < 1.0/fps:
            time.sleep(0.05)
        last_time = time.time()
        flag_pause.wait()
        data = reader.data_channel
        for i in np.arange(8):
            if test_dict[(1, i+2)]:
                s.widget['button', i+2]['s'] = '{:.1e}'.format(data[i])
                s.render('button', i+2)
                if data[i] > thres and not last_status[i]:
                    s.widget['img', i+5]['img'] = img_green
                    s.render('img', i+5)
                    last_status[i] = True
                elif data[i] < thres and last_status[i]:
                    s.widget['img', i+5]['img'] = img_red
                    s.render('img', i+5)
                    last_status[i] = False
    reader._esp.do_measure_impedance = False
    print('leave page1')

def page2_daemon(flag_pause, flag_close, step=1, low=2.5, high=30.0,
                 area=[39, 45, 290, 179], center=112):
    print('turn to page2')
    line = np.ones((2, area[2]), np.uint16) * center
    data = reader.data_frame
    si.bandpass(data, low, high, register=True)
    si.notch(data, register=True)
    while not flag_close.isSet():
        flag_pause.wait()
        ch = channel_range['n']
        scale = scale_list['a'][scale_list['i']]
        c = ILI9341_COLOR[ch]
        s._ili.draw_rectf(area[0], area[1], area[0]+step*3, area[3], ILI9341_WHITE)
        s.widget['text', 16]['s'] = u'%5.1fs\u2191' % \
            (time.time() - reader._start_time)
        s.render('text', 16)
        for x in np.arange(area[0], area[2], step, dtype=int):
            if flag_close.isSet():
                break
            d = reader.data_channel
            server.send(d)
            data = d[ch]
            data = np.array([data, si.bandpass_realtime(si.notch_realtime(data))])
            line[:, x] = np.uint16(np.clip(center - data*scale, area[1], area[3]))
            yraw, yflt = line[:, x-step], line[:, x]
            s._ili.draw_line(x+step*4, area[1], x+step*4, area[3], ILI9341_WHITE)
            # if yraw[0] == yraw[1]:
            #     s._ili.draw_point(x, yraw[0], ILI9341_GREY)
            # else:
            #     s._ili.draw_line(x, yraw.min(), x, yraw.max(), ILI9341_GREY)
            if yflt[0] == yflt[1]:
                s._ili.draw_point(x, yraw[0], c)
            else:
                s._ili.draw_line(x, yraw.min(), x, yraw.max(), c)
    print('leave page2')

def page3_daemon(flag_pause, flag_close, fps=1, area=[26, 56, 153, 183]):
    print('turn to page3')
    last_time = time.time()
    x = np.linspace(0, reader.sample_time, reader.window_size)
    sin_sig = 1e-3 * np.sin(2*np.pi*32*x).reshape(1, -1)
    x = np.arange(127).reshape(1, -1)
    blank = np.zeros((127, 127, 4), np.uint8)
    while not flag_close.isSet():
        flag_pause.wait()
        if (time.time() - last_time) < 1.0/fps:
            continue
            last_time = time.time()
        ch = channel_range['n']
        c = RGB_COLOR[ch]
        d = reader.data_frame
        server.send(d)
        d = si.notch(d[ch])
        s.widget['text', 23]['s'] = '%.2f' % move_coefficient(d)
        d = si.detrend(d)
        amp = si.fft(sin_sig + d, resolution=4)[1][:, :127]
        amp[-1] = 0
        amp = np.concatenate(( x, 127*(1 - amp/amp.max()) )).T
        img = Image.fromarray(blank)
        ImageDraw.Draw(img).polygon(map(tuple, amp), outline=c)
        s._ili.draw_rectf(*area, c=ILI9341_WHITE)
        s._ili.draw_img(area[0], area[1], np.uint8(img))
        s.widget['text', 21]['s'] = '%.2f' % tremor_coefficient(d)[0]
        s.widget['text', 22]['s'] = '%.2f' % stiff_coefficient(d)
        s.render('text', 21); s.render('text', 22); s.render('text', 23)
    print('leave page3')

def page4_daemon(flag_pause, flag_close, fps=1):
    print('turn to page4')
    start_time = [None, None]
    last_time = time.time()
    while not flag_close.isSet():
        flag_pause.wait()
        if (time.time() - last_time) < 1.0/fps:
            continue
            last_time = time.time()
        ch = channel_range['n']
        d = si.notch(si.detrend(reader[ch]))
        for i in np.arange(2, 8):
            if test_dict[(4, i)]:
                if i % 3 == 2:
                    s.widget['button', i]['s'] = '%.2f' % tremor_coefficient(d)[0]
                    s.render('button', i)
                elif i % 3 == 0:
                    s.widget['button', i]['s'] = '%.2f' % stiff_coefficient(d)
                    s.render('button', i)
                else:
                    if not start_time[(i-2)/3]:
                        start_time[(i-2)/3] = time.time()
                    s.widget['button', i]['s'] = '  {:4.1f}s '.format(
                        time.time() - start_time[(i-2)/3])
                    s.render('button', i)
            elif i % 3 == 1 and start_time[(i-2)/3]:
                start_time[(i-2)/3] = None
        for i in np.arange(21, 24):
            b = s.widget['button', i-19, 's'][:-1]
            a = s.widget['button', i-16, 's'][:-1]
            if b != '  test  ' and a != '  test  ':
                b, a = float(b), float(a)
                s.widget['text', i]['s'] = '%.2d%%' % (abs(b-a) / b)
                s.render('text', i)
    print('leave page4')

def page5_daemon(flag_pause, flag_close):
    print('turn to page5')
    print('Nothing to do! Abort')
    print('leave page5')

def tremor_coefficient(data, ch=0, distance=None):
    data = si.smooth(si.envelop(data), 15)[0]
    data[data < data.max() / 4] = 0
    peaks, heights = signal.find_peaks(data, 0, distance=si.sample_rate/10)
    return (si.sample_rate/(np.average(np.diff(peaks))+1),
            1000 * np.average(heights['peak_heights']))
    # # preprocessing
    # data = si.notch(si.detrend(data[ch]))[0]
    #
    # # peaks on raw data
    # #===========================================================================
    # # upper, lower = data.copy(), -data.copy()
    # # upper[data < 0] = lower[data > 0] = 0
    # #===========================================================================
    # # peaks on envelops
    # #===========================================================================
    # data = si.envelop(data, method=1)[0]  # method 1: combine upper&lower edge
    # #===========================================================================
    #
    # # smooth
    # data = si.smooth(data, 15, method=1)[0]  # combine neighboor peaks
    #
    # # peaks of upper and lower seperately
    # #===========================================================================
    # # upper_peaks, upper_h = signal.find_peaks(data, (0, None), distance=distance)
    # # lower_peaks, lower_h = signal.find_peaks(data, (None, 0), distance=distance)
    # # intervals = np.hstack((np.diff(upper_peaks), np.diff(lower_peaks)))
    # # heights = np.hstack((upper_h['peak_heights'], lower_h['peak_heights']))
    # #===========================================================================
    # # peaks of both upper and lower
    # #===========================================================================
    # data[data < data.max() / 4] = 0  # filter misleading extramax peaks
    # peaks, heights = signal.find_peaks(data, 0, distance=distance or si.sample_rate/10)
    # intervals = np.diff(peaks)
    # heights = heights['peak_heights']
    # #===========================================================================
    #
    # return si.sample_rate / np.average(intervals), 1000 * np.average(heights)

def stiff_coefficient(data, ch=0):
    b, a = signal.butter(4, 10.0/si.sample_rate, btype='lowpass')
    return si.rms(signal.lfilter(b, a, data, -1))

def move_coefficient(data, ch=0):
    data = si.notch(data)
    data = si.smooth(si.envelop(data, method=1), 10)[0]
    return np.average(data)


if __name__ == '__main__':
    username = 'test'
    try:
        print('username: ' + username)
    except NameError:
        username = check_input('Hi! Please offer your username: ', answer={})

    reader = Reader(sample_rate=500, sample_time=2, n_channel=8)
    reader.start()
    server = Socket_server()
    server.start()
    si = Signal_Info(500)
    s = Screen_GUI()
    s.start_touch_screen('/dev/ttyS1')
    s.load_layout('./files/layouts/layout-DBS-page1.pcl')
    change_page()
    IPython.embed()

    # reset_avr = SysfsGPIO(10) # PA10
    # reset_avr.export = True
    # reset_avr.direction = 'out'
    # reset_avr.value = 0
    # time.sleep(1)
    # reset_avr.value = 1
    # time.sleep(1)

    '''
    program_exit = threading.Event()

    try:
        reader = Reader(); reader.start(spi_device=(0, 1))
        s = Screen_GUI(spi_device=(0, 0))
        # s = Screen_GUI(screen_port='/dev/ttyS1', screen_baud=115200)
        s.start_touch_screen('/dev/ttyS2')
        # stop = virtual_serial()
        # s.start_touch_screen('/dev/pts/0')
        # s1 = serial.Serial('/dev/pts/1', 115200)
        # s.display_logo('./files/LOGO.bmp')
        s.display_logo('./files/LOGO.jpg')
        # s.widget = menu
        s.widget = menu_list['a'][menu_list['i']]
        s.render()
        while not program_exit.is_set():
            time.sleep(5)
    except KeyboardInterrupt:
        print('keyboard interrupt shutdown')
    except SystemExit:
        print('touch screen shutdown')
    except Exception:
        IPython.embed()
    finally:
        s.close()
        # s1.close()
        # stop.set()
        server.close()
    '''
