#
# Copyright (c) 2016 Alex Richardson
# All rights reserved.
#
# This software was developed by SRI International and the University of
# Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-10-C-0237
# ("CTSRD"), as part of the DARPA CRASH research programme.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

from .crosscompileproject import *
from ..cheribsd import BuildCHERIBSD
from ...utils import setEnv, runCmd


class BuildGDB(CrossCompileAutotoolsProject):
    defaultInstallDir = lambda config, cls: BuildCHERIBSD.rootfsDir(config) / "usr/local"
    repository = "https://github.com/bsdjhb/gdb.git"
    requiresGNUMake = True
    targetArch = "mips64"  # don't compile as a CHERI binary!

    def __init__(self, config: CheriConfig):
        # See https://github.com/bsdjhb/kdbg/blob/master/gdb/build
        self.useLld = False  # cheribsd mips sysroot is incompatible...
        super().__init__(config)
        self.gitBranch = "mips_cheri"
        # ./configure flags
        self.configureArgs.extend([
            "--enable-targets=mips64-unknown-freebsd",
            "--without-python",
            "--without-expat",
            "--disable-nls",
            "--without-libunwind-ia64",
            "--enable-tui",
            "--disable-ld",
            "--enable-64-bit-bfd",

            "--with-gdb-datadir=" + str(self.installPrefix / "share/gdb"),
            "--with-separate-debug-dir=/usr/lib/debug",
            "--mandir=/usr/local/man",
            "--infodir=/usr/local/info/",

            "--disable-werror",
            "MAKEINFO=/bin/false",
            # TODO:
            # "--enable-build-with-cxx"
        ])
        # extra ./configure environment variables:
        self.configureEnvironment.update(gl_cv_func_gettimeofday_clobber="no",
                                         lt_cv_sys_max_cmd_len="262144",
                                         # The build system run CC without any flags to detect dependency style...
                                         # (ZW_PROG_COMPILER_DEPENDENCIES([CC])) -> for gcc3 mode which seems correct
                                         am_cv_CC_dependencies_compiler_type="gcc3",
                                         MAKEINFO="/bin/false"
                                         )
        # compile flags
        self.warningFlags.extend(["-Wno-absolute-value", "-Wno-parentheses-equality", "-Wno-unknown-warning-option",
                                  "-Wno-unused-function", "-Wno-unused-variable"])
        # TODO: we should fix this:
        self.warningFlags.append("-Wno-error=implicit-function-declaration")
        self.warningFlags.append("-Wno-error=format")
        self.warningFlags.append("-Wno-error=incompatible-pointer-types")

        self.compileFlags.append("-static")  # seems like LDFLAGS is not enough
        self.compileFlags.extend(["-DRL_NO_COMPAT", "-g", "-DLIBICONV_PLUG", "-fno-strict-aliasing",
                                  "-I/usr/local/include"])
        self.cOnlyFlags.append("-std=gnu89")
        self.linkerFlags.append("-L/usr/local/lib")
        self.configureEnvironment.update(CONFIGURED_M4="m4", CONFIGURED_BISON="byacc", TMPDIR="/tmp", LIBS="")
        if self.makeCommand == "gmake":
            self.configureEnvironment["MAKE"] = "gmake"
        self.configureEnvironment["CC_FOR_BUILD"] = str(config.clangPath)
        self.configureEnvironment["CXX_FOR_BUILD"] = str(config.clangPlusPlusPath)

        # TODO: do I need these:
        """(cd $obj; env INSTALL="/usr/bin/install -c "  INSTALL_DATA="install   -m 0644"  INSTALL_LIB="install    -m 444"  INSTALL_PROGRAM="install    -m 555"  INSTALL_SCRIPT="install   -m 555"   PYTHON="${PYTHON}" SHELL=/bin/sh CONFIG_SHELL=/bin/sh CONFIG_SITE=/usr/ports/Templates/config.site ../configure ${CONFIGURE_ARGS} )"""

    def compile(self):
        # # don't build the documentation by touching the timestamp files
        # self.makedirs(self.buildDir / "bfd/doc")
        # runCmd("touch", 'aoutx.stamp', 'archive.stamp', 'archures.stamp', 'bfdio.stamp', 'bfdt.stamp', 'bfdwin.stamp', 'cache.stamp', 'chew.stamp', 'coffcode.stamp', 'core.stamp', 'elf.stamp', 'elfcode.stamp', 'format.stamp', 'hash.stamp', 'init.stamp', 'libbfd.stamp', 'linker.stamp', 'mmo.stamp', 'opncls.stamp', 'reloc.stamp', 'section.stamp', 'syms.stamp', 'targets.stamp')
        buildenv = self.configureEnvironment.copy()
        # it runs configure during the build step too...
        with setEnv(**buildenv):
            self.runMake(self.commonMakeArgs + [self.config.makeJFlag], cwd=self.buildDir)

    def install(self):
        self.runMake(self.makeInstallArgs + [self.config.makeJFlag], makeTarget="install-gdb", cwd=self.buildDir)
