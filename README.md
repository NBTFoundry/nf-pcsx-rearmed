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

PCSX ReARMed's libretro core, unmodified, on the NBT App SDK's libretro host,
with its ARM dynamic recompiler: the frame scaled to the car's panel, sound
through the car's speakers, memory cards, save states, disc swaps and a pause
menu. Discs come from a USB stick, copied to the head unit's hard disk.
Installed and launched through NBT Manager.

**Supported head units:** BMW NBT Evo (iDrive 6). Support for the earlier NBT
may come later.

Part of [NBTFoundry](https://github.com/NBTFoundry):
[manager](https://github.com/NBTFoundry/manager) ·
[sdk](https://github.com/NBTFoundry/sdk) ·
[mobile-app](https://github.com/NBTFoundry/mobile-app) ·
[installer](https://github.com/NBTFoundry/installer) ·
[nf-doom](https://github.com/NBTFoundry/nf-doom) ·
[nf-snes9x](https://github.com/NBTFoundry/nf-snes9x)

Not affiliated with or endorsed by BMW AG or Sony Interactive Entertainment.
BMW, iDrive and NBT are trademarks of BMW AG; PlayStation is a trademark of
Sony Interactive Entertainment Inc. No game and no BIOS is included: use only
games and BIOS files you own.

## Status

Work in progress: not yet tested in a car.

## Build

Needs the NBT App SDK next to this repository (`../sdk`, or `NBT_SDK_DIR`),
gcc, Python 3, rsync, and the X11, EGL and GLESv2 development files; Xvfb for
the tests. `git submodule update --init` fetches PCSX ReARMed (not its own
`libpicofe` submodule, which the libretro core does not use).

## Layout

| Path | Contents |
| --- | --- |
| `third_party/pcsx_rearmed/` | PCSX ReARMed r26l, unmodified (submodule) |

## License

Copyright (c) 2026 Fabien Poussin. Original code, tests, build scripts and
documentation are licensed under **GPL-2.0-or-later**, as PCSX ReARMed is; see
[LICENSE](LICENSE). The application's binary also contains the NBT App SDK
(MPL-2.0) and the libraries PCSX ReARMed bundles, under their own licences.
Original NBTFoundry logos and artwork are MPL-2.0; copyright permission for
artwork does not grant trademark rights or imply endorsement by BMW AG or Sony
Interactive Entertainment.
