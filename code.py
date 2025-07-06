import sys, os, time
import m5Lcd
import m5Wifi
import cat

requests = None

def main():
    bgColor = 0x0000A0
    fontColor = 0xFFFFFF

    try:
        display = m5Lcd.initDisplay(bgColor)
        #display = None

        # Show Text on the Display and Turn it off
        myText = "Cat Logger"
        m5Lcd.boot(myText, fontColor, bgColor, display)
    except:
        pass

    # Creating adafruit_requests session
    requests = m5Wifi.create_https_requests()
    
    # Main code
    cat.logger(requests)
      
    return 0

if __name__ == "__main__":
    sys.exit(main())

