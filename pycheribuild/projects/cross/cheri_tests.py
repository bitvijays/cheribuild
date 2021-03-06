#
# Copyright (c) 2017 Alex Richardson
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

if False:
    # FIXME: move to CheriBSD
    class BuildCheriTests(CrossCompileCMakeProject):
        repository = GitRepository("https://github.com/arichardson/cheri-tests.git")
        native_install_dir = DefaultInstallDir.IN_BUILD_DIRECTORY
        cross_install_dir = DefaultInstallDir.ROOTFS
        default_build_type = BuildType.RELWITHDEBINFO
        project_name = "cheri-tests"



    class BuildRtldTests(CrossCompileCMakeProject):
        repository = GitRepository("https://github.com/arichardson/rtld-tests.git")
        native_install_dir = DefaultInstallDir.IN_BUILD_DIRECTORY
        cross_install_dir = DefaultInstallDir.ROOTFS
        default_build_type = BuildType.DEBUG
        project_name = "rtld-tests"

        def __init__(self, config: CheriConfig, *args, **kwargs):
            super().__init__(config, *args, **kwargs)
            self._linkage = Linkage.DYNAMIC
            assert not self.force_static_linkage
            assert self.force_dynamic_linkage
