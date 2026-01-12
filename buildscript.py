from __future__ import annotations

__all__ = ()

import os
import shutil
import subprocess
import sys
from pathlib import Path
from platform import system

from setuptools import Distribution
from setuptools import Extension
from setuptools.command.build_ext import build_ext

_coverage_compile_args: list[str] = []
_coverage_links_args: list[str] = []
if os.environ.get("EGRAPHICS_BUILD_WITH_COVERAGE", "0") == "1":
    if system() == "Windows":
        print("Cannot build with coverage on windows.")
        sys.exit(1)
    _coverage_compile_args = ["-fprofile-arcs", "-ftest-coverage", "-O0"]
    _coverage_links_args = ["-fprofile-arcs"]

libraries: list[str] = ["SDL3"]
extra_link_args: list[str] = []
define_macros: list[tuple[str, None | str]] = [
    ("VMA_STATIC_VULKAN_FUNCTIONS", "0"),
    ("VMA_DYNAMIC_VULKAN_FUNCTIONS", "1"),
]
if system() == "Windows":
    libraries.extend(["opengl32", "glu32"])
elif system() == "Darwin":
    extra_link_args.extend(["-framework", "OpenGL"])
    define_macros.extend([("GL_SILENCE_DEPRECATION", None)])
else:
    libraries.extend(["GL", "GLU"])

_egraphics = Extension(
    "egraphics._egraphics",
    libraries=libraries,
    library_dirs=["vendor/SDL"],
    include_dirs=[
        "src/egraphics",
        "vendor/glew/include",
        "vendor/emath/include",
        "vendor/SDL/include",
        "vendor/VulkanMemoryAllocator/include",
    ],
    sources=["src/egraphics/_egraphics.c", "vendor/glew/src/glew.c", "src/egraphics/_vma.cpp"],
    extra_compile_args=_coverage_compile_args,
    extra_link_args=_coverage_links_args + extra_link_args,
    define_macros=[("GLEW_STATIC", None)] + define_macros,
)

try:
    vulkan_sdk_path = os.environ["VULKAN_SDK"]
    if system() == "Windows":
        if not os.path.isdir(vulkan_sdk_path) and vulkan_sdk_path.startswith("/"):
            vulkan_sdk_path = f"{vulkan_sdk_path[1:2]}:/{vulkan_sdk_path[3:]}"
    print(f"Vulkan SDK: {vulkan_sdk_path}", file=sys.stderr)
    _egraphics.include_dirs.append(str(Path(vulkan_sdk_path) / "include"))
except KeyError:
    vulkan_sdk_path = None
    print("VULKAN_SDK env var not set, Vulkan headers may not be found", file=sys.stderr)


def _build_sdl() -> None:
    subprocess.run(
        [
            "cmake",
            ".",
            "-GNinja",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DSDL_TESTS=0",
            "-DSDL_TEST_LIBRARY=0",
        ],
        cwd="vendor/SDL",
        check=True,
    )
    subprocess.run(["cmake", "--build", ".", "--config", "Release"], cwd="vendor/SDL", check=True)


def _build() -> None:
    _build_sdl()
    cmd = build_ext(Distribution({"name": "extended", "ext_modules": [_egraphics]}))
    cmd.ensure_finalized()
    cmd.run()
    for output in cmd.get_outputs():
        dest = str(Path("src/egraphics/") / Path(output).name)
        print(f"copying {output} to {dest}...")
        shutil.copyfile(output, dest)


if __name__ == "__main__":
    _build()
