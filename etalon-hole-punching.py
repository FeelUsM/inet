from pathlib import Path
import time
import os
import sys


def cls():
    os.system("cls" if os.name == "nt" else "clear")


try:
    scriptname = Path(__file__).name
except:
    scriptname = "CnC.py"
try:
    verfrom = time.ctime(os.path.getmtime(__file__))
except:
    verfrom = "!No time!"


import threading
import socket
import random
import hashlib
import json
import logging
import pdb


class Debug(pdb.Pdb):
    def __init__(self, *args, **kwargs):
        super(Debug, self).__init__(*args, **kwargs)
        self.prompt = "CnC Debug Shell >>> "

    def shell(self):
        self.set_trace()


debug = Debug()
# logging.warn(f"Event logging is enabled. You can see it in {scriptname}.log")
logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, filename=f"{scriptname}.log"
)
logging.info("Hello world!")
logging.getLogger().setLevel(logging.DEBUG)


def get_files():
    '''
    возвращает имена баз разширений всех html-файлов в текущей директории
    '''
    matches = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".html"):
                matches.append(os.path.splitext(file)[0])
    return matches


def dat_to_bytes(diction: dict) -> bytes:
    return json.dumps(diction).encode("cp866")


def bytes_to_dat(byte: bytes) -> dict:
    return json.loads(byte.decode("cp866"))


def checksum(b):
    return hashlib.blake2s(b, digest_size=4).hexdigest()


_alreadyused = set()
def randomport():
    '''
    возвращает случайное число 16000..65535, которое не бало использовано
    '''
    global _alreadyused
    p = random.randint(16000, 65535)
    while p in _alreadyused:
        p = random.randint(16000, 65535)
    _alreadyused.update({p})
    return p


def aegis(f):
    '''
    враппер, запускает функцию f() пока она не закончится удачно
    '''
    def wr():
        while 1:
            try:
                f()
                break
            except Exception as e:
                logging.critical(e)

    return wr


def STUN(port, host="stun.ekiga.net"):
    '''
    возвращает внешний ip:port
    '''
    logging.debug(f"STUN request via {host}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.setblocking(0)
    server = socket.gethostbyname(host)
    work = True
    while work:
        sock.sendto(
            b"\x00\x01\x00\x00!\x12\xa4B\xd6\x85y\xb8\x11\x030\x06xi\xdfB",
            (server, 3478),
        )
        for i in range(20):
            try:
                ans, addr = sock.recvfrom(2048)
                work = False
                break
            except:
                time.sleep(0.01)

    sock.close()
    return socket.inet_ntoa(ans[28:32]), int.from_bytes(ans[26:28], byteorder="big")


def addr2int(ip, port: int):
    '''
    ip:port -> 48-битное число
    '''
    binport = bin(port)[2:].rjust(16, "0")
    binip = "".join([bin(int(i))[2:].rjust(8, "0") for i in ip.split(".")])
    return int(binip + binport, 2)


def int2addr(num):
    '''
    48-битное число -> ip:port
    '''
    num = bin(num)[2:].rjust(48, "0")
    print(num)
    num = [
        str(int(i, 2))
        for i in [num[0:8], num[8:16], num[16:24], num[24:32], num[32:48]]
    ]
    return ".".join(num[0:4]), int(num[4])


pool = []  # Pool for commands to any session (like RQD to initiate data update)

missed_messages = (
    set()
)  # Storage for hashes of required but missed messages (to request them later)

data = {}
sessions = []


def mass_command(c):
    '''
    добавляет c в pool
    '''
    global pool
    pool.append(c)


def data_add(item):
    '''
    добавляет сообщение в data
    '''
    data.update({checksum(item.encode("cp866")): item})


def data_dump():
    '''
    сохраняет data на диск
    '''
    with open(f"{scriptname}.chat-savefile.json", "w") as f:
        json.dump(data, f)


def data_load():
    '''
    загружает data с диска
    '''
    global data
    try:
        with open(f"{scriptname}.chat-savefile.json", "r") as f:
            data = json.load(f)
    except:
        logging.error(f"No save file exists! New one created")
        with open(f"{scriptname}.chat-savefile.json", "w") as f:
            json.dump({}, f)


class Session:
    def __init__(self):
        # self.prefix="IDL"
        self.immortal = False
        self.local_port = randomport()
        for i in range(10):
            self.public_ip, self.public_port = STUN(self.local_port)
        self.socket = None
        self.client = None
        self.thread = None
        logging.info(f'"{self.public_ip}",{self.public_port}')

    def make_connection(self, ip, port, timeout=10):
        logging.debug(f"Start waiting for handshake with {ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # работаем по UDP
        sock.bind(("0.0.0.0", self.local_port)) # устанавливаем локальный порт
        sock.setblocking(0) # recvfrom() - не блокирующий
        while True:
            sock.sendto(b"Con. Request!", (ip, port)) # шлем запрос на дарес
            time.sleep(2)
            try:
                ans, addr = sock.recvfrom(9999)
                sock.sendto(b"Con. Request!", (ip, port))
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(("0.0.0.0", self.local_port))
                sock.setblocking(0)
                self.client = (ip, port)
                self.socket = sock
                logging.debug(f"Hole with {self.client} punched!")
                break
            except Exception as e:
                assert timeout > 0
                timeout -= 1
                logging.debug(f"No handshake with {ip}:{port} yet...")

    def backlife_cycle(self, freq=1):
        global sessions
        if self.immortal:
            logging.warning(f"{self.client} session beacame immortal")
            self.life_cycle = aegis(self.life_cycle)
        th = threading.Thread(target=self.life_cycle, args=(freq,))
        th.start()
        self.thread = th
        logging.warning(f"Session with {self.client} stabilized!")
        # sessions.append(self)

    def life_cycle(self, freq=1):
        global data
        global sessions
        global pool
        c = 0
        while 1:
            if len(pool):
                pref = pool.pop(0)
            else:
                pref = b"KPL"

            self.socket.sendto(pref, self.client)  # Keep-alive
            time.sleep(max(random.gauss(1 / freq, 3), 0))

            while True:
                try:
                    ans, reply_addr = self.socket.recvfrom(9999)
                    logging.debug(
                        f"{self.client[0]}: Recieved {ans[:3].decode('cp866')} from {reply_addr}: {ans}"
                    )
                except:
                    break

                if ans[:3] == b"KPL":
                    c += 1
                    if c % 10 == 0:
                        logging.debug(
                            f"{self.client[0]}: Requesting Datagram     {c//10}"
                        )
                        self.socket.sendto(b"RQD", self.client)
                        c += 1
                    elif c % 33 == 0:
                        logging.debug(
                            f"{self.client[0]}: Requesting Session List {c//33}"
                        )
                        self.socket.sendto(b"RQS", self.client)
                        c += 1

                # ----------------------------------------Hashes (keys) sync (disabled now)----------------------------------------
                elif ans[:3] == b"RQH":
                    logging.debug(f"{self.client[0]}: Sending hashes")
                    self.socket.sendto(
                        b"HAS" + dat_to_bytes(list(data.keys())), self.client
                    )

                elif ans[:3] == b"HAS":
                    missed_messages.update(
                        set(bytes_to_dat(ans[3:])) - set(data.keys())
                    )

                # ----------------------------------------Data sync----------------------------------------
                elif ans[:3] == b"RQD":
                    if ans[3:] != b"":
                        logging.debug(f"{self.client[0]}: Sending specific datagram")
                        n = {}
                        r = set(bytes_to_dat(ans[3:]))
                        for i in r:
                            if i in data:
                                n.update({i: data[i]})
                        logging.debug(f"{self.client[0]}: Sending {n}")
                        self.socket.sendto(b"DAT" + dat_to_bytes(n), self.client)
                    else:
                        logging.debug(f"{self.client[0]}: Sending datagram")
                        self.socket.sendto(b"DAT" + dat_to_bytes(data), self.client)

                elif ans[:3] == b"DAT":
                    data.update(bytes_to_dat(ans[3:]))

                # ----------------------------------------IP list sync-------------------------------------
                elif ans[:3] == b"RQS":
                    logging.debug(f"{self.client[0]}: Sending Session List")
                    sess = [i.client[0] if i.client else None for i in sessions]
                    sess = set(sess)
                    sess = sess - {None}
                    sess = list(sess)
                    sess.remove(self.client[0])
                    self.socket.sendto(b"SES" + dat_to_bytes(sess), self.client)

                elif ans[:3] == b"SES":
                    sess = [i.client[0] if i.client else None for i in sessions]
                    sess = set(sess)
                    sess = sess - {None}
                    logging.debug(
                        f"{self.client[0]}: My sessions: {sess} Recieved: {set(bytes_to_dat(ans[3:]))} New: {list(set(bytes_to_dat(ans[3:]))-sess)}"
                    )
                    uncon = list(set(bytes_to_dat(ans[3:])) - sess)
                    if not uncon:
                        continue
                    adr = random.choice(uncon)
                    s = Session()
                    sessions.append(s)
                    self.socket.sendto(
                        b"HOP"
                        + socket.inet_aton(adr)
                        + b"CON"
                        + s.public_ip.encode("cp866")
                        + b":"
                        + str(s.public_port).encode("cp866"),
                        self.client,
                    )
                # ----------------------------------------HOP Tracking-------------------------------------
                elif ans[:3] == b"HOP":
                    sess = [i.client[0] if i.client else None for i in sessions]

                    ip = socket.inet_ntoa(ans[3:7])
                    if ip in sess:
                        s = sessions[sess.index(ip)]
                        s.socket.sendto(ans[7:], s.client)

                elif ans[:3] == b"CON":
                    s = Session()
                    adr, prt = ans[3:].decode("cp866").split(":")
                    self.socket.sendto(
                        b"HOP"
                        + socket.inet_aton(adr)
                        + b"RDY"
                        + prt.encode("cp866")
                        + b":"
                        + s.public_ip.encode("cp866")
                        + b":"
                        + str(s.public_port).encode("cp866"),
                        self.client,
                    )
                    try:
                        s.make_connection(adr, int(prt))
                        s.backlife_cycle(1)
                        sessions.append(s)
                    except:
                        logging.error(f"{self.client[0]}: Connect initiation timeout!")

                elif ans[:3] == b"RDY":
                    myprt, adr, prt = ans[3:].decode("cp866").split(":")
                    sess = [i.public_port for i in sessions]

                    if int(myprt) in sess:
                        s = sessions[sess.index(int(myprt))]
                        try:
                            s.make_connection(adr, int(prt))
                            s.backlife_cycle(1)
                        except:
                            logging.error(
                                f"{self.client[0]}: Connect stabilization timeout!"
                            )
                            sessions.remove(s)

                # ----------------------------------------Disabled Trash-----------------------------------
                elif ans[:3] == b"TRK":
                    adr, prt = ans[3:].decode("cp866").split(",")
                    sess = [i.client[0] for i in sessions]
                    sess.remove(self.client[0])
                    s = sessions[sess.index(adr)]

                    s.socket.sendto(
                        b"CN0"
                        + f"{self.client[0].encode('cp866')}:{prt.encode('cp866')}",
                        s.client,
                    )

                elif ans[:3] == b"CN0":
                    s = Session()
                    self.socket.sendto(
                        b"CN1"
                        + f"{s.public_ip.encode('cp866')}:{str(s.public_port).encode('cp866')}",
                        self.client,
                    )
                    adr, prt = ans[3:].decode("cp866").split(":")
                    s.make_connection(adr, int(prt))
                    sessions.append(s)
                elif ans[:3] == b"TRK":
                    pass
                else:
                    logging.warning(f"{self.client[0]}: Malformed! !!!{ans}!!!")


# It is like a legacy code, bruh: (https://stackoverflow.com/questions/51903172/how-to-display-a-tree-in-python-similar-to-msdos-tree-command)
def ptree(start, tree, indent_width=4):
    def _ptree(start, parent, tree, grandpa=None, indent=""):
        if parent != start:
            if grandpa is None:  # Ask grandpa kids!
                print(parent, end="")
            else:
                print(parent)
        if parent not in tree:
            return 
        for child in tree[parent][:-1]:
            print(indent + "├" + "─" * indent_width, end="")
            _ptree(start, child, tree, parent, indent + "│" + " " * 4)
        child = tree[parent][-1]
        print(indent + "└" + "─" * indent_width, end="")
        _ptree(start, child, tree, parent, indent + " " * 5)  # 4 -> 5

    parent = start
    print(start)
    _ptree(start, parent, tree)


def silent():
    logging.disable()


logging.warning(
    f"Logger for DEBUG is running! to disable it run {scriptname.split('.')[0]}.silent()"
)
print(
    f" Welcome to {scriptname} version from {verfrom} - event logging here: {scriptname}.log"
)
print(
    f"   Your Python version is {'.'.join([str(i) for i in sys.version_info[0:3]])}, branch {sys.version_info[3].upper()}"
)
try:
    c = STUN(12346)
    print(f"     Internet connection is stable on {socket.gethostname()}!")
    if 1:
        import requests

        r2 = requests.get(f"http://ipinfo.io/{c[0]}").json()["org"]
        print(
            f"       Gray  (local)  IP is {socket.gethostbyname(socket.gethostname())}"
        )
        print(f"       While (public) IP is {c[0]} - {r2}")
    else:
        print(
            f"       Gray  (local)  IP is {socket.gethostbyname(socket.gethostname())}"
        )
        print(f"       While (public) IP is {c[0]}")
except Exception as e:
    logging.critical(e)
    print(f" No internet connection found! I cant work offline!")


import re


def get_tree(data):
    data = data.copy()
    data.update({"00000000": "Root"})
    # data.update({"11111111":"Root"})
    data.update({"ffffffff": "Lost"})
    dct = {}

    for key, message in data.items():
        if key + ": " + message not in dct:
            dct.update({key + ": " + message: []})

    for key, message in data.items():
        rep = [i[1:] for i in re.findall("@+[a-z0-9]{8}", message)]

        if len(rep) > 0:
            rep = rep[0]
        else:
            rep = "00000000"

        if rep not in data:
            rep = "ffffffff"
        if rep + ": " + data[rep] in dct:
            dct[rep + ": " + data[rep]].append(key + ": " + message)
        else:
            pass
            # dct.update({rep+": "+data[rep]:[key+": "+message]})
    # print(dct)
    dct["00000000: Root"].remove("00000000: Root")
    for k, v in list(dct.items()).copy():
        if v == []:
            dct.pop(k)
    return dct


if __name__ == "__main__":
    data_load()
    print()
    inp = input(
        "You must to connect with one node (friend), which is already in net. (Press Enter when you and your friend are ready)"
    )
    s = Session()
    print()
    print(f"Send this to your friend {addr2int(s.public_ip,int(s.public_port))}")
    print()
    i, p = int2addr(int(input("Input the number from your friend: ")))
    print("Waiting for your friend")
    s.make_connection(i, p)
    sessions.append(s)
    s.backlife_cycle(1)
    while 1:
        print()
        print("╔════════════> Connect & Chan Panel <═════════════")
        print("╟> Type and enter your post")
        print("╟> (Empty input + Enter) to see Root")
        print("╟> ($00000000) to see specific thread")
        print("╟> (!) for new connection")
        print("╟> (#) to save checkpoint")
        print("╟> (`) dev console")
        print("╚══════════════════════════>")
        inp = input("Input: ")
        print("<════════════> Connect & Chan Info <════════════>")
        print(
            f" Connected Nodes: {len(sessions)} | Size of Chan tree: {len(dat_to_bytes(data))} bytes\n"
        )

        if inp == "":
            ptree("00000000: Root", get_tree(data))

        elif inp == "!":
            s = Session()
            print(
                f"Send this to your friend {addr2int(s.public_ip,int(s.public_port))}"
            )
            print()
            inp = input("Input the number from your friend (Empty to cancel): ")
            if inp:
                i, p = int2addr(int(inp))
                print("Waiting for your friend")
                try:
                    s.make_connection(i, p)
                    sessions.append(s)
                    s.backlife_cycle(1)
                except:
                    print("Timeout(")
        elif inp == "`":
            try:
                debug.shell()
            except:
                pass
        elif inp == "#":
            data_dump()
        elif inp[0] == "$":
            if inp[1:] in data:
                ptree(f"{inp[1:]}: {data[inp[1:]]}", get_tree(data))
            else:
                print(f"There is no message with id [{inp[1:]}]")
        elif inp:
            data_add(inp)
        else:
            ptree("00000000: Root", get_tree(data))
        input("\n\nEnter to reload page")
        cls()