# Cat Activity Logger

import os, time, board
import math
import alarm
from busio import I2C
import mpu6886

import m5Lcd
import kintone

sleepInterval = 1
sumActivityInterval = 10

def logger(requests):
    # Activity Intervals
    sleepInterval = int(os.getenv("SLEEP_INTERVAL"))
    sumActivityInterval = int(os.getenv("SUM_ACTIVITY_INTERVAL"))
    mpu_range = int(os.getenv("ACCELEROMETER_RANGE"))
    
    CAT_WEIGHT = 15.0  # weight in kg 
    MET_ACTIVE = 2.0   # MET value when cat is moving (2.0 = roughly walking)
    MET_REST   = 1.0   # MET value when cat is resting
    THRESHOLD  = 0.57
    
    DEBUG_LOG = int(os.getenv("DEBUG_LOG"))
    
    # Kintone Settings
    SDOMAIN = os.getenv("SDOMAIN")
    APPID = int(os.getenv("APPID"))
    TOKEN = os.getenv("TOKEN")

    # Time Zone offset in seconds
    TZ_OFFSET = int(os.getenv("TZ_OFFSET"))
    timezoneOffset = TZ_OFFSET*60*60

    # Initializing MPU8668 
    i2c = I2C(board.G22, board.G21)
    mpu = mpu6886.MPU6886(i2c)

    #####
    # mpu.accelerometer_range
    # +----------------------+-------------------+------------------+
    # | accelerometer_range  | Measurement Range | Max Value (m/s²) |
    # +----------------------+-------------------+------------------+
    # | 0                    | ±2g               | ±19.62          |
    # | 1                    | ±4g               | ±39.24          |
    # | 2                    | ±8g               | ±78.48          |
    # | 3                    | ±16g              | ±156.96         |
    # +----------------------+-------------------+------------------+
    mpu.accelerometer_range = int(os.getenv("ACCELEROMETER_RANGE"))
    #####

    ac = mpu.acceleration
    acPrev = ac
    
    sumActivityValue = 0.0
    sumCalories = 0.0               # accumulated calories for the current upload interval
    dailyCalories = 0.0             # accumulated calories for the day
    dailyActiveTime = 0 

    # Initializing activity value
    sumActivityValue = 0
    previousTime = time.time() + timezoneOffset
    
    lastDate = time.localtime(time.time() + timezoneOffset)[0:3]
    
    while True:
        ac = mpu.acceleration
        acX = abs(ac[0] - acPrev[0])
        acY = abs(ac[1] - acPrev[1])
        acZ = abs(ac[2] - acPrev[2])
        acPrev = ac

        currentActivityValue = math.sqrt(acX**2 + acY**2 + acZ**2)
        sumActivityValue = sumActivityValue + currentActivityValue
        
        if currentActivityValue > THRESHOLD:
            # Cat is moving
            currentMET = MET_ACTIVE
            dailyActiveTime += sleepInterval    # increment active time counter
        else:
            # Cat is not moving
            currentMET = MET_REST
        
        # Calculate calories burned in this interval (interval is sleepInterval seconds)
        # Convert interval to hours for MET formula
        interval_hours = sleepInterval / 3600.0
        calories_this_interval = currentMET * CAT_WEIGHT * interval_hours  # kcal burned in this interval
        sumCalories += calories_this_interval
        dailyCalories += calories_this_interval
        
        print(calories_this_interval)

        currentTime = time.time() + timezoneOffset
        print(".", end="")

        if(currentTime - previousTime >= sumActivityInterval):
            previousTime = currentTime
            temperature = mpu.temperature
            
            intervalTotal = sumActivityValue  # total movement in this period
            intervalCalories = sumCalories    # calories burned in this period
            
            if temperature >= 60.0:
                shutdown()
            
            print(f"\nTotal: {sumActivityValue:.2f}, Temp: {temperature}")
            print(intervalCalories)

            payload = {"app": APPID,
                        "record": {"activity": {"value": round(intervalCalories, 4)},
                                   "temperature": {"value": temperature} }}

            recordId = kintone.uploadRecord(requests=requests,
                                            subDomain=SDOMAIN,
                                            apiToken=TOKEN,
                                            record=payload)

            if recordId is None:
                print(f"Failed to upload data to Kinton!")
                time.sleep(10)
                # sys.exit()

            sumActivityValue = 0
            sumCalories = 0.0

            # Check for new day
            currentDate = time.localtime(time.time() + timezoneOffset)[0:3]  # (Y, M, D)
            if currentDate != lastDate:
                print(f"New day detected. Yesterday's total calories: {dailyCalories:.1f} kcal, Active time: {dailyActiveTime} sec")
                dailyCalories = 0.0
                dailyActiveTime = 0
                lastDate = currentDate

    
        time.sleep(sleepInterval)


def shutdown():
    while True:
        timeAlarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 10)
        alarm.exit_and_deep_sleep_until_alarms(timeAlarm)
