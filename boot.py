import sys
import supervisor

import board
import displayio
import digitalio

import m5Wifi

def main():
    supervisor.runtime.autoreload = False
    supervisor.set_next_code_file(None)

    m5Wifi.connect_to_wifi()
    m5Wifi.connect_to_ntp()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
