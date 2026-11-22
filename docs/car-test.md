<!-- SPDX-License-Identifier: GPL-2.0-or-later -->
# Car test: PCSX ReARMed before a release

Parked, ignition on. About 45 minutes, all from the phone: no adapter, no
computer.

Run it on a candidate before tagging a release, and whenever the car-side
behaviour changed. PCSX ReARMed is a **guest**: the `nbt-runner` NBT Manager
ships copies it out and starts it as its own process, executes its GL command
stream on the GPU and plays its sound from a shared ring. Its ARM recompiler
writes and runs code at run time. There is no sound at the game list itself:
sound starts with a game.

## What you need

- NBT Manager 0.3.1 or later on the car, and its phone app, paired.
- From the kit folder: the candidate `pcsx-<version>.nbt`, a second one with a
  higher sequence for part C, and their `SHA256SUMS` file. Copy them to the
  phone.
- A USB stick with PlayStation discs you own: one game as `.cue` + `.bin`
  (or `.chd`), and if you have one, a game on two discs with an `.m3u` list
  of its discs (one file name per line, e.g. `Game (Disc 1).cue`). Optional:
  your console's BIOS file (`scph1001.bin`, `scph5501.bin`, …) on the stick
  too, for part B.6.
- A USB gamepad (Xbox or DualShock 4 / DualSense), for part B.4.

## A. Install, health check, settings

1. In the phone app's library, add the candidate and open it. Under the file
   name: **PCSX ReARMed** (version and commit), **Project: PCSX ReARMed
   (https://github.com/notaz/pcsx_rearmed)**, **Licence: GPL-2.0-or-later**,
   then the text, ending with the repository's address.
2. Send it to the car (an install, or an update of **pcsx**) and approve on
   the car. The manager runs its health check (about 10 s): it must succeed.
3. In the manager's menu, hold the push on **pcsx**: 10 settings (Aspect,
   Filter, Region, BIOS, Dynarec, GPU thread, Frame skip, Sound, Show FPS,
   Debug log). Set **Show FPS: on** and **Debug log: on**.

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
3. While a game runs, send the second package from the phone and approve: the
   update stops the running copy, runs the health check and installs. Start
   it again: saves and states are still there.

## Logs (before switching the car off: `/dev/shmem` is RAM)

- The application's log: the phone app, **pcsx** → log. With **Debug log:
  on**, it has the core's own messages. `runner: 1 frames presented` means
  the first frame reached the screen (a count follows every minute and at the
  end); `runner: GL error 0x…` names the first GL error. A crash shows as
  `runner: guest killed by signal N` with the faulting address in
  `sloginfo` (`Process … (nbt-pcsx.guest) terminated SIG…`): copy both
  lines. `SIGBUS` there would mean an unaligned access, `SIGSEGV`/`SIGILL`
  right after a game starts would point at the recompiler's memory.
- For more, the phone's **Collect everything** (Install NBT Manager on a car ›
  More tools, over the Wi-Fi ENET adapter): the manager's and iDrive's logs.

## Back

Uninstall **pcsx** from the manager (hold → Uninstall, or from the phone), or
install the last release from GitHub (a test package with a lower sequence is
refused).

## Report

| Step | Result | Notes |
| --- | --- | --- |
| A.1 information shown | | |
| A.2 install or update + health check | | |
| A.3 10 settings shown and kept | | |
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

With the car's software version (Navigation → Settings → Position and
software version), the games used (and their region) and the pad model.
