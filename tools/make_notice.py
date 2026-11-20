#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Writes legal/NOTICE.txt: the notices the application's guest carries.

Ours and PCSX ReARMed's licence (GPL-2.0-or-later), PCSX ReARMed's authors,
the libraries it bundles and the guest links (read from their own files),
the NBT App SDK (MPL-2.0) and its third-party notices (NBT_SDK_DIR, default
../sdk), and picolibc, which the NBT toolchain's runtime links statically
(NBT_TOOLCHAIN, default the SDK's installed release). Run again when the
pin, a bundled library or the toolchain changes.
"""
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get("NBT_SDK_DIR", ROOT.parent / "sdk"))
CORE = ROOT / "third_party/pcsx_rearmed"
CHDR = CORE / "deps/libchdr"
RULE = "\n" + "=" * 72 + "\n\n"

HEADER = """NBTFoundry

NBTFoundry nf-pcsx-rearmed
Copyright (c) 2026 Fabien Poussin
Original software: GPL-2.0-or-later. You may redistribute and modify it under that license.
This software comes WITHOUT ANY WARRANTY, to the extent permitted by law.
Original NBTFoundry artwork: MPL-2.0. Trademark rights are separate.
Source: https://github.com/NBTFoundry/nf-pcsx-rearmed
When redistributing binaries, include applicable notices and provide the source required by the component licenses.

The application's binary contains PCSX ReARMed and is distributed under the
GNU General Public License, version 2 or later: its complete source is the
repository above with its submodule (NBTFoundry/pcsx_rearmed, a fork of
notaz/pcsx_rearmed) and the NBT App SDK it names (release/sdk.ref). No game
and no BIOS is included.
"""


def toolchain() -> Path:
    if os.environ.get("NBT_TOOLCHAIN"):
        return Path(os.environ["NBT_TOOLCHAIN"])
    version = re.search(r"^NBT_TOOLCHAIN_VERSION := (\S+)", (SDK / "module/flags.mk").read_text(), re.M)
    return SDK / "toolchain" / f"nbt-toolchain-{version.group(1)}"


def leading_comment(path: Path) -> str:
    """A source file's licence: its first comment, without the comment marks."""
    text = path.read_text()
    block = text[text.index("/*") + 2 : text.index("*/")]
    return "\n".join(re.sub(r"^ ?\* ?", "", line).rstrip() for line in block.strip("\n").split("\n")) + "\n"


def main():
    runtime = toolchain() / "share/licenses/picolibc"
    if not runtime.is_dir():
        sys.exit(f"no picolibc notices in {runtime}: set NBT_TOOLCHAIN")
    revision = subprocess.run(["git", "-C", str(CORE), "describe", "--tags", "--always"],
                              capture_output=True, text=True).stdout.strip()
    sdk_notices = subprocess.run([sys.executable, str(SDK / "tools/third_party_notices.py")],
                                 check=True, capture_output=True, text=True).stdout
    parts = [
        HEADER,
        "Head-unit risk and disclaimer\n\n" + (ROOT / "DISCLAIMER.md").read_text().split("\n", 1)[1],
        "GPL-2.0-or-later: this application and PCSX ReARMed\n\n" + (ROOT / "LICENSES/GPL-2.0-or-later.txt").read_text(),
        f"PCSX ReARMed {revision}, the emulator (third_party/pcsx_rearmed)\n"
        "https://github.com/notaz/pcsx_rearmed; GNU GPL version 2 or later (above). Its authors:\n\n"
        + (CORE / "AUTHORS").read_text(),
        "libchdr, CHD disc images (third_party/pcsx_rearmed/deps/libchdr)\n\n" + (CHDR / "LICENSE.txt").read_text(),
        "zlib 1.3.1, used by libchdr (deps/libchdr/deps/zlib-1.3.1)\n\n"
        + (CHDR / "deps/zlib-1.3.1/LICENSE").read_text(),
        "Zstandard 1.5.6, used by libchdr (deps/libchdr/deps/zstd-1.5.6), under its BSD licence\n\n"
        + (CHDR / "deps/zstd-1.5.6/LICENSE").read_text(),
        "LZMA SDK 24.05, used by libchdr (deps/libchdr/deps/lzma-24.05)\n\n"
        + (CHDR / "deps/lzma-24.05/LICENSE").read_text() + "\n",
        "dr_flac, used by libchdr (deps/libchdr/include/dr_libs/dr_flac.h)\n"
        "Public domain (Unlicense) or MIT No Attribution, at the user's choice.\n",
        "libretro-common, used by PCSX ReARMed (deps/libretro-common): libretro.h, "
        "features/features_cpu.c, rthreads/rthreads.c\n\n"
        + leading_comment(CORE / "deps/libretro-common/features/features_cpu.c"),
        "MPL-2.0: the NBT App SDK (https://github.com/NBTFoundry/sdk)\n\n" + (ROOT / "LICENSES/MPL-2.0.txt").read_text(),
        sdk_notices,
        "picolibc, the C library of the NBT toolchain's runtime, linked statically "
        "(https://github.com/picolibc/picolibc)\n\n"
        + (runtime / "COPYING.picolibc").read_text() + RULE.lstrip("\n")
        + "picolibc's newlib-derived parts\n\n" + (runtime / "COPYING.NEWLIB").read_text(),
    ]
    text = "\n\n" + RULE.join(p.rstrip("\n") + "\n" for p in parts)
    (ROOT / "legal").mkdir(exist_ok=True)
    (ROOT / "legal/NOTICE.txt").write_text(text)
    print(f"legal/NOTICE.txt: {len(parts)} sections")


if __name__ == "__main__":
    main()
