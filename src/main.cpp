// SPDX-License-Identifier: GPL-2.0-or-later
/* PCSX ReARMed on NBT Manager: the upstream libretro core, linked statically,
 * on the SDK's libretro host (game list, memory card, states, disc swaps,
 * pause menu, controls). */
#include <stddef.h>

#include "controls.hpp"
#include "nbt/retro/host.hpp"

namespace {

/* The games offered: disc images and lists (release/package.args has the
 * files NBT Manager accepts, which add the tracks and BIOS files: .bin, .sub,
 * .sbi are read by the core, never started). */
const char* const kExtensions[] = {"cue", "chd", "pbp", "m3u", "iso", "img",
                                   "mdf", "toc", "cbn", "exe", NULL};
/* A game folder (a folder or zip archive with a playlist or cue sheet,
 * imported whole: `|folders=` in release/package.args) opens at its playlist,
 * else its cue sheet; the rest are fallbacks. */
const char* const kFolderMains[] = {"m3u", "cue", "ccd", "mds", "toc", "cbn", "chd",
                                    "pbp", "iso", "img", "bin", NULL};

/* Manager settings feeding the core's variables (frontend/libretro_core_options.h):
 * setting value, core value. */
const char* const kRegion[] = {"auto", "auto", "ntsc", "NTSC", "pal", "PAL", NULL};
const char* const kBios[] = {"auto", "auto", "hle", "HLE", NULL};
const char* const kDynarec[] = {"on", "enabled", "off", "disabled", NULL};
const char* const kGpuThread[] = {"auto", "auto", "on", "enabled", "off", "disabled", NULL};
/* The core skips frames itself (it does not ask GET_AUDIO_VIDEO_ENABLE). */
const char* const kSkipType[] = {"off", "disabled", "1", "fixed_interval", "2", "fixed_interval", NULL};
const char* const kSkipInterval[] = {"1", "1", "2", "2", NULL};
const nbt::retro::VariableMap kVariables[] = {
    {"region", "pcsx_rearmed_region", kRegion},
    {"bios", "pcsx_rearmed_bios", kBios},
    {"dynarec", "pcsx_rearmed_drc", kDynarec},
    {"gpu_thread", "pcsx_rearmed_gpu_thread_rendering", kGpuThread},
    {"frameskip", "pcsx_rearmed_frameskip_type", kSkipType},
    {"frameskip", "pcsx_rearmed_frameskip_interval", kSkipInterval}};

}  // namespace

int main(int argc, char** argv) {
  const nbt::retro::HostConfig config = {"pcsx",
                                         "PCSX ReARMed",
                                         "PlayStation",
                                         kExtensions,
                                         &pcsx::controls(),
                                         kVariables,
                                         sizeof(kVariables) / sizeof(kVariables[0]),
                                         4.0f / 3.0f,
                                         0 /* the core reads its discs itself */,
                                         true /* BIOS files with the games */,
                                         kFolderMains};
  return nbt::retro::run(argc, argv, config);
}
