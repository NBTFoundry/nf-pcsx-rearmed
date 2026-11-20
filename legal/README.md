<!-- SPDX-License-Identifier: GPL-2.0-or-later -->
# License notices

The repository's original work is licensed as described in its root README and LICENSE. Third-party components retain their own licenses and copyright notices, collected in [NOTICE.txt](NOTICE.txt) (written by `make notice`, `tools/make_notice.py`). Original NBTFoundry artwork is MPL-2.0.

| Component | Licence | Text |
| --- | --- | --- |
| This application (`src/`, `tests/`, `tools/`, build files) | GPL-2.0-or-later | [LICENSE](../LICENSE) |
| PCSX ReARMed (`third_party/pcsx_rearmed`) | GPL-2.0-or-later | its `COPYING`; NOTICE.txt |
| libchdr | BSD-3-Clause | its `LICENSE.txt`; NOTICE.txt |
| zlib 1.3.1 | Zlib | its `LICENSE`; NOTICE.txt |
| Zstandard 1.5.6 | BSD-3-Clause (of its BSD/GPL-2.0 choice) | its `LICENSE`; NOTICE.txt |
| LZMA SDK 24.05 | public domain | NOTICE.txt |
| dr_flac | Unlicense or MIT-0 | NOTICE.txt |
| libretro-common (libretro.h, features_cpu.c, rthreads.c) | MIT | NOTICE.txt |
| NBT App SDK and its third-party parts | MPL-2.0; MIT, public domain | [LICENSES/MPL-2.0.txt](../LICENSES/MPL-2.0.txt); NOTICE.txt |
| picolibc (the NBT toolchain's C library, linked in) | BSD-style | NOTICE.txt |
| compiler-rt, libc++, libc++abi, libunwind (linked in) | Apache-2.0 WITH LLVM-exception | no attribution owed in binaries |

The notices are a snapshot of the current dependencies. Update them when changing the pin, a bundled dependency or the toolchain. A binary distribution must include the applicable notices and the source the GPL requires: this repository, its submodule and the SDK commit it names (`release/sdk.ref`).

No PlayStation BIOS and no game is included or distributed.

See [DISCLAIMER.md](../DISCLAIMER.md) for head-unit risks and warranty and liability terms.
