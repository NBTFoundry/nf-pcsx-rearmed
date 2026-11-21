# SPDX-License-Identifier: GPL-2.0-or-later
"""PCSX ReARMed on the libretro host, under Xvfb, with a small PlayStation
program made here, as a PS-EXE and on ISO 9660 discs (no game or BIOS is
shipped): the game list, the program running, save states, the region
setting, a disc swap and --game; and the signed package's declaration."""

import os
from pathlib import Path
import re
import select
import shutil
import signal
import socket
import struct
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = Path(os.environ.get("NBT_PCSX_APP", ROOT / "build/nbt-pcsx-host"))
MGR_DIR = Path(os.environ.get("NBT_MGR_DIR", ROOT.parent / "manager"))

SOUTH, VIEW, MENU, DOWN = 1 << 0, 1 << 6, 1 << 7, 1 << 12
XBOX = 1

# What the program computes into RAM at 0x80100000: the complement of these
# words, so the bytes are nowhere in the program itself.
MARKER = b"NBT PCSX RUNS OK"


def mips_program() -> bytes:
    """MIPS R3000 code: turns the display on, fills the screen blue, writes
    the complement of MARKER to RAM, then loops."""
    T0, T1, T2, T3 = 8, 9, 10, 11
    code = []

    def li(reg, value):
        code.append(0x3C000000 | reg << 16 | value >> 16)  # lui
        code.append(0x34000000 | reg << 21 | reg << 16 | value & 0xFFFF)  # ori

    def sw(reg, offset, base):
        code.append(0xAC000000 | base << 21 | reg << 16 | offset)

    li(T0, 0x1F800000)  # I/O ports
    for command in (0x00000000, 0x03000000, 0x08000001, 0x05000000, 0x06C60260, 0x07042018):
        li(T1, command)  # GP1: reset, display on, 320x240, area, ranges
        sw(T1, 0x1814, T0)
    for command in (0xE3000000, 0xE403BD3F, 0xE5000000, 0x02FF0000, 0x00000000, 0x00F00140):
        li(T1, command)  # GP0: drawing area, offset, fill 320x240 blue
        sw(T1, 0x1810, T0)
    li(T3, 0x80100000)
    for i, (word,) in enumerate(struct.iter_unpack("<I", MARKER)):
        li(T1, word)
        code.append(T1 << 21 | T2 << 11 | 0x27)  # nor t2, t1, zero
        sw(T2, 4 * i, T3)
    code += [0x1000FFFF, 0]  # b . ; nop
    return struct.pack(f"<{len(code)}I", *code)


def ps_exe() -> bytes:
    """A PS-EXE: a 2 KiB header, then the program loaded at 0x80010000."""
    text = mips_program()
    text += bytes(-len(text) % 2048)
    header = bytearray(2048)
    header[0:8] = b"PS-X EXE"
    struct.pack_into("<IIII", header, 0x10, 0x80010000, 0, 0x80010000, len(text))
    struct.pack_into("<II", header, 0x30, 0x801FFFF0, 0)
    region = b"Sony Computer Entertainment Inc. for North America area"
    header[0x4C : 0x4C + len(region)] = region
    return bytes(header) + text


def both16(value: int) -> bytes:
    return struct.pack("<H", value) + struct.pack(">H", value)


def both32(value: int) -> bytes:
    return struct.pack("<I", value) + struct.pack(">I", value)


def directory_record(name: bytes, sector: int, size: int, is_dir: bool) -> bytes:
    record = (bytes([0, 0]) + both32(sector) + both32(size) + bytes(7) + bytes([2 if is_dir else 0, 0, 0])
              + both16(1) + bytes([len(name)]) + name)
    record += bytes(len(record) % 2)
    return bytes([len(record)]) + record[1:]


def iso_disc(label: str) -> bytes:
    """A 2048-byte-sector ISO 9660 image the HLE BIOS boots: SYSTEM.CNF names
    PSX.EXE, the program above."""
    exe = ps_exe()
    cnf = b"BOOT = cdrom:\\PSX.EXE;1\r\nTCB = 4\r\nEVENT = 10\r\nSTACK = 801FFFF0\r\n"
    root, cnf_at, exe_at = 20, 21, 22
    total = exe_at + len(exe) // 2048
    files = (directory_record(b"\0", root, 2048, True) + directory_record(b"\1", root, 2048, True)
             + directory_record(b"PSX.EXE;1", exe_at, len(exe), False)
             + directory_record(b"SYSTEM.CNF;1", cnf_at, len(cnf), False))
    pvd = bytearray(2048)
    pvd[0:7] = b"\x01CD001\x01"
    pvd[8:40] = b"PLAYSTATION".ljust(32)
    pvd[40:72] = label.encode().ljust(32)
    pvd[80:88] = both32(total)
    pvd[120:124] = both16(1)
    pvd[124:128] = both16(1)
    pvd[128:132] = both16(2048)
    pvd[132:140] = both32(10)
    pvd[140:144] = struct.pack("<I", 18)
    pvd[148:152] = struct.pack(">I", 19)
    pvd[156:190] = directory_record(b"\0", root, 2048, True)
    path_table = bytes([1, 0]) + struct.pack("<IH", root, 1) + bytes(2)
    sectors = [bytes(2048)] * 16 + [bytes(pvd), b"\xffCD001\x01".ljust(2048, b"\0"),
                                     path_table.ljust(2048, b"\0"),
                                     (bytes([1, 0]) + struct.pack(">IH", root, 1) + bytes(2)).ljust(2048, b"\0"),
                                     files.ljust(2048, b"\0"), cnf.ljust(2048, b"\0")]
    image = b"".join(sectors) + exe
    assert len(image) == total * 2048
    return image


def complement(data: bytes) -> bytes:
    return bytes(b ^ 0xFF for b in data)


def xvfb():
    r, w = os.pipe()
    proc = subprocess.Popen(
        ["Xvfb", "-displayfd", str(w), "-screen", "0", "1280x480x24", "-nolisten", "tcp"],
        pass_fds=(w,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(w)
    number = b""
    while not number.endswith(b"\n"):
        ready, _, _ = select.select([r], [], [], 10)
        chunk = os.read(r, 1) if ready else b""
        if not chunk:
            break
        number += chunk
    os.close(r)
    return proc, ":" + number.decode().strip()


class App:
    """The emulator, its log (standard error) read by line."""

    def __init__(self, env, pass_fds, args=()):
        full = {k: v for k, v in os.environ.items() if not k.startswith("NBT_")}
        full.update(env)
        self.proc = subprocess.Popen([str(APP), *args], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.PIPE, env=full, pass_fds=pass_fds)
        self.lines, self.buf = [], b""

    def wait(self, pattern, timeout=30.0):
        regex, deadline = re.compile(pattern), time.monotonic() + timeout
        while True:
            while b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                self.lines.append(raw.decode(errors="replace"))
            for i, line in enumerate(self.lines):
                if regex.search(line):
                    del self.lines[: i + 1]
                    return line
            fd = self.proc.stderr.fileno()
            left = deadline - time.monotonic()
            ready, _, _ = select.select([fd], [], [], max(0.0, left)) if left > 0 else ([], [], [])
            chunk = os.read(fd, 4096) if ready else b""
            if not chunk:
                raise AssertionError(f"no line matching {pattern!r}; saw {self.lines[-20:]!r}")
            self.buf += chunk

    def stop(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)
        _, err = self.proc.communicate(timeout=30)
        self.buf += err
        return self.proc.returncode


@unittest.skipUnless(os.access(APP, os.X_OK), f"{APP} not built")
@unittest.skipUnless(shutil.which("Xvfb"), "Xvfb not installed")
class PlayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="nbt-pcsx-"))
        self.files, self.data = self.tmp / "files", self.tmp / "data"
        self.files.mkdir(mode=0o700)
        self.data.mkdir(mode=0o700)
        (self.files / "notes.txt").write_bytes(b"not a game")
        self.x, self.display = xvfb()
        self.pad_app, self.pad = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.seq = 0

    def tearDown(self):
        self.pad_app.close()
        self.pad.close()
        self.x.terminate()
        self.x.wait(timeout=5)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def start(self, *args, **settings):
        env = {
            "NBT_LAUNCH": "user", "DISPLAY": self.display, "LIBGL_ALWAYS_SOFTWARE": "1",
            "NBT_NO_AUDIO": "1", "NBT_FILES_DIR": str(self.files), "NBT_DATA_DIR": str(self.data),
            "NBT_BRIDGE_CAPS": "gamepad", "NBT_GAMEPAD_FD": str(self.pad_app.fileno()),
        }
        env.update({"NBT_SETTING_" + k.upper(): v for k, v in settings.items()})
        app = App(env, (self.pad_app.fileno(),), args)
        self.addCleanup(lambda: app.proc.poll() is None and app.proc.kill())
        app.wait(r"core PCSX-ReARMed ")
        return app

    def press(self, buttons=0, hold=0.15):
        self.seq += 1
        self.pad.send(struct.pack("<BBBBIIhhhhHH", 1, 1, 1, XBOX, self.seq, buttons, 0, 0, 0, 0, 0, 0))
        time.sleep(hold)

    def tap(self, buttons):
        self.press(buttons)
        self.press(0)

    def menu(self, downs):
        """The pause menu (View + Menu), `downs` items down, chosen."""
        self.tap(VIEW | MENU)
        for _ in range(downs):
            self.tap(DOWN)
        self.tap(SOUTH)

    def play(self, seconds):
        """Lets the game run, the pad idle but plugged in."""
        for _ in range(int(seconds / 0.15)):
            self.press(0)

    def test_a_disc_runs_and_a_state_is_saved_and_loaded(self):
        (self.files / "Test.iso").write_bytes(iso_disc("TEST"))
        (self.files / "track.bin").write_bytes(bytes(2352))  # a track or BIOS: not offered
        app = self.start()
        self.press(0)
        self.tap(SOUTH)  # the only game
        app.wait(r"game Test\.iso: \d+x\d+, (59|60)\.\d+ fps")
        self.play(1.5)
        self.menu(1)  # Save state
        app.wait(r"State saved in slot 1")
        state = (self.data / "states" / "Test.iso.state1").read_bytes()
        self.assertGreater(len(state), 2 * 1024 * 1024)  # the RAM is in it
        self.assertIn(complement(MARKER), state)  # the program ran from the disc
        self.menu(2)  # Load state
        app.wait(r"State of slot 1 loaded")
        self.assertEqual(app.stop(), 0)
        self.assertEqual((self.data / "last-game").read_bytes(), b"Test.iso")

    def test_a_ps_exe_runs(self):
        (self.files / "Test.exe").write_bytes(ps_exe())
        app = self.start("--game", "Test.exe")
        app.wait(r"game Test\.exe: ")
        self.play(1.5)
        self.menu(1)
        app.wait(r"State saved in slot 1")
        self.assertIn(complement(MARKER), (self.data / "states" / "Test.exe.state1").read_bytes())
        self.assertEqual(app.stop(), 0)

    def test_the_region_setting_reaches_the_core(self):
        (self.files / "Test.iso").write_bytes(iso_disc("TEST"))
        app = self.start("--game", "Test.iso", region="pal")
        app.wait(r"game Test\.iso: \d+x\d+, (49|50)\.\d+ fps")
        self.assertEqual(app.stop(), 0)

    def test_discs_of_a_list_are_swapped_from_the_pause_menu(self):
        (self.files / "Two (Disc 1).iso").write_bytes(iso_disc("DISC1"))
        (self.files / "Two (Disc 2).iso").write_bytes(iso_disc("DISC2"))
        (self.files / "Two.m3u").write_text("Two (Disc 1).iso\nTwo (Disc 2).iso\n")
        app = self.start("--game", "Two.m3u")
        app.wait(r"game Two\.m3u: ")
        self.play(0.5)
        self.menu(4)  # Resume, Save, Load, Slot, then the disc
        app.wait(r"Disc 2 of 2 inserted")
        self.play(0.5)
        self.assertEqual(app.stop(), 0)


class PackageTest(unittest.TestCase):
    def test_the_package_declares_files_and_its_settings(self):
        verify = MGR_DIR / "build" / "nbt-verify"
        if not (MGR_DIR / "tools/package.py").exists() or not verify.exists():
            self.skipTest("the manager's tools/package.py or build/nbt-verify is missing")
        if not shutil.which("openssl"):
            self.skipTest("openssl is missing")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            key, public = tmp / "app.key", tmp / "app.pub"
            subprocess.run(["openssl", "genrsa", "-out", key, "3072"], check=True, capture_output=True)
            subprocess.run(["openssl", "rsa", "-in", key, "-pubout", "-out", public], check=True,
                           capture_output=True)
            # A stand-in for the guest: ARM ET_EXEC with the SDK's NBT ABI note.
            binary = tmp / "stand-in.guest"
            note = struct.pack("<III", 4, 12, 1) + b"NBT\0" + struct.pack("<III", 1, 1, 2)
            elf = bytearray(52)
            elf[:7] = b"\x7fELF\x01\x01\x01"
            struct.pack_into("<HHI", elf, 16, 2, 40, 1)
            struct.pack_into("<I", elf, 28, 52)
            struct.pack_into("<HHH", elf, 40, 52, 32, 1)
            phdr = struct.pack("<IIIIIIII", 4, 84, 0, 0, len(note), len(note), 4, 4)
            binary.write_bytes(bytes(elf) + phdr + note)
            subprocess.run(["make", "-s", "-C", str(ROOT), "package", f"BUILD_DIR={tmp}",
                            f"PACKAGE_INPUT={binary}", f"APP_KEY={key}", f"NBT_MGR_DIR={MGR_DIR}",
                            "APP_VERSION=0.0.1"], check=True, capture_output=True)
            package = tmp / "pcsx-0.0.1.nbt"
            out = subprocess.run([str(verify), str(package), str(public), "pcsx", "nbt_6.5_armv7"],
                                 check=True, capture_output=True, text=True).stdout
            self.assertIn("app=pcsx\n", out)
            self.assertIn("bridge=1.7\n", out)
            self.assertIn("bridge-uses=show,controller,files,runner\n", out)
            self.assertIn("bridge-optional=status,live-settings,gamepad\n", out)
            raw = package.read_bytes()
            manifest = raw[24 : 24 + int.from_bytes(raw[8:12], "big")].decode("ascii")
            self.assertIn("bridge-files=cue,bin,img,iso,chd,pbp,m3u,mdf,mds,ccd,sub,sbi,toc,cbn,exe"
                          "|2048|16384|folders=m3u,cue,ccd,mds,toc\n", manifest)
            for setting in ("region|Region|auto|auto,ntsc,pal", "bios|BIOS|auto|auto,hle",
                            "dynarec|Dynarec|on|on,off", "frameskip|Frame skip|off|off,1,2"):
                self.assertIn(f"setting={setting}\n", manifest)


if __name__ == "__main__":
    unittest.main()
