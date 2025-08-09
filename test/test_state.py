import os
import subprocess
import sys

import pytest
from OpenGL.GL import GL_CLIP_DEPTH_MODE
from OpenGL.GL import GL_CLIP_ORIGIN
from OpenGL.GL import glGetIntegerv

from egraphics import ClipDepth
from egraphics import ClipOrigin
from egraphics import clip_space
from egraphics._egraphics import GL_LOWER_LEFT
from egraphics._egraphics import GL_NEGATIVE_ONE_TO_ONE
from egraphics._egraphics import GL_UPPER_LEFT
from egraphics._egraphics import GL_ZERO_TO_ONE


@pytest.mark.xfail(sys.platform == "darwin", reason="macos doesn't support glClipSpace")
def test_clip_space(platform):
    assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_LOWER_LEFT
    assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_NEGATIVE_ONE_TO_ONE
    with clip_space(ClipOrigin.TOP_LEFT, ClipDepth.ZERO_TO_ONE):
        assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_UPPER_LEFT
        assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_ZERO_TO_ONE
    assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_LOWER_LEFT
    assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_NEGATIVE_ONE_TO_ONE

    with clip_space(ClipOrigin.BOTTOM_LEFT, ClipDepth.ZERO_TO_ONE):
        assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_LOWER_LEFT
        assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_ZERO_TO_ONE
        with clip_space(ClipOrigin.TOP_LEFT, ClipDepth.NEGATIVE_ONE_TO_ONE):
            assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_UPPER_LEFT
            assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_NEGATIVE_ONE_TO_ONE
        assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_LOWER_LEFT
        assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_ZERO_TO_ONE
    assert glGetIntegerv(GL_CLIP_ORIGIN)[0] == GL_LOWER_LEFT
    assert glGetIntegerv(GL_CLIP_DEPTH_MODE)[0] == GL_NEGATIVE_ONE_TO_ONE


@pytest.mark.xfail(sys.platform == "darwin", reason="macos doesn't support glClipSpace")
@pytest.mark.parametrize("open_gl_version_max", [(4, 6), (4, 4)])
def test_clip_space_support(open_gl_version_max):
    process = subprocess.Popen(
        [sys.executable, "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = process.communicate(
        f"""
import os

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(os.getcwd() + "/vendor/SDL")

from egraphics import clip_space, ClipOrigin, ClipDepth
from eplatform import Platform

with Platform(open_gl_version_max={open_gl_version_max}):
    with clip_space(ClipOrigin.TOP_LEFT, ClipDepth.ZERO_TO_ONE):
        pass
    """.encode("utf8")
    )
    assert process.returncode == 0, (out, err)


def test_clip_space_not_supported():
    process = subprocess.Popen(
        [sys.executable, "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ | {"EGRAPHICS_GL_CLIP_CONTROL": "disabled"},
    )
    out, err = process.communicate(
        f"""
import os

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(os.getcwd() + "/vendor/SDL")

from egraphics import clip_space, ClipOrigin, ClipDepth
from eplatform import Platform

with Platform():
    ex = None
    try:
        with clip_space(ClipOrigin.TOP_LEFT, ClipDepth.ZERO_TO_ONE):
            pass
    except RuntimeError as _ex:
        ex = _ex
    assert str(ex) == "glClipControl not supported"

    ex = None
    try:
        with clip_space(ClipOrigin.BOTTOM_LEFT, ClipDepth.ZERO_TO_ONE):
            pass
    except RuntimeError as _ex:
        ex = _ex
    assert str(ex) == "glClipControl not supported"

    ex = None
    try:
        with clip_space(ClipOrigin.TOP_LEFT, ClipDepth.NEGATIVE_ONE_TO_ONE):
            pass
    except RuntimeError as _ex:
        ex = _ex
    assert str(ex) == "glClipControl not supported"

    with clip_space(ClipOrigin.BOTTOM_LEFT, ClipDepth.NEGATIVE_ONE_TO_ONE):
        pass
    """.encode("utf8")
    )
    assert process.returncode == 0, (out, err)
