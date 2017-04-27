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
import re


class BuildNginx(CrossCompileAutotoolsProject):
    repository = "https://github.com/CTSRD-CHERI/nginx.git"
    # we have to build in the source directory, out-of-source is broken
    # defaultBuildDir = CrossCompileAutotoolsProject.defaultSourceDir
    requiresGNUMake = True
    add_host_target_build_config_options = False
    warningFlags = CrossCompileAutotoolsProject.warningFlags + ["-Wno-error=cheri-capability-misuse"]
    defaultOptimizationLevel = ["-O2"]

    def __init__(self, config: CheriConfig):
        super().__init__(config)
        self.COMMON_FLAGS.append("-static")  # adding it to LDFLAGS only doesn't seem to be enough
        self.COMMON_FLAGS.extend(["-pedantic",
                                  "-Wno-gnu-statement-expression",
                                  "-Wno-flexible-array-extensions",  # TODO: could this cause errors?
                                  "-Wno-extended-offsetof",
                                  "-Wno-format-pedantic",
                                  ])
        self.configureEnvironment["AR"] = str(self.sdkBinDir / "cheri-unknown-freebsd-ar")
        self.configureCommand = self.sourceDir / "auto/configure"

    def install(self, **kwargs):
        # We have to run make inside the source directory so that it invokes make -f $build/Makefile
        self.runMakeInstall(cwd=self.sourceDir)
        self.installFile(self.sourceDir / "fetchbench", self.installDir / "sbin/fetchbench")
        # install the benchmark script
        benchmark = self.readFile(self.sourceDir / "nginx-benchmark.sh")
        benchmark = re.sub(r'NGINX=".*"', "NGINX=\"" + str(self.installPrefix / "sbin/nginx") + "\"", benchmark)
        benchmark = re.sub(r'FETCHBENCH=".*"', "FETCHBENCH=\"" + str(self.installPrefix/ "sbin/fetchbench") + "\"",
                           benchmark)
        self.writeFile(self.destdir / "nginx-benchmark.sh", benchmark, overwrite=True)

    def needsConfigure(self):
        return not (self.buildDir / "Makefile").exists()

    def configure(self):
        self.LDFLAGS.append("-v")
        self.configureArgs.extend(["--with-debug",
                                   "--without-pcre",
                                   "--without-http_rewrite_module",
                                   "--crossbuild=FreeBSD:12.0-CURRENT:mips",
                                   "--builddir=" + str(self.buildDir),
                                   "--with-cc-opt=" + " ".join(self.default_compiler_flags),
                                   "--with-ld-opt=" + " ".join(self.default_ldflags),
                                   "--sysroot=" + str(self.sdkSysroot),
                                   ])
        self.configureEnvironment["CC_TEST_FLAGS"] = " ".join(self.default_compiler_flags)
        self.configureEnvironment["NGX_TEST_LD_OPT"] = " ".join(self.default_ldflags)
        self.configureEnvironment["NGX_SIZEOF_int"] = "4"
        self.configureEnvironment["NGX_SIZEOF_sig_atomic_t"] = "4"  # on mips it is an int
        self.configureEnvironment["NGX_SIZEOF_long"] = "8"
        self.configureEnvironment["NGX_SIZEOF_long_long"] = "8"
        self.configureEnvironment["NGX_SIZEOF_size_t"] = "8"
        self.configureEnvironment["NGX_SIZEOF_off_t"] = "8"
        self.configureEnvironment["NGX_SIZEOF_time_t"] = "8"
        self.configureEnvironment["NGX_SIZEOF_void_p"] = "32" if self.config.cheriBits == 256 else "16"
        self.configureEnvironment["NGX_HAVE_MAP_DEVZERO"] = "yes"
        self.configureEnvironment["NGX_HAVE_SYSVSHM"] = "yes"
        self.configureEnvironment["NGX_HAVE_MAP_ANON"] = "yes"
        self.configureEnvironment["NGX_HAVE_POSIX_SEM"] = "yes"
        super().configure(cwd=self.sourceDir)

    def compile(self, **kwargs):
        # We have to run make inside the source directory so that it invokes make -f $build/Makefile
        super().compile(cwd=self.sourceDir)
