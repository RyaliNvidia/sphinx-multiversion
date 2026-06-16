# -*- coding: utf-8 -*-
# Copyright (c) 2026 Jan Holthuis <jan.holthuis@rub.de>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause

import contextlib
import datetime
import importlib
import os
import tempfile
import types
import unittest
from unittest import mock

smv_main = importlib.import_module("sphinx_multiversion.main")


@contextlib.contextmanager
def chdir(path):
    original = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


class GitRef:
    commit = "abc123"
    creatordate = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
    is_remote = False
    name = "release/6.1"
    refname = "refs/heads/release/6.1"
    source = "heads"

    def __iter__(self):
        return iter((self.source, self.name))


class Project:
    def __init__(self, sourcedir, source_suffixes):
        self.sourcedir = sourcedir
        self.source_suffixes = source_suffixes

    def discover(self):
        return ["index"]


class MainTestCase(unittest.TestCase):
    def test_builds_use_versioned_confdir(self):
        with tempfile.TemporaryDirectory() as tmp_root:
            root = os.path.realpath(tmp_root)
            docs = os.path.join(root, "docs")
            output = os.path.join(root, "out")
            os.makedirs(docs)

            base_config = types.SimpleNamespace(
                release="",
                rst_prolog="",
                smv_branch_whitelist=".*",
                smv_outputdir_format="{ref.name}",
                smv_prefer_remote_refs=False,
                smv_released_pattern=r"^refs/tags/",
                smv_remote_whitelist=".*",
                smv_tag_whitelist=".*",
                source_suffix=[".rst"],
                version="",
            )
            calls = []

            def copy_tree(gitroot, source, repopath, gitref):
                os.makedirs(os.path.join(repopath, "docs"))

            def check_call(cmd, cwd=None, env=None):
                calls.append((cmd, cwd, env))

            with (
                chdir(root),
                mock.patch.object(
                    smv_main.git, "get_toplevel_path", return_value=root
                ),
                mock.patch.object(
                    smv_main.git, "get_refs", return_value=[GitRef()]
                ),
                mock.patch.object(
                    smv_main.git, "copy_tree", side_effect=copy_tree
                ),
                mock.patch.object(
                    smv_main, "load_sphinx_config", return_value=base_config
                ),
                mock.patch.object(smv_main.sphinx_project, "Project", Project),
                mock.patch.object(
                    smv_main.subprocess, "check_call", side_effect=check_call
                ),
            ):
                rc = smv_main.main(
                    [
                        docs,
                        output,
                        "--run-markdown-build",
                        "-D",
                        "custom=$name",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(len(calls), 2)

            for cmd, _, env in calls:
                args = list(cmd)
                confdir = args[args.index("-c") + 1]

                self.assertEqual(os.path.basename(confdir), "docs", args)
                self.assertEqual(
                    os.path.basename(os.path.dirname(confdir)), "abc123", args
                )
                self.assertNotEqual(confdir, docs)
                self.assertIn("custom=release/6.1", args)
                self.assertEqual(env["SPHINX_MULTIVERSION_CONFDIR"], confdir)


if __name__ == "__main__":
    unittest.main()
