import clr
import os
import sys

# Get absolute path of the DLL in the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "OpenHardwareMonitorLib.dll")

sys.path.append(script_dir)
clr.AddReference("OpenHardwareMonitorLib")

from OpenHardwareMonitor import Hardware

# Initialize OpenHardwareMonitor Computer instance
computer = Hardware.Computer()
computer.CPUEnabled = True
computer.Open()

def get_temperature():
    try:
        for hw in computer.Hardware:
            if hw.HardwareType == Hardware.HardwareType.CPU:
                hw.Update()
                for sensor in hw.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature and "Core #0" in sensor.Name:
                        return f"{sensor.Value:.1f}°C"
        return "Unavailable"
    except Exception as e:
        return f"Error: {e}"
