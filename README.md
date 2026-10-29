# ESP32 Hazardous Gas and Room Climate Monitor

[![Platform: ESP32](https://img.shields.io/badge/Platform-ESP32-blue.svg)](https://www.espressif.com/)
[![Runtime: MicroPython](https://img.shields.io/badge/Runtime-MicroPython-yellow.svg)](https://micropython.org/)
[![Simulation: Wokwi](https://img.shields.io/badge/Simulated%20on-Wokwi-brightgreen.svg)](https://wokwi.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An environmental safety monitor built for the ESP32 using MicroPython. It tracks hazardous gas concentrations, ambient temperature, and humidity, showing readings on an OLED screen and sounding a buzzer when gas crosses set limits.

---

## What the System Does

- Gas monitoring: Reads analog gas levels and applies a 10-sample moving average filter to reduce ADC noise.
- Climate tracking: Reads temperature in degrees Celsius and relative humidity from a DHT22 sensor.
- Local display: Updates an SSD1306 OLED screen with current values and status.
- Audio alarms: Drives a piezo buzzer with distinct frequencies and beep counts depending on gas level.
- Serial output: Prints JSON telemetry over UART at 2 Hz for logging or external microcontrollers.

---

## Screen Dashboard and Alarm States

```
┌──────────────────────────┐
│ === AIR SENTINEL ===     │
│                          │
│ Gaz : 450 PPM            │
│ Temp: 24.5 C             │
│ Hum : 58.0 %             │
│ Etat: WARNING            │
└──────────────────────────┘
```

| State | Gas Threshold | OLED Status | Buzzer Pattern | Action |
| :--- | :--- | :--- | :--- | :--- |
| SAFE | Below 300 PPM | Etat: SAFE | Silent | Normal air levels |
| WARNING | 300 to 699 PPM | Etat: WARNING | 1 short beep (1500 Hz) | Inspect burners and valves |
| CRITICAL | 700 PPM or higher | Etat: CRITICAL | 3 rapid beeps (2500 Hz) | Evacuate area immediately |

---

## Hardware Wiring

| Component | Pin | ESP32 Pin | Details |
| :--- | :--- | :--- | :--- |
| Gas Sensor (MQ-2 or MQ-135) | A0 | GPIO 34 | Analog ADC1 input (0 to 3.3V) |
| Gas Sensor | VCC / GND | 5V (or VIN) / GND | Sensor heater and amplifier power |
| DHT22 Sensor | OUT / Data | GPIO 15 | Digital 1-wire pin |
| DHT22 Sensor | VCC / GND | 3V3 / GND | 3.3V power |
| OLED Display (SSD1306 128x64) | SDA | GPIO 21 | I2C data |
| OLED Display | SCL | GPIO 22 | I2C clock |
| OLED Display | VCC / GND | 3V3 / GND | 3.3V power |
| Piezo Buzzer | Positive (+) | GPIO 27 | PWM signal |
| Piezo Buzzer | Negative (-) | GND | Ground |

Note on MQ sensor voltage: Standard MQ series modules need 5V on VCC to power the internal heater. Make sure the analog output does not exceed 3.3V when connected to ESP32 GPIO 34. Most breakout boards with built-in dividers are safe to plug directly into the 3.3V ADC.

---

## Step-by-Step Guide: Running on Real Hardware

### 1. Parts Needed
- 1x ESP32 DevKit V1 board
- 1x MQ-2 or MQ-135 gas sensor breakout board
- 1x DHT22 (AM2302) sensor module
- 1x 0.96 inch I2C OLED display (SSD1306, 128x64)
- 1x 5V piezo buzzer
- Breadboard and jumper wires
- Micro-USB or USB-C cable for power and programming

---

### 2. Physical Connections
1. Seat the ESP32 on the breadboard.
2. Connect ESP32 3V3 to the positive rail and GND to the negative rail.
3. Wire the OLED screen: VCC to 3V3, GND to GND, SDA to GPIO 21, and SCL to GPIO 22.
4. Wire the DHT22: VCC to 3V3, GND to GND, and Data to GPIO 15.
5. Wire the buzzer: positive pin to GPIO 27, negative pin to GND.
6. Wire the gas sensor: VCC to 5V (or VIN pin from USB), GND to GND, and A0 to GPIO 34.

---

### 3. Flashing MicroPython
1. Download Thonny IDE from thonny.org.
2. Download the standard ESP32 MicroPython firmware (.bin) from micropython.org.
3. Plug the ESP32 into your computer.
4. In Thonny, open Tools > Options > Interpreter.
5. Select MicroPython (ESP32) and choose your COM port.
6. Click Install or update MicroPython, select your port and the downloaded .bin file, then click Install.

---

### 4. Uploading the Code
1. Open Thonny with the board connected.
2. Open `ssd1306.py` in Thonny, click File > Save as > MicroPython device, and name it `ssd1306.py`.
3. Open `main.py` in Thonny, click File > Save as > MicroPython device, and name it `main.py`.
4. Press the physical EN or RST button on the ESP32. The code will start running automatically and turn on the OLED screen.

---

### 5. Testing the Hardware
- Warm-up period: MQ gas sensors take 1 to 2 minutes to stabilize after power is applied because the internal heater needs to reach operating temperature.
- Temperature and humidity: Breathe near the DHT22. The numbers on the screen will shift within 2 to 4 seconds.
- Gas alert test: Take a regular butane lighter, bring it near the sensor, and press the release lever without sparking a flame. The PPM value on the display will rise. Above 300 PPM the buzzer will beep once. Above 700 PPM it will switch to continuous triple beeps. Releasing the lever returns the reading to normal and silences the buzzer.

---

## Wall Placement Rules

Mounting height depends on which gas you want to catch:

```
       CEILING
  ┌─────────────────────────────────────────────────────┐
  │ [30 cm below ceiling]                               │
  │ Natural Gas (Methane): lighter than air, rises      │
  │                                                     │
  │ [Eye level: 1.5 meters]                             │
  │ Carbon Monoxide and room temperature/humidity       │
  │                                                     │
  │ [30 cm above floor]                                 │
  │ Butane and Propane: heavier than air, sinks down    │
  └─────────────────────────────────────────────────────┘
       FLOOR
```

- Distance: Keep the device 1 to 2 meters away from stoves, gas cylinders, or heaters. Do not mount it directly over flames or cooking oil.
- Drafts: Avoid placing it right next to open windows or exhaust fans that blow fresh air directly onto the sensor.

---

## Wokwi Simulation

You can test this setup in your browser without any hardware:

[Launch Live Simulation on Wokwi](https://wokwi.com/projects/479238633086989313)

---

## Project Structure

```
├── .gitignore          # Git exclusion rules
├── diagram.json        # Wokwi simulation schematic and wiring
├── LICENSE             # MIT license
├── main.py             # MicroPython firmware
├── README.md           # Project documentation and build guide
├── ssd1306.py          # MicroPython I2C driver for SSD1306 OLED
└── wokwi.toml          # Local Wokwi configuration
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
