import time
import subprocess
import sys
print("Waiting for Bot to Shut down.")
time.sleep(1)
print("Pulling Update")
subprocess.call("git pull https://github.com/d3molite/feenbot", shell=True)
time.sleep(1)
subprocess.Popen([sys.executable, "./feenbot.py"])