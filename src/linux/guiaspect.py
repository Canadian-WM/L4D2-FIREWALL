from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QApplication, QLabel, QTextEdit, QCheckBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor,QBrush
from linux.firewallcore import blacklist,interactionqueue
import threading, time, subprocess
import lib.cfgbasic as cfgbasic

class settings:
    rmfwonexit=False
    #pfwall=False


def savemanual(ips):
    ips=ips.strip()
    with open("settings/iplist_manual.txt", "w") as f:
        f.write(ips)
    print("saved")

class FirewallGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("L4D2 Firewall Blocker - Linux")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.ip_list = QListWidget()
        self.layout.addWidget(self.ip_list)

        for ip in blacklist:
            self.ip_list.addItem(ip)

        self.btn1 = QPushButton("Settings")
        self.btn1.clicked.connect(self.open_settings)
        self.layout.addWidget(self.btn1)

        threading.Thread(target=self.queue_listener, daemon=True).start()

    def open_settings(self):
        self.settingspage=SettingsGUI()
        self.settingspage.show()

    # TODO: FADE FROM RED TO FUCKING DEFAULT COLOUR
    def flash_red(self, ip):
        for i in range(self.ip_list.count()):
            item = self.ip_list.item(i)
            if item.text() == ip:
                item.setBackground(QBrush(QColor("red")))
                time.sleep(0.1)
                item.setBackground(QBrush())
                break

    def queue_listener(self):
        while True:
            ip = interactionqueue.get()
            if ip:
                self.flash_red(ip)

    def closeEvent(self, event):
        if settings.rmfwonexit:
            subprocess.run("iptables -D INPUT -m set --match-set l4d2blacklist src -j LOG 2>/dev/null; iptables -D INPUT -m set --match-set l4d2blacklist src -j DROP 2>/dev/null; iptables -D OUTPUT -m set --match-set l4d2blacklist dst -j LOG 2>/dev/null; iptables -D OUTPUT -m set --match-set l4d2blacklist dst -p tcp -j REJECT --reject-with tcp-reset 2>/dev/null; iptables -D OUTPUT -m set --match-set l4d2blacklist dst -p udp -j REJECT --reject-with icmp-port-unreachable 2>/dev/null", shell=True)

class SettingsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        textlabel1 = QLabel("Manual IP List:")
        layout.addWidget(textlabel1)

        self.textinput1=QTextEdit()
        with open("settings/iplist_manual.txt", "r") as f:
            self.manualtext=f.read()
            self.textinput1.setText(self.manualtext)
        layout.addWidget(self.textinput1)

        #self.checkbox2=QCheckBox("Permanent firewall")
        #self.checkbox2.toggled.connect(self.pfwall)
        #layout.addWidget(self.checkbox2)

        setting=cfgbasic.openCfg("settings/settings.cfg")
        settings.rmfwonexit=(True if setting["rmfwonexit"]=="True" else False)

        self.checkbox1=QCheckBox("Remove firewall on exit")
        self.checkbox1.toggled.connect(self.rmfwonexit)
        self.checkbox1.setChecked(settings.rmfwonexit)
        layout.addWidget(self.checkbox1)

    def rmfwonexit(self, boolean):
        settings.rmfwonexit=boolean
        #if boolean:
        #    self.checkbox2.hide()
        #    self.checkbox2.setChecked(False)
        #else:
        #    self.checkbox2.show()
    #def pfwall(self,boolean):
    #    settings.pfwall=boolean

    def closeEvent(self, event):
        textrn=self.textinput1.toPlainText()
        if textrn!=self.manualtext:savemanual(textrn)
        setting=cfgbasic.openCfg("settings/settings.cfg")
        setting["rmfwonexit"]=self.checkbox1.isChecked()
