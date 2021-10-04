import subprocess as sp
import time

class Terminal:
    def __init__(self, path):
        self.path = path
        self.term = None
        self.height = None
        self.width = None
        self.auto_flush = False
        self.open_term()
        self.read_term_size()
    def open_term(self):
        if self.term is not None:
            return False
        self.term = open(self.path, "wb")
        return True
    def close_term(self):
        if self.term is None:
            return False
        self.term.close()
        self.term = None
        return True
    def read_term_size(self):
        ret = sp.check_output(["stty", "size", "-F", self.path])
        ret = ret.decode()
        height, width = ret.strip().split(" ")
        self.height = int(height)
        self.width = int(width)
    def flush(self):
        self.term.flush()
    def write(self, in_bytes, flush=True):
        if self.term is None:
            return False
        if type(in_bytes) == str:
            in_bytes = in_bytes.encode("utf-8")
        self.term.write(in_bytes)
        if self.auto_flush:
            self.flush()
    def write_cs(self, in_cs):
        if type(in_cs) == str:
            in_cs = in_cs.encode("ascii")
        self.write(in_cs)
        if self.auto_flush:
            self.flush()
    def __enter__(self):
        self.open_term()
        return self
    def __exit__(self):
        self.close_term()
        return self
    def clear_screen(self):
        self.write_cs(b"\x1b[2J")
    def move_cursor(self, x=0, y=0):
        x += 1
        y += 1
        # Coordinates are 1 indexed in control sequences
        cs = "\x1b[{};{}H".format(y, x)
        self.write_cs(cs)
    def set_color(self, color=0):
        cs = "\x1b[38;5;{}m".format(color)
        self.write_cs(cs)
    def set_background(self, color=0):
        cs = "\x1b[48;5;{}m".format(color)
        self.write_cs(cs)
    def reset_color(self):
        self.write_cs(b"\x1b[39m")
    def reset_background(self):
        self.write_cs(b"\x1b[49m")
    def write_shade(self, strength=2):
        if strength < 1:
            strength = 1
        if strength > 3:
            strength = 3
        ch = chr(0x2590+strength)
        self.write(ch)
    def write_braille(self, i=0x99):
        if i < 0:
            i = 0
        if i > 255:
            i = 255
        ch = chr(0x2800+i)
        self.write(ch)

import math

class BrailleTest:
    def __init__(self, term):
        self.term = term
        self.width = term.width
        self.height = term.height
        self.ylimit = self.height * 4
        self.ys = [0] * (self.width * 2)
        self.color = [0] * self.width
        self.color_seq = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46, 47, 48, 49, 50, 51, 45, 39, 33, 27, 21, 57, 93, 129, 165, 201, 200, 199, 198, 197]
        self.color_phase = 0
        self.wave_period = 56.789
        self.wave_phase = 0
        self.wave_amplitude = 12.345
        self.wave_offset = 0
    def update_frame(self):
        for ci in range(len(self.color)):
            self.color[ci] = self.color_seq[(self.color_phase + ci) % len(self.color_seq)]
        self.color_phase += 1
        self.color_phase %= len(self.color_seq)
        wave_center = int(self.ylimit / 2)
        for yi in range(len(self.ys)):
            self.ys[yi] = math.sin((yi + self.wave_phase % self.wave_period) / self.wave_period * 2 * math.pi) * self.wave_amplitude + (self.wave_offset + wave_center)
            self.ys[yi] = int(self.ys[yi])
        self.wave_phase += 1
        self.wave_phase %= self.wave_period
    def get_buf(self):
        buf = bytearray()
        # Clear screen
        buf += b"\x1b[2J"
        # Move cursor to top
        buf += b"\x1b[1;1H"
        for y in range(self.height):
            for x in range(self.width):
                color = "\x1b[38;5;{}m".format(self.color[x])
                color = color.encode()
                buf += color
                br_odd = self.ys[2*x]
                br_odd -= (self.height - y) * 4
                br_odd = max(0, br_odd)
                br_odd = min(br_odd, 4)
                
                br_even = self.ys[2*x+1]
                br_even -= (self.height - y) * 4
                br_even = max(0, br_even)
                br_even = min(br_even, 4)

                # 1 8
                # 2 16
                # 4 32
                # 64 128
                ch = 0
                if br_odd >= 1:
                    ch |= 64
                if br_odd >= 2:
                    ch |= 4
                if br_odd >= 3:
                    ch |= 2
                if br_odd == 4:
                    ch |= 1
                if br_even >= 1:
                    ch |= 128
                if br_even >= 2:
                    ch |= 32
                if br_even >= 3:
                    ch |= 16
                if br_even == 4:
                    ch |= 8
                
                ch = chr(0x2800+ch)
                ch = ch.encode("utf-8")
                buf += ch
        return bytes(buf)

def test():
    term = Terminal("/dev/pts/0")
    print("WIDTH",term.width)
    print("HEIGHT",term.height)
    for w in range(0, term.width, 10):
        term.move_cursor(w, 0)
        term.write(str(w))
    for h in range(0, term.height):
        term.move_cursor(0, h)
        term.write(str(h))
    time.sleep(1)
    term.move_cursor(1, 1)
    [(term.set_color(i), term.write_shade(3)) for i in range(256)]
    term.reset_color()
    term.move_cursor(1, 3)
    [(term.set_background(i), term.write_shade(1)) for i in range(256)]
    term.reset_background()
    term.move_cursor(1, 5)
    [(term.write_braille(i)) for i in range(256)]
    time.sleep(4)
    term.clear_screen()
    term.move_cursor(0, 0)

def btest():
    term = Terminal("/dev/pts/0")
    bt = BrailleTest(term)
    while True:
        bt.update_frame()
        term.write(bt.get_buf())
        term.flush()

if __name__ == "__main__":
    btest()