import platform
import os, sys, subprocess
from PyQt6.QtWidgets import QApplication
import lib.msgbox as msgbox

namo = platform.system()

if namo == "Linux":
    print("linux")
    if os.getuid()!=0:
        msgbox.show(1,"FATAL ERROR","Run as sudo!")
        sys.exit(1)
    if subprocess.run("command -v iptables",shell=True).returncode!=0:
        subprocess.run("apt install iptables -y")
    if subprocess.run("command -v ipset",shell=True).returncode!=0:
        subprocess.run("apt install ipset -y")
    from linux.firewallcore import blacklist,interactionqueue
    from linux.guiaspect import FirewallGUI
elif namo == "Windows":
    print("win32")
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        msgbox.show(1,"FATAL ERROR","Run as admin!")
        sys.exit(1)
    from win32.firewallcore import blacklist
    from win32.guiaspect import FirewallGUI
else:
    print("what the fuck is " + namo + "?")
print("this is debug")
try:
    app = QApplication([])
    window = FirewallGUI()
    window.show()
    app.exec()
except NameError:
    print("are you using macOS")
