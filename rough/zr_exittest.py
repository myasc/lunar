from time import sleep

try:
    while True:
        print("hello")
        # x = 10/0
        sleep(10)
except KeyboardInterrupt:
    print("Exiting")
    print("Cancel all hellos")
    print("Programme aborted by user")
    exit()
except:
    print("Unknow exception")
