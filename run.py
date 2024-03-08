from threading import Thread
import serial
import time
import pygame
import math
import threading


class SerialConnect:
    def __init__(self, serialPort='COM5', serialBaud=115200):
        self.port = serialPort
        self.baud = serialBaud
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.accelerationData = ""
        self.temperatureData = ""  # Added a variable to store temperature data

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            self.serialConnection.close()
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except Exception as e:
            print(f"Failed to connect with {str(serialPort)} at {str(serialBaud)} BAUD.")
            print(str(e))

    def readSerialStart(self):
        if not self.thread:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()

    def backgroundThread(self):
        self.serialConnection.open()
        while self.isRun:
            if self.serialConnection.in_waiting:
                data_str = self.serialConnection.readline().decode('ascii', errors='replace').strip()
                if data_str:
                    self.isReceiving = True
                    data_parts = data_str.split(" , ")
                    if len(data_parts) == 2:
                        self.accelerationData = data_parts[0]
                        self.temperatureData = data_parts[1]
                    # Optionally, print to verify
                    # print("Acceleration:", self.accelerationData, "Temperature:", self.temperatureData)
        self.serialConnection.close()

    def close(self):
        self.isRun = False
        self.thread.join()


class MotorSoundController(threading.Thread):
    def __init__(self, serialConnect, motorSoundFile='motor_sound.wav'):
        super().__init__()
        self.serialConnect = serialConnect
        pygame.init()
        pygame.mixer.init()
        self.motorSound = pygame.mixer.Sound(motorSoundFile)
        self.motorChannel = pygame.mixer.Channel(0)
        self.currentVolume = 0
        self.accelerationFlag = False
        self.overwrittenVolume = 0
        self.targetVolume = 0
        self.i = 0
        self.decayFactor = 0.00002
        self.daemon = True  # Ensure this thread exits when main program does

    def run(self):
        self.monitorSerial()

    def monitorSerial(self):
        while self.serialConnect.isRun:
            if self.serialConnect.isReceiving:
                self.update(self.serialConnect.accelerationData, self.serialConnect.temperatureData)

    def update(self, accelerationData, overtakeData):
        try:
            x_acceleration = float(accelerationData.split(',')[0])

            if abs(x_acceleration) < 0.05:
                if not self.accelerationFlag and self.currentVolume > 0.1:
                    # Flag that we've dropped below threshold and need to start decay
                    self.accelerationFlag = True
                    self.overwrittenVolume = self.currentVolume
                self.targetVolume = 0.1
            else:
                # When acceleration is again above threshold
                self.targetVolume = max(0, min(1, (x_acceleration + 1) / 2))
                self.accelerationFlag = False
                # print(f"Target volume: {self.targetVolume}")

            if self.accelerationFlag:
                # Apply an exponential decay based on the number of updates since decaying started
                decay = self.overwrittenVolume * math.exp(-self.decayFactor * self.overwrittenVolume)
                self.currentVolume = max(self.targetVolume, decay)  # Never below idle volume
                self.overwrittenVolume = self.currentVolume  # Update overwritten for gradual decrease
            else:
                # Directly set to target volume if no decay is needed
                self.currentVolume = self.targetVolume

            self.motorChannel.set_volume(self.currentVolume)
            if not self.motorChannel.get_busy():
                self.motorChannel.play(self.motorSound, loops=-1)

        except ValueError:
            print("Could not convert acceleration to float")

    def close(self):
        self.serialConnect.isRun = False



class TemperatureAlertController(threading.Thread):
    def __init__(self, serialConnect, alertSoundFile='overtake.mp3'):
        super().__init__()
        pygame.init()
        pygame.mixer.init()
        self.serialConnect = serialConnect
        self.alertSound = pygame.mixer.Sound(alertSoundFile)
        self.alertChannel = pygame.mixer.Channel(1)
        self.previousTemperature = '0'
        self.daemon = True  # Ensure this thread exits when the main program does

    def run(self):
        while self.serialConnect.isRun:
            self.update(self.serialConnect.temperatureData)
            time.sleep(0.1)  # Reduce CPU usage

    def update(self, temperatureData):
        print(temperatureData)
        currentTemperature = temperatureData
        # Check if temperature has changed from 0 to 1 and the alert is not currently playing
        if currentTemperature == '1' and self.previousTemperature == '0' and not self.alertChannel.get_busy():
            self.alertChannel.play(self.alertSound)
        self.previousTemperature = currentTemperature

# Your main function should initiate threads without calling monitorSerial directly for controllers:

def main():
    portName = 'COM5'
    baudRate = 9600

    s = SerialConnect(serialPort=portName, serialBaud=baudRate)
    s.readSerialStart()

    motorSoundFile = 'engine-6000.mp3'
    motorController = MotorSoundController(serialConnect=s, motorSoundFile=motorSoundFile)
    motorController.start()

    temperatureAlertController = TemperatureAlertController(s, 'files/car_passing_sound.mp3')
    temperatureAlertController.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        s.close()
        print("Program terminated.")

if __name__ == "__main__":
    main()

