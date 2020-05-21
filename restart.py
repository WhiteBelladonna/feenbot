import time
import subprocess
import sys
print("Waiting for Bot to Shut down.")
time.sleep(1)
subprocess.Popen([sys.executable, "./faqbot3.py"])