<!-- SPDX-License-Identifier: GPL-2.0-or-later -->
# Car test: PCSX ReARMed under NBT Manager (first test, guest build)

Parked, ignition on. About 45 minutes. Keep SSH/ENET recovery at hand.

First run of this application in a car, and the first emulator built as a
**guest**: `nbt-runner` (built with the QNX 6.5 SP1 SDP) with PCSX ReARMed
appended, which it copies out and starts as its own process. PCSX ReARMed's
ARM recompiler writes and runs code at run time: whether the car's QNX allows
it is the main question, with the speed.

## What you need

- NBT Manager from test kit dev119 or later (it trusts the kit's `test-app`
  key and runs bridge 1.5 applications) and the phone app from the same kit,
  paired.
- `build/car-test/`: `pcsx-0.0.1.nbt`, `pcsx-0.0.2.nbt` and `SHA256SUMS.txt`.
  Copy both packages to the phone.
- A USB stick with PlayStation discs you own: one game as `.cue` + `.bin`
  (or `.chd`), and if you have one, a game on two discs with an `.m3u` list
  of its discs (one file name per line, e.g. `Game (Disc 1).cue`). Optional:
  your console's BIOS file (`scph1001.bin`, `scph5501.bin`, …) on the stick
  too, for part B.6.
- A USB gamepad (Xbox or DualShock 4 / DualSense), for part B.4.
- SSH to the head unit (logs, recovery).

## A. Install, health check, settings

1. On the phone: import `pcsx-0.0.1.nbt`, send it to the car, approve on the
   car. The manager runs its health check (about 10 s): install must succeed.
2. In the manager's menu, hold the push on **pcsx**: 10 settings (Aspect,
   Filter, Region, BIOS, Dynarec, GPU thread, Frame skip, Sound, Show FPS,
   Debug log). Set **Show FPS: on**.

## B. Discs, start and play

1. Plug in the USB stick. Hold the push on **pcsx** → **Files** → **Import
   from a USB stick**: the discs, tracks (`.bin`), lists and BIOS are listed;
   import all. Large `.bin` files take a while.
2. Select **pcsx**. Its game list shows the `.cue`/`.chd`/`.m3u` files only
   (no `.bin`). Without a BIOS file a notice says "No PlayStation BIOS file
   found": expected, the built-in replacement runs.
3. Start the single-disc game with the push. It must boot to its title
   screen and intro **with sound**. Note the FPS shown top right (60 for an
   NTSC game, 50 for PAL) during the intro and in play.
4. Controls with the iDrive controller: tilts are the D-pad, push Cross, BACK
   tap Circle, the knob L1/R1, MEDIA Select, OPTION Start, favourite keys 1–4
   Square, Triangle, L2, R2. Then plug the gamepad in: a notice names it, and
   every button sits where the PlayStation pad has it. Unplug it: the iDrive
   controller plays again.
5. Pause menu (MENU, or a BACK hold, or the pad's Xbox/PS button): **Save
   state**, play on a bit, **Load state**: back where saved. Save in the game
   itself (its memory card), **Quit**, start the game again: its save is
   there.
6. With a BIOS file imported: **Choose another game**, start the game again:
   no BIOS notice, and the application's log has `found … BIOS file`.
7. Two-disc game (`.m3u`): pause menu, a **Disc: 1 of 2** row after Slot;
   choose it: "Disc 2 of 2 inserted". Where the game asks for disc 2, it
   reads it.
8. Speed, if under full speed in B.3: try **GPU thread: on**, then **Frame
   skip: 1**, noting the FPS each time. Then **Dynarec: off** for one
   comparison (the interpreter: expect it much slower), and back **on**.

## C. Stop, start again, update

1. In the manager, hold the push on **pcsx**, then **Stop**: the screen
   returns to iDrive.
2. Start it again: the list focuses the last game played.
3. While a game runs, send `pcsx-0.0.2.nbt` from the phone and approve: the
   update stops the running copy, runs the health check and installs. Start
   it again: saves and states are still there.

## D. Over SSH (optional)

- `pidin arg | grep -e pcsx -e nbt-runner`: the application (`…/apps/pcsx/bin/app`,
  the runner) and its child, the guest.
- `kill <app pid>` (SIGTERM): a clean stop as in C.1; the guest goes too.
- `kill -9 <guest pid>`: the application ends ("guest killed by signal 9");
  the manager shows it stopped.

## Logs (before switching the car off: `/dev/shmem` is RAM)

- The application's log: the phone app, **pcsx** → log. With **Debug log:
  on**, it has the core's own messages. A crash shows as
  `runner: guest killed by signal N` with the faulting address in
  `sloginfo` (`Process … (nbt-pcsx.guest) terminated SIG…`): copy both
  lines. `SIGBUS` there would mean an unaligned access, `SIGSEGV`/`SIGILL`
  right after a game starts would point at the recompiler's memory.
- The manager: its debug log, with the debug log on.

## Back

Uninstall **pcsx** from the manager (hold → Uninstall, or from the phone).

## Report

| Step | Result | Notes |
| --- | --- | --- |
| A.1 install + health check | | |
| A.2 10 settings shown and kept | | |
| B.1 import from USB (time for the discs) | | |
| B.2 list: games only, BIOS notice | | |
| B.3 game boots, sound, FPS (intro / play) | | |
| B.4 iDrive controls; gamepad by position; unplug | | |
| B.5 states; in-game save kept after Quit | | |
| B.6 BIOS found | | |
| B.7 disc swap | | |
| B.8 FPS with GPU thread / Frame skip / Dynarec off | | |
| C.1 stop | | |
| C.2 start again, last game focused | | |
| C.3 update while running; saves kept | | |
| D clean stop, guest killed | | |

With the car's software version (Navigation → Settings → Position and
software version), the games used (and their region) and the pad model.
