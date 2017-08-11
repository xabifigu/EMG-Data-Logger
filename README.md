# EMG Data Logger

## Overview
The goal of this project is simple: read EMG data from the muscles and store and represent this data on a PC.
The data is stored in a CSV type file (*.emgdat*), which makes easier the manage of it.
If the Python script is used (whether the gui or the single script), the data can be seen in real time.

## Parts
- MyoWare: EMG sensor
- DE0-Nano (FPGA): read and digitalize data from MyoWare
- HC-05 (Bluetooth module): communication between FPGA and PC
- Python (Desktop GUI) or Octave: recolect data from FPGAStore and represent data 

## Tools
- ModelSim-Altera 10.1d
- Quartus II 13.0
- Python 3.5
- Octave 4.2.1