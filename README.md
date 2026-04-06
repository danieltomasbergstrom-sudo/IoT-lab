# IoT Climate Monitoring System: From Sensor to Cloud
A collection of IoT projects and lab exercises focused on exploring connected devices, sensors, and embedded systems.
This guide covers the end-to-end setup of a temperature and humidity monitoring system using a Raspberry Pi, IoT Open (Lynx), Grafana, and Node-RED.

# Material
Raspberry Pi with 64bit operating system
Breadboard and some connection cables so that you can connect the pins from the Raspberry Pi to your breadboard. (If you have male to male connection cables you wont need the breadboard for this example, but it always good to have)
A DHT11 sensor.

# Preparations
Install Raspberry Pi OS 64bit on your Raspberry. Make sure you can log in to it from your computer. 
Please see this link on how to get started with Rasberry Pi:[Raspberry Pi Documentation, Getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html)
You should have an account on IoT Open that you can log into. You can create one here. https://lynx.iotopen.se/
Follow the steps in this awesome tutorial and make sure you understand the concept: https://github.com/mrejas/edu-iot-hands-on/blob/main/exercises/exercise-1.md


# Hardware Connections (DHT11 Sensor)
Before powering on your Raspberry Pi, connect the DHT11 sensor to the GPIO pins. The sensor typically has three pins: VCC, GND, and DATA.

Wiring Diagram:
VCC (Power) → Pin 1 (3.3V)
GND (Ground) → Pin 6 (GND)
DATA (Signal) → Pin 11 (GPIO 17)

Ensure your system is up to date and the necessary background services for IoT Open and MQTT are installed.
# 1. Update system and install Python 3
sudo apt update && sudo apt upgrade -y
sudo apt install python3 -y

# Install MQTT Broker and IoT Open core components
sudo apt install -y mosquitto mosquitto-clients iotopen-rt iotopen-edge scheduler iotopen-verify

# Install GPIO library for DHT sensors
sudo apt-get install libgpiod2 -y

First step done. Well done! 

# 2. Python Environment & Sensor Setup
We use a virtual environment to manage dependencies for the DHT11/DHT22 sensor.

# Create and activate a virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install the Adafruit DHT library
pip install adafruit-circuitpython-dht

Secound step done. Awesome! 

# 3. Grafana Installation & Configuration
Grafana provides the visual layer. We use a specific repository to ensure we get a version compatible with our plugins (e.g., v10.x).
Install Grafana
# Create keyring directory
sudo mkdir -p /etc/apt/keyrings/

# Download GPG key and add repository
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Update and install a specific stable version (v10.4.15 recommended for plugin compatibility)
sudo apt-get update
sudo apt-get install grafana=10.4.15

# 4. Install IoT Open Plugin
Download and move the plugin:
cd /var/lib/grafana/plugins
sudo wget https://github.com/IoTOpen/grafana-datasource-lynx/archive/refs/tags/2.2.1.zip
sudo unzip 2.2.1.zip
sudo mv grafana-datasource-lynx-2.2.1 iotopen-datasource

# 4.1 Allow Unsigned Plugins:
Edit /etc/grafana/grafana.ini and find the [plugins] section. Remove the semicolon ; and set:
allow_loading_unsigned_plugins = iotopen-datasource

# 4.2 Enable and Start Service:
sudo systemctl enable grafana-server
sudo systemctl restart grafana-server

# 4.3 Grafana Configuration (Step-by-Step)
Access the Grafana UI by navigating to http://<your_pi_ip>:3000 (Default login: admin/admin)
Add Data Source
1. Navigate to Administration -> Data Sources -> Add data source.
2. Search for IoT Open (Lynx).
3. URL: [https://lynx.iotopen.se](https://lynx.iotopen.se)
4. API Key: Enter your unique API Key from your IoT Open JSON file.
5. Click Save & Test.

# 4.4 Create the Dashboard in Grafana
1. Go to Dashboards -> New -> Add visualization.
2. Select the IoT Open data source.
3. Set the time range (top right) to Last 1 hour.

# 4.5 Configure Temperature Panel (Gauge)
* Query: Select your Installation ID and filter by name or topic to find your temperature data.
* Visualization: Choose Gauge from the right-hand menu.
* Standard Options: Set Min to 0 and Max to 50. Set unit to Celsius (°C).
* Thresholds:
  Base: Green
  25: Yellow
  28: Red (Critical threshold for alerts).

# 4.6 Configure Humidity Panel (Gauge)
Repeat the steps above but filter for your humidity data.
Standard Options: Set Min to 0 and Max to 100. Set unit to Percent (%).

# 5. Automation with Node-RED
Node-RED acts as the brain, processing logic and triggering alerts.
Installation
# Official install script for Raspberry Pi
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)

# Start and enable Node-RED
sudo systemctl enable nodered.service
sudo systemctl start nodered.service

# The Logic Flow
1. Access the Node-red editor at http://<your_pi_ip>:1880.
2. Lynx-In Node: Connects to the IoT Open broker and subscribes to your temperature topic.
Function Node: Contains the logic to check thresholds:
JavaScript
if (msg.payload.value > 28) {
    msg.payload = "Warning! Temperature is " + msg.payload.value + "°C";
    return msg;
}
return null;
3. Debug/Email Node: Outputs the warning to the console or sends a notification.

# 6. Running the Data Collection Script
The script lab1.py in the code directory reads data from the sensor and publishes it to the IoT Open broker via MQTT.
To start the data collection download the lab1.py file in the code folder to a folder of your choie. 

# Navigate to your code directory:
cd ~/code

# Activate the virtual environment:
source ../myenv/bin/activate

# Run the script:
python lab1.py
The script will now start sending temperature and humidity data every 10 seconds.
