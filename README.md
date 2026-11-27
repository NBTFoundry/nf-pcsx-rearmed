<!-- SPDX-License-Identifier: GPL-2.0-or-later -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img src="docs/assets/logo-light.svg" alt="NBTFoundry" height="44">
  </picture>
</p>

<h1 align="center">PCSX ReARMed for NBT Manager</h1>

> **Warning: installing or modifying this software can brick your head unit. Recovery may require professional service or replacement, at your expense. Provided AS IS; use at your own risk, subject to applicable law.** [Read the risk and liability disclaimer](DISCLAIMER.md).

<p align="center">
  <b>PlayStation games on the iDrive screen,</b><br>
  played with a USB gamepad laid out like the original pad, or the iDrive controller.
</p>

PCSX ReARMed's libretro core on the NBT App SDK's libretro host, with its ARM
dynamic recompiler: the frame scaled to the car's panel, sound through the
car's speakers, a memory card, save states, disc swaps and a pause menu. Discs
come from a USB stick, copied to the head unit's hard disk. Installed and
launched through NBT Manager.

**Supported head units:** BMW NBT Evo (iDrive 6). Support for the earlier NBT
may come later.

Part of [NBTFoundry](https://github.com/NBTFoundry):
[manager](https://github.com/NBTFoundry/manager) ·
[sdk](https://github.com/NBTFoundry/sdk) ·
[mobile-app](https://github.com/NBTFoundry/mobile-app) ·
[installer](https://github.com/NBTFoundry/installer) ·
[toolchains](https://github.com/NBTFoundry/toolchains)

Not affiliated with or endorsed by BMW AG or Sony Interactive Entertainment.
BMW, iDrive and NBT are trademarks of BMW AG; PlayStation is a trademark of
Sony Interactive Entertainment Inc. No game and no BIOS is included: use only
games and BIOS files you own.

## Status

Built and tested on the desktop and in the SDK's VM under QEMU; not yet tested
in a car.

## Adding games

PCSX ReARMed plays disc images: `.cue` with its `.bin` tracks, `.chd`, `.pbp`,
`.iso`, `.img` (with `.ccd`, `.sub`), `.mdf` (with `.mds`), `.toc`, `.cbn`,
and PS-EXE programs (`.exe`); `.sbi` files next to a disc carry its
subchannel data. A game on several discs is an `.m3u` list of their files, one
per line. Files of up to 2 GiB each, 16 GiB in all (NBT Manager's `files`
capability).

- **From a USB stick** (discs are too big for the phone, which sends at most
  64 MiB): on the car, hold the push on PCSX ReARMed in NBT Manager, then
  **Files** › **Import from a USB stick**. One game is a folder or an archive:
  - a **folder** holding a game's files with its `.cue` sheet (or `.m3u`
    list, `.ccd`, `.mds`, `.toc`): `Tekken 3/` with `Tekken 3.cue` and its
    `.bin` tracks is listed as one entry, `Tekken 3/`, and copied whole;
  - a **`.zip` archive** holding them is listed as `<archive name>/` and
    unpacked into a folder of that name on the car (the head unit's disk has
    the room; the stick is only read);
  - single-file games (`.chd`, `.pbp`, `.iso`) are listed one by one, in a
    folder or a zip too, as are BIOS files.
  Choose one entry or **Import all**. On the car the Files page lists a game
  folder as one entry; deleting it deletes the whole game.
- **From the phone:** small files only (an `.m3u`, an `.sbi`, a BIOS file):
  the NBT Manager app, the car, PCSX ReARMed, **Files**, **Add files**.

The game list shows one entry per game: a file that starts a game, or a game
folder, which starts at its `.m3u` list, else its `.cue` sheet (or `.ccd`,
`.mds`, `.toc`, `.cbn`), else its single image (`.chd`, `.pbp`, `.iso`,
`.img`), else its first `.bin`. Tracks, subchannel data and BIOS files are used
but not listed.

### Compressed images (CHD and PBP)

PCSX ReARMed reads two compressed formats itself, one file per disc, about
half the size of a `.cue` and its tracks, with nothing to unpack:

- **CHD** (MAME's compressed hunks), from a `.cue` or an `.iso` with MAME's
  `chdman` (in the `mame-tools` package on Debian and Ubuntu, `mame` on
  Homebrew, or `chdman.exe` from mamedev.org on Windows):
  ```sh
  chdman createcd -i "Tekken 3 (USA).cue" -o "Tekken 3 (USA).chd"
  ```
  A folder of them in one go (bash): `for c in *.cue; do chdman createcd -i
  "$c" -o "${c%.cue}.chd"; done`. A game on several discs gets one `.chd` per
  disc and an `.m3u` naming them, one per line.
- **PBP** (the PSP's EBOOT format), from tools such as PSX2PSP or `popstationr`;
  several discs fit in one `.pbp`.

Copy the `.chd` or `.pbp` files to the stick, loose or in a folder: each is
one game.

**BIOS:** without one, PCSX ReARMed uses its own replacement (HLE), which runs
most games. For better compatibility, add a BIOS dump of your console with the
games, named as PCSX ReARMed looks for it: `scph5500.bin`, `scph5501.bin`,
`scph5502.bin` (Japan, America, Europe), `scph1001.bin`, `scph7001.bin`,
`scph101.bin` or `psxonpsp660.bin`.

## Playing

PCSX ReARMed opens on its game list, the last game played focused. In a game,
the pause menu has Resume, Save state, Load state, the slot (1 to 4), the disc
(for a game on several discs: choosing it puts in the next one), Reset, Choose
another game and Quit. Memory card 1 is saved when it changes (at most every
10 seconds) and on leaving; it and the states stay in PCSX ReARMed's data
folder across updates.

## Controls

Bindings are chosen for the pad plugged in, by its family; there is nothing to
set. Each button is where the PlayStation pad has it, so a game plays as on
the original: the bottom button is Cross, the right one Circle.

| PlayStation | Xbox | DualShock 4 / DualSense | iDrive controller | Desktop |
| --- | --- | --- | --- | --- |
| D-pad | D-pad or left stick | D-pad or left stick | Tilt | Arrows |
| Cross | A | Cross | Push | Z |
| Circle | B | Circle | BACK, tap | X |
| Square | X | Square | Favourite key 1 | A |
| Triangle | Y | Triangle | Favourite key 2 | S |
| L1 / R1 | LB / RB | L1 / R1 | Turn the knob left / right | Q / W |
| L2 / R2 | LT / RT | L2 / R2 | Favourite keys 3 / 4 | E / R |
| L3 / R3 | Stick clicks | Stick clicks | — | — |
| Select | View | Share / Create | MEDIA | Right Shift |
| Start | Menu | Options | OPTION | Return |
| Pause menu | Xbox button, or View + Menu | PS button, or Share / Create + Options | MENU, or BACK held | Escape |
| Quit | from the menu | from the menu | BACK, long hold | from the menu |

The pad is the digital one: the left stick works as the D-pad. In the menus
the D-pad, left stick, knob or tilts move, the bottom button (push) chooses
and the right button (BACK) goes back; LB and RB (L1, R1) jump ten games. The
menus name the buttons of the pad in use, and a notice says when a pad is
plugged in or removed: the iDrive controller then plays. The knob holds L1 or
R1 for 150 ms per detent. Which pads are supported is up to NBT Manager
(`NBTFoundry/manager: docs/gamepad-bridge.md`).

## Settings

Changed from the phone app or NBT Manager's settings page; they apply at once.

| Setting | Choices | Default |
| --- | --- | --- |
| Aspect | 4-3 (the TV's shape), pixel (whole multiples), full | 4-3 |
| Filter | sharp (crisp pixels, smoothed edges), smooth, nearest | sharp |
| Region | auto, ntsc (60 Hz), pal (50 Hz) | auto |
| BIOS | auto (a BIOS file when there is one), hle (PCSX ReARMed's own) | auto |
| Dynarec | on (the ARM recompiler), off (the interpreter, slow) | on |
| GPU thread | auto, on, off: drawing on the second core | auto |
| Frame skip | off, 1, 2 (frames not drawn between two drawn) | off |
| Sound | on, off | on |
| Show FPS | off, on | off |
| Debug log | off, on | off |

## Bridge

The package carries the guest (built with the NBT toolchain, run by NBT
Manager's `nbt-runner`) and declares bridge 1.7: `show`, `controller`, `files`
and `runner` required, `status`, `live-settings` and `gamepad` optional, and
the files policy
`cue,bin,img,iso,chd,pbp,m3u,mdf,mds,ccd,sub,sbi,toc,cbn,exe|2048|16384|folders=m3u,cue,ccd,mds,toc`
(a folder or archive with one of those is one game, imported whole). It also
carries what the phone app shows before an install (the PCSX ReARMed version,
the project, the licence, notices), so it needs NBT Manager 0.3.1 or later.
PCSX ReARMed reports the game played as its status. NBT Manager keeps its
standard error as its log (shown, shared and cleared from the phone app); the
Debug log setting adds tracing and the core's debug messages.

## Build

Needs the NBT App SDK next to this repository (`../sdk`, or `NBT_SDK_DIR`),
gcc, Python 3, and the X11, EGL and GLESv2 development files; Xvfb for
the tests. `git submodule update --init` fetches PCSX ReARMed (not its own
`libpicofe` submodule, which the libretro core does not use).

```sh
make -j"$(nproc)" host test test-asan check-static-init   # host binary and tests
./build/nbt-pcsx-host                                     # play on the desktop (X11)
```

The desktop build lists the games in `NBT_FILES_DIR` and keeps saves in
`NBT_DATA_DIR` (the current folder without it):
`NBT_FILES_DIR=~/psx NBT_DATA_DIR=/tmp/pcsx ./build/nbt-pcsx-host`, or
`--game <file>` to start one directly. It runs the interpreter. The tests make
their own PlayStation program, as a PS-EXE and on ISO 9660 discs; no game or
BIOS is needed.

Head unit: PCSX ReARMed is GPL, so the application is a **guest**
(`sdk/docs/native-apps.md`): built with the NBT toolchain and run as its own
process by the `nbt-runner` NBT Manager ships (bridge 1.7, `runner`).

```sh
make -j"$(nproc)" guest                                  # build/nbt-pcsx.guest
make APP_KEY=/path/to/apps-signing-key.pem package       # build/pcsx-<version>.nbt
make vm-test                                             # the SDK's VM under QEMU
```

`package` signs the guest with NBT Manager's packer
(`../manager/tools/package.py`, or `NBT_MGR_DIR`), described by
`release/package.args`; `make package-args` writes the PCSX ReARMed version the
pin builds, and `make test` fails when it lags. `vm-test` runs it in the SDK's
VM, with the SDK's own `nbt-runner` (`sdk/docs/native-apps.md`, "Testing without
a head unit", says what building it takes). `make notice` writes
`legal/NOTICE.txt`.

### PCSX ReARMed on the NBT toolchain

Upstream's own `Makefile.libretro` builds the core, unchanged, as a static
library: in a copy of the submodule per build kind under `build/core/`
(upstream writes its objects next to its sources and sets flags per object),
with the ARM dynarec (`ari64`) in ARM state, the `gpu_unai` software renderer,
no NEON, no physical CD-ROM and no `dlopen`. The guest needs from the stack:
anonymous and executable memory for the recompiler (`mmap`, `mprotect`,
`__clear_cache`), thread scheduling attributes and `getauxval` (NBT toolchain
1.1.0 and the SDK's module runtime).

Two upstream changes, on the `clang-asm` branch of the
[NBTFoundry fork](https://github.com/NBTFoundry/pcsx_rearmed) (from `r26l`)
until upstream takes them:

- `plugins/dfsound/arm_utils.S`: the divided-syntax `ldmeqfd`, which Clang's
  assembler rejects, written `ldmfdeq`;
- the recompiler's assembly `get_reg` loads unaligned words; without
  unaligned access (`__ARM_FEATURE_UNALIGNED`), the C version is used. The
  SDK's VM faults on unaligned accesses.

## Releases

`.github/workflows/ci.yml` runs the host tests, the same under ASan/UBSan and
the guest build on every push and pull request. A `vX.Y.Z` tag runs
`.github/workflows/release.yml`: NBT Manager's application release workflow
builds the guest on a plain runner with the NBT toolchain (no private image),
signs it with the apps key after a maintainer approves the run (the `release`
environment, secret `APPS_SIGNING_KEY`, tags `v*` only) and publishes
`pcsx-X.Y.Z.nbt`, sequence `X*1000000 + Y*1000 + Z`. `release/sdk.ref` is the
SDK commit both build against: [SDK
0.2.0](https://github.com/NBTFoundry/sdk/releases/tag/v0.2.0).

## To confirm on the head unit

- Full speed with sound (Show FPS): otherwise Frame skip, the GPU thread, then
  NEON (`port-perf`) once the car session allows it.
- The recompiler's memory (executable `.bss`, `__clear_cache`) on the car,
  as in the VM.
- Disc images read from the hard disk while playing; a disc swap.
- The profile follows a pad plugged in and out; the iDrive controller plays
  without one.

## Layout

| Path | Contents |
| --- | --- |
| `third_party/pcsx_rearmed/` | PCSX ReARMed r26l and the fork's two changes (submodule) |
| `src/main.cpp` | The application: the SDK's libretro host with PCSX ReARMed's settings |
| `src/controls.*` | The PlayStation layout for each pad family, the iDrive controller and the keyboard |
| `tests/` | Controls unit test (`controls_test.cpp`), play and package tests (`test_pcsx.py`) |
| `tools/` | PCSX ReARMed's version for the package (`package_version.py`), notices (`make_notice.py`) |
| `release/` | The package description and the SDK commit to build against |

## License

Copyright (c) 2026 Fabien Poussin. Original code, tests, build scripts and
documentation are licensed under **GPL-2.0-or-later**, as PCSX ReARMed is; see
[LICENSE](LICENSE). The application's binary contains PCSX ReARMed, the
libraries it bundles, the NBT App SDK (MPL-2.0) and the NBT toolchain's
runtime, under their own licences: [legal/README.md](legal/README.md) and
[legal/NOTICE.txt](legal/NOTICE.txt). Original NBTFoundry logos and artwork
are MPL-2.0; copyright permission for artwork does not grant trademark rights
or imply endorsement by BMW AG or Sony Interactive Entertainment.
