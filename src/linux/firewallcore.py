import sys
import subprocess
import requests, queue, threading
interactionqueue=queue.Queue()
blacklist=[]

# TODO: DETECT DISTRO AND CHANGE LOGS LOCATION
logs="/var/log/kern.log" # debian default i guess

r=requests.get("https://raw.githubusercontent.com/Canadian-WM/L4D2-FIREWALL/refs/heads/blocked-ips/blocked_ips.txt")
if r.status_code==200:
    blacklist=[line.strip() for line in r.text.splitlines() if line.strip()]
else:
    sys.exit(1)

with open("settings/iplist_manual.txt", "r") as f:
    blacklist += [line.strip() for line in f.read().splitlines() if line.strip()]
subprocess.run("ipset create l4d2blacklist hash:ip -exist", shell=True)
for ip in blacklist:
    subprocess.run(f"ipset add l4d2blacklist {ip} -exist", shell=True)
subprocess.run("iptables -C INPUT -m set --match-set l4d2blacklist src -j LOG 2>/dev/null || iptables -A INPUT -m set --match-set l4d2blacklist src -j LOG; iptables -C INPUT -m set --match-set l4d2blacklist src -j DROP 2>/dev/null || iptables -A INPUT -m set --match-set l4d2blacklist src -j DROP; iptables -C OUTPUT -m set --match-set l4d2blacklist dst -j LOG 2>/dev/null || iptables -A OUTPUT -m set --match-set l4d2blacklist dst -j LOG; iptables -C OUTPUT -m set --match-set l4d2blacklist dst -p tcp -j REJECT --reject-with tcp-reset 2>/dev/null || iptables -A OUTPUT -m set --match-set l4d2blacklist dst -p tcp -j REJECT --reject-with tcp-reset; iptables -C OUTPUT -m set --match-set l4d2blacklist dst -p udp -j REJECT --reject-with icmp-port-unreachable 2>/dev/null || iptables -A OUTPUT -m set --match-set l4d2blacklist dst -p udp -j REJECT --reject-with icmp-port-unreachable", shell=True)



# log the ip connection attemps for decoration
def mainfirewall():
    with subprocess.Popen(["tail", "-F", logs], stdout=subprocess.PIPE, text=True) as h:
        for line in h.stdout:
            for ip in blacklist:
                if ip in line:
                    interactionqueue.put(ip)
                    print("INTERACTION FROM {"+ip+"} BLOCKED")
threading.Thread(target=mainfirewall, daemon=True).start()
