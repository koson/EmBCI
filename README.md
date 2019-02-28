# Required modules
simply run

`sudo pip install -r ./requirements.txt`

or

`sudo pip3 install -r ./requirements.txt`

This program is py2 && py3 compatiable after 2018.03.23 modification(theorically...)

# How to use
`python2 run_me.py` or `python3 run_me.py`


# Connection
- Communicate with [ADS1299](http://www.ti.com/product/ADS1299) through SPI
interface on OrangePi pin `CS/PA13`, `CLK/PA14`, `MOSI/PA15` and `MISO/PA16`

- On shield Atmega328P(Arduino Uno/Nano) is connected to `UART2_TX/PA00` and
`UART2_RX/PA01`

- Control SSD1306 0.96' OLED screen by SPI or ILI9325 2.3' LCD screen through
on shield Arduino by serial

- Broadcast collected raw data from ADS1299 to wifi port 9999(default) by TCP
socket, there are two ways to grab data from network
    - Connect OrangePi to your LAN wifi network and check its IP address, you
    can login to router(e.g. TP-Link @ `192.168.1.1`) or use any other methods
    to get OrangePi IP address.
    - Set OrangePi as a wifi hotpot, connect your PC/laptop/phone to this
    network and this way OrangePi IP address will be `192.169.0.1`(usually)


## Get data from matlab
- Make sure orangepi and your PC are in same LAN
- Here's an example script to fetch data through socket in matlab

```Matlab
% socket server on orangepi default listen on port 9999.
client = tcpclient('192.168.10.10', 9999)

% 8-channel float32 data --> 8_ch * 32_bits / 8_bits = 32 bytes data
data = client.read(32)

% unpack bytes into float32(single)
data = typecast(data, 'single')

% here data is 1x8 vector
data
```


# Project structure
|    folder    |    description    |
| :----------- | :---------------- |
|     data     | save biosignal data with label in each subfolder named by username |
|    models    | save trained models with weight for each user |
|     src      | preprocessing algorithms, classifiers and frameworks |
|    test      | testing new ideas |
|    utils     | common functions, gym clients, data IO, etc. |
|   run_me.py  | bootloader script of recognition program |
|   run_me1.py | bootloader script of Screen GUI |


# Supported gyms
Currently we only support two environments
- plane-war-game: written by [@buaawyz](https://github.com/buaawyz),
[installation guide](https://github.com/hankso/gym_plane_python),
run `python main.py` first and then `from gyms import PlaneClient as Client`
- torcs-car-game: see more details at [gym_torcs](https://github.com/ugo-nama-kun/gym_torcs)


## EmBCI
EmBCI is Embedded Brain Computer Interface, a bio-signal acquisition and processing platform.

It's composed of a **Hardware**, a **Python library** and a **Linux Service Interface**.

## Hardware

## Python lib

## Service
EmBCI has a `Linux` service interface to work properly on embedded devices.

More details at [files/service](files/service).


## Install
### Debian & Ubuntu & Windows
`pip install embci` **(to be implemented, not working now)**

### Install from source
```bash
git clone git@github.com:hankso/EmBCI.git && cd EmBCI
sudo python -m pip install -r ./requirements.txt
python setup.py build && sudo python setup.py install
```

This program is py2 && py3 compatiable.

## Output Interface
### Get data from matlab
- Here we use Orange Pi + EmBCI Shield Rev.A7
- Make sure Orange Pi and your PC are in same LAN
- Here's an example script to fetch data through socket in `Matlab`

```Matlab
% socket server on orangepi default listen on port 9999.
client = tcpclient('192.168.10.10', 9999)

% 8-channel float32 data --> 8_ch * 32_bits / 8_bits = 32 bytes data
data = client.read(32)

% unpack bytes into float32(single)
data = typecast(data, 'single')

% here data is 1x8 vector
data
```

## Project structure
|    folder     |    description    |
| :------------ | :---------------- |
|    embci      | Preprocessing algorithms, classifiers, WebUI and frameworks |
|   files/avr   | On shield Atmega328P firmware |
|  files/esp32  | On shield ESP32 firmware and burning tools |
| files/layouts | Saved SPI-Screen GUI layouts in `python-pickle` format |
| files/service | Linux service files |


## TODOs
### Documents
- This page & README
- embci lib docs

### Hardware Design
- ESP32
    - Serial connection higher baudrate (like 921600)
    - Act as a portable WiFi card: WiFi-echo (through Serial/I2C)
    - Change command interface from SPI to Serial
- ADS1299 better de-noising
- PCB shielding cases

### Algorithums
- SSVEP & P300
- ERP/EDP
- Motor Imagery

### Application
- Parkinson DBS treatment recovery
- Online SSVEP mind-typing
- Sign language sEMG recognition
