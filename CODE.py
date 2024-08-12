from vl53l5cx.vl53l5cx import VL53L5CX
import time
from pynput import keyboard
import RPi.GPIO as GPIO

# Initialize sensor
driver = VL53L5CX()
if not driver.is_alive():
    raise IOError("VL53L5CX Device is not alive")

print("Initialising...")
t = time.time()
driver.init()
print(f"Initialised ({time.time() - t:.1f}s)")
print("Press the space bar to quit.")

# Initialize GPIO for LED
GPIO.setmode(GPIO.BOARD)
LED_PIN = 11
GPIO.setup(LED_PIN, GPIO.OUT)
pwm = GPIO.PWM(LED_PIN, 1000)  # 1 kHz PWM frequency
pwm.start(0)  # Start PWM with 0% duty cycle

# Start ranging
driver.start_ranging()

measurement_count = 0
quit_program = False

def on_press(key):
    global quit_program
    if key == keyboard.Key.space:
        quit_program = True
        return False

listener = keyboard.Listener(on_press=on_press)
listener.start()

def is_valid_measurement(distance_mm):
    # Add a realistic range for your application; for example, 0 to 4000 mm (0 to 4 meters)
    return 0 <= distance_mm <= 4000

try:
    while not quit_program:
        if driver.check_data_ready():
            ranging_data = driver.get_ranging_data()
            measurement_count += 1

            # Get the distance for the first zone (zone 0) in mm
            distance_mm = ranging_data.distance_mm[0]
            
            if not is_valid_measurement(distance_mm):
                print(f"{measurement_count}: Invalid measurement {distance_mm:.2f} mm")
                continue

            distance_cm = distance_mm / 10.0
            led_status = "OFF"

            # Adjust LED brightness based on distance thresholds
            if 1< distance_cm < 3:
                pwm.ChangeDutyCycle(45  )  # 50% brightness
                led_status = "Half Bright"
            elif 0 <= distance_cm <= 1:
                pwm.ChangeDutyCycle(100)  # 100% brightness
                led_status = "Full Bright"
            else:
                pwm.ChangeDutyCycle(15)  # 0% brightness
                led_status = "little"

            print(f"{measurement_count}: {distance_cm:.2f} cm, LED Status: {led_status}")

        time.sleep(0.1)  # Decrease sleep time to check more frequently

except KeyboardInterrupt:
    pass

print("Stopping ranging...")
driver.stop_ranging()
print("Ranging stopped.")
pwm.stop()
GPIO.cleanup()
listener.stop() 
