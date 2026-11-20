// SPDX-License-Identifier: GPL-2.0-or-later
/* The PlayStation pad on a USB gamepad, the iDrive controller and the desktop
 * keyboard. */
#ifndef NBT_PCSX_CONTROLS_HPP
#define NBT_PCSX_CONTROLS_HPP

#include "nbt/frontend/pad_profiles.hpp"

namespace pcsx {

/* Each pad family has the PlayStation pad's layout, button for button by
 * position: the bottom face button is Cross, the right one Circle, the left
 * one Square, the top one Triangle. Actions are RETRO_DEVICE_ID_JOYPAD_* of
 * port 0, which the core maps as the RetroPad: B Cross, A Circle, Y Square,
 * X Triangle, L/R L1/R1, L2/R2, L3/R3. */
const nbt::frontend::Profiles& controls();

}  // namespace pcsx

#endif /* NBT_PCSX_CONTROLS_HPP */
