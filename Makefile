# SPDX-License-Identifier: GPL-2.0-or-later
SHELL := /bin/bash

BUILD_DIR ?= build
OBJ_DIR := $(BUILD_DIR)/obj

APP_VERSION ?= 0.0.1
APP_SEQ ?= 1
APP_KEY ?=
# Sibling NBTFoundry checkouts; override as needed. The SDK is built into
# $(BUILD_DIR)/sdk; the manager is only needed for packaging.
NBT_SDK_DIR ?= ../sdk
NBT_MGR_DIR ?= ../manager
# The QNX SDP builds only the SDK's nbt-runner, for the VM test: the
# application itself is GPL, so it is a guest, never a QNX build. On the car,
# NBT Manager's own nbt-runner runs the guest (bridge 1.7, runner).
QNX_ENV ?=
QNX_SCREEN_LIBDIR ?=

CC ?= gcc
CXX ?= g++

NBT_SDK_BUILD_DIR := $(abspath $(BUILD_DIR))/sdk
include $(NBT_SDK_DIR)/nbt-sdk.mk
# Each kind of object rebuilds when its compile command changes (the SDK's
# nbt-stamp.mk; the stamps are written at the end of this file).
stamp = $(OBJ_DIR)/$(1).stamp
ifeq ($(value nbt_stamp),)
$(error $(NBT_SDK_ROOT) has no nbt-stamp.mk: update that SDK checkout)
endif

# --- PCSX ReARMed: built by upstream's own Makefile.libretro, unmodified ---
# Upstream writes its objects next to its sources and sets flags per object,
# so each build kind gets a copy of the submodule under $(BUILD_DIR)/core/
# (objects kept between runs) and upstream's make there produces the core as
# a static library. Flags reach it through the environment: upstream appends
# to CFLAGS. GIT_DIR gives its version string the submodule's commit.
CORE_SRC := third_party/pcsx_rearmed
CORE_GIT_DIR := $(shell git -C $(CORE_SRC) rev-parse --absolute-git-dir 2>/dev/null)
CORE_LIB_NAME := libpcsx_rearmed.a
# The libretro core: the software renderer gpu_unai, no physical CD-ROM, no
# libretro VFS, no shared libraries (-DNO_DYLIB: plugins are built in).
CORE_MAKE_ARGS := platform=unix STATIC_LINKING=1 TARGET=$(CORE_LIB_NAME) BUILTIN_GPU=unai \
	HAVE_PHYSICAL_CDROM=0 USE_LIBRETRO_VFS=0 fpic=
core_dir = $(BUILD_DIR)/core/$(1)
core_lib = $(call core_dir,$(1))/$(CORE_LIB_NAME)

# Our command line's CFLAGS and CXXFLAGS (make passes them on in MAKEFLAGS)
# would replace upstream's own instead of adding to them: they stay ours.
CORE_MAKEFLAGS = MAKEFLAGS='$(filter-out CFLAGS=% CXXFLAGS=%,$(MAKEFLAGS))'
# $(call core_build,kind): upstream's make with CORE_ENV_<kind> in its
# environment and CORE_ARGS_<kind> as arguments. When those or the toolchain
# (the kind's core stamp) changed since the copy's objects were built, they go
# first: upstream's make would keep them.
define core_build
	@mkdir -p $(call core_dir,$(1))
	@if ! cmp -s $(call stamp,core-$(1)) $(call core_dir,$(1))/.stamp \
		|| test $(call stamp,core-$(1)) -nt $(call core_dir,$(1))/.stamp; then \
		test ! -f $(call core_dir,$(1))/.stamp || echo "core $(1): build stamp changed, rebuilding it"; \
		find $(call core_dir,$(1)) -name '*.o' -delete; cp $(call stamp,core-$(1)) $(call core_dir,$(1))/.stamp; fi
	tar -C $(CORE_SRC) --exclude=.git --exclude='*.o' --exclude='*.a' --exclude=./include/revision.h -cf - . \
		| tar -C $(call core_dir,$(1)) -xf -
	cd $(call core_dir,$(1)) && GIT_DIR=$(CORE_GIT_DIR) $(CORE_ENV_$(1)) $(CORE_MAKEFLAGS) $(MAKE) --no-print-directory \
		-f Makefile.libretro $(CORE_MAKE_ARGS) $(CORE_ARGS_$(1))
endef

.PHONY: FORCE
FORCE:

# Host and sanitizer builds: the interpreter (upstream's x86 dynarec is
# lightrec, which the head unit does not use).
CORE_ENV_host := CFLAGS="-DNO_DYLIB"
CORE_ARGS_host := DYNAREC=0
$(call core_lib,host): FORCE
	$(call core_build,host)

CORE_ENV_asan := CFLAGS="-DNO_DYLIB -fno-omit-frame-pointer"
CORE_ARGS_asan := DYNAREC=0 DEBUG_ASAN=1
$(call core_lib,asan): FORCE
	$(call core_build,asan)

# The guest: the ARM dynarec (ari64) in ARM state, no NEON, with the NBT
# toolchain's flags and runtime (sdk/module/flags.mk).
CORE_ENV_guest = CFLAGS="$(NBT_MOD_CFLAGS) -DNO_DYLIB"
CORE_ARGS_guest = CC="$(NBT_MOD_CC)" CXX="$(NBT_MOD_CXX)" AR="$(NBT_MOD_AR)" ARCH=arm DYNAREC=ari64 HAVE_NEON_ASM=0
$(call core_lib,guest): FORCE | nbt-sdk-mod
	$(call core_build,guest)

# --- Ours: the application on the SDK's libretro host ---
APP_SRC := src/controls.cpp src/main.cpp
APP_INC := $(NBT_SDK_INC) $(NBT_SDK_LIBRETRO_INC) -Isrc
APP_CXXFLAGS := -std=c++11 -O2 -Wall -Wextra -Werror -fno-exceptions -fno-rtti $(CXXFLAGS)
app_objs = $(patsubst %.cpp,$(OBJ_DIR)/$(1)/%.o,$(APP_SRC))

HOST_APP := $(BUILD_DIR)/nbt-pcsx-host
ASAN_APP := $(BUILD_DIR)/nbt-pcsx-asan
ASAN_FLAGS := -O1 -g -fsanitize=address -fno-omit-frame-pointer
# The core after the SDK: the libretro host calls it (GNU ld takes from an
# archive only what is already wanted).
CORE_HOST_LDLIBS := -lm -lpthread

.PHONY: all host test test-asan check-static-init format guest vm-test package package-args notice clean

all: host test

# --- Host (Linux, X11) ---
$(OBJ_DIR)/host/src/%.o: src/%.cpp $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) -MMD -MP -c $< -o $@

$(HOST_APP): $(call app_objs,host) $(NBT_SDK_FRONT_HOST_LIBS) $(call core_lib,host)
	$(CXX) $(call app_objs,host) $(NBT_SDK_FRONT_HOST_LIBS) $(call core_lib,host) $(LDFLAGS) \
		$(NBT_SDK_HOST_LDLIBS) $(CORE_HOST_LDLIBS) -o $@

host: $(HOST_APP) $(BUILD_DIR)/controls-test

# --- Sanitizer build: the core under AddressSanitizer (upstream's
# DEBUG_ASAN), ours under UBSan too ---
$(OBJ_DIR)/asan/src/%.o: src/%.cpp $(call stamp,asan)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined -MMD -MP -c $< -o $@

$(ASAN_APP): $(call app_objs,asan) $(NBT_SDK_FRONT_ASAN_LIBS) $(call core_lib,asan)
	$(CXX) $(ASAN_FLAGS) -fsanitize=undefined $(call app_objs,asan) $(NBT_SDK_FRONT_ASAN_LIBS) \
		$(call core_lib,asan) $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) $(CORE_HOST_LDLIBS) -o $@

# --- Tests ---
$(OBJ_DIR)/host/tests/%.o: tests/%.cpp $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) -MMD -MP -c $< -o $@

$(BUILD_DIR)/controls-test: $(OBJ_DIR)/host/tests/controls_test.o $(OBJ_DIR)/host/src/controls.o \
		$(NBT_SDK_FRONT_HOST_LIBS)
	$(CXX) $^ $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) -o $@

$(BUILD_DIR)/controls-asan: tests/controls_test.cpp src/controls.cpp src/controls.hpp \
		$(NBT_SDK_FRONT_ASAN_LIBS)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined tests/controls_test.cpp \
		src/controls.cpp $(NBT_SDK_FRONT_ASAN_LIBS) $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) -o $@

test: host
	python3 tools/package_version.py --check release/package.args
	$(BUILD_DIR)/controls-test
	NBT_PCSX_APP=$(abspath $(HOST_APP)) NBT_MGR_DIR=$(abspath $(NBT_MGR_DIR)) \
		python3 -m unittest discover -s tests -v

test-asan: $(ASAN_APP) $(BUILD_DIR)/controls-asan
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
		$(BUILD_DIR)/controls-asan
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
		NBT_PCSX_APP=$(abspath $(ASAN_APP)) NBT_MGR_DIR=$(abspath $(NBT_MGR_DIR)) \
		python3 -m unittest discover -s tests -v -k Play

# Our objects only: the core's are upstream's business.
check-static-init: $(call app_objs,host)
	@set -e; \
	for obj in $^; do \
		ctors="$$(readelf -S "$$obj" | awk '/\.init_array|\.ctors/ {print $$2}')"; \
		if test -n "$$ctors"; then \
			echo "ERROR: static constructor section in $$obj: $$ctors"; exit 1; \
		fi; \
	done; \
	echo "OK: no .init_array/.ctors in our objects"
	+@$(NBT_SDK_MAKE) check-static-init

format:
	clang-format -i src/*.cpp src/*.hpp tests/*.cpp

# --- The guest: built without the QNX SDP, run by nbt-runner as its own
# process (sdk/guest). PCSX ReARMed is GPL: the QNX licence forbids linking
# it with QNX code, so it is a guest, never a module (the licence gate
# checks). ---
GUEST_APP := $(BUILD_DIR)/nbt-pcsx.guest
GUEST_APP_LICENSE := GPL-2.0-or-later
MOD_APP_CXXFLAGS := $(NBT_MOD_CXXFLAGS) -O2 -std=c++11 -Wall -Wextra -Werror -fno-exceptions -fno-rtti \
	$(APP_INC)

$(OBJ_DIR)/guest/src/%.o: src/%.cpp $(call stamp,guest) | nbt-sdk-mod
	@mkdir -p $(dir $@)
	$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS) -MMD -MP -c $< -o $@

GUEST_OBJ := $(call app_objs,guest) $(call core_lib,guest)

$(GUEST_APP): $(GUEST_OBJ) $(NBT_SDK_MOD_DEPS)
	$(call nbt_guest_link,$@,$(GUEST_OBJ),$(GUEST_APP_LICENSE))

guest: $(GUEST_APP)

# --- The guest in QNX 6.5 SP1 under QEMU (the SDK's tools/qnx65-vm; no GPU,
# no sound: both faked): a health check, then the test disc of
# tests/test_pcsx.py played through the ARM dynarec, which must map its
# memory, draw frames and stop cleanly. ---
VM_DISC := $(BUILD_DIR)/vm/Test.iso
VM_PLAY := NBT_LAUNCH=user NBT_SURFACE=5 NBT_RUNNER_FAKE_GL=1 NBT_RUNNER_FAKE_AUDIO=1 \
	NBT_DATA_DIR=/dev/shmem NBT_FILES_DIR=/proc/boot

$(VM_DISC): tests/test_pcsx.py
	@mkdir -p $(dir $@)
	python3 -c 'import sys; sys.path.insert(0, "tests"); import test_pcsx; \
		open(sys.argv[1], "wb").write(test_pcsx.iso_disc("TEST"))' $@

vm-test: $(NBT_SDK_RUNNER) $(GUEST_APP) $(VM_DISC)
	QEMU_RUN_SECS=180 $(NBT_SDK_ROOT)/tools/qnx65-vm/run.sh \
		-c "NBT_LAUNCH=check NBT_DATA_DIR=/dev/shmem nbt-runner --nbt-payload /proc/boot/$(notdir $(GUEST_APP)) &" \
		-c "waitfor /none 10" -c "slay -s TERM nbt-runner" -c "waitfor /none 3" \
		-c "$(VM_PLAY) nbt-runner --nbt-payload /proc/boot/$(notdir $(GUEST_APP)) --game Test.iso &" \
		-c "waitfor /none 60" -c "slay -s TERM nbt-runner" -c "waitfor /none 3" \
		-x 'stage: check' -x 'game Test\.iso: ' -x 'core: Mapped' -x 'fake-gl: closed: [1-9][0-9]* frames' \
		-x 'runner: guest exited status=0' \
		$^

# release/package.args's PCSX ReARMed version (tools/package_version.py): again
# when the pin moves; `make test` fails until then.
package-args:
	python3 tools/package_version.py release/package.args

# --- The signed package (release/package.args describes it) ---
PACKAGE_INPUT ?= $(GUEST_APP)
PACKAGE := $(BUILD_DIR)/pcsx-$(APP_VERSION).nbt

package: $(PACKAGE_INPUT)
	@test -f "$(APP_KEY)" || { echo "APP_KEY must name the RSA signing key"; exit 1; }
	@test -f "$(NBT_MGR_DIR)/tools/package.py" || { echo "NBT_MGR_DIR=$(NBT_MGR_DIR) has no tools/package.py"; exit 1; }
	rm -f $(PACKAGE)
	python3 $(NBT_MGR_DIR)/tools/package.py @release/package.args \
		--version "$(APP_VERSION)" \
		--sequence "$(APP_SEQ)" \
		--key "$(APP_KEY)" \
		--output $(PACKAGE) \
		$(PACKAGE_INPUT)

# legal/NOTICE.txt (tools/make_notice.py): again when the pin, a bundled
# library or the toolchain changes.
notice:
	NBT_SDK_DIR=$(NBT_SDK_ROOT) NBT_TOOLCHAIN=$(NBT_TOOLCHAIN) python3 tools/make_notice.py

clean:
	rm -rf $(BUILD_DIR)

DEPS := $(shell find $(OBJ_DIR) -name '*.d' 2>/dev/null)
-include $(DEPS)

$(call nbt_stamp,$(call stamp,host),$(CXX) $(APP_INC) $(APP_CXXFLAGS),$(CXX))
$(call nbt_stamp,$(call stamp,asan),$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined,$(CXX))
$(call nbt_stamp,$(call stamp,guest),$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS),,$(NBT_TOOLCHAIN)/VERSION)
$(call nbt_stamp,$(call stamp,core-host),$(CORE_MAKE_ARGS) $(CORE_ENV_host) $(CORE_ARGS_host),$(CC) $(CXX))
$(call nbt_stamp,$(call stamp,core-asan),$(CORE_MAKE_ARGS) $(CORE_ENV_asan) $(CORE_ARGS_asan),$(CC) $(CXX))
$(call nbt_stamp,$(call stamp,core-guest),$(CORE_MAKE_ARGS) $(CORE_ENV_guest) $(CORE_ARGS_guest),, \
	$(NBT_TOOLCHAIN)/VERSION)
