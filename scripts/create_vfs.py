#!/usr/bin/env python3
import zipfile
from pathlib import Path

VFS_DIR = Path("vfs")
VFS_DIR.mkdir(exist_ok=True)

def create_minimal():
    with zipfile.ZipFile(VFS_DIR / "minimal.zip", "w") as zf:
        zf.writestr("hello.txt", "Hello from minimal VFS!\n")
    print("Created minimal.zip")

def create_several():
    with zipfile.ZipFile(VFS_DIR / "several.zip", "w") as zf:
        zf.writestr("readme.txt", "Several files\n")
        zf.writestr("data/info.txt", "Info\n")
        zf.writestr("data/list.txt", "a\nb\nc\n")
    print("Created several.zip")

def create_deep():
    with zipfile.ZipFile(VFS_DIR / "deep.zip", "w") as zf:
        zf.writestr("level1/readme.txt", "Level 1\n")
        zf.writestr("level1/level2/file.txt", "Level 2\n")
        zf.writestr("level1/level2/level3/deep.txt", "Deep content\n")
        zf.writestr("level1/level2/level3/another.txt", "Another\n")
    print("Created deep.zip")

def create_sample():
    with zipfile.ZipFile(VFS_DIR / "sample.zip", "w") as zf:
        zf.writestr("motd", "Welcome to the Virtual File System!\n")
        zf.writestr("home/user/hello.txt", "Hello, user!\n")
        zf.writestr("home/user/docs/guide.md", "# Guide\nUse ls, cd, cat...\n")
        zf.writestr("etc/config.ini", "[main]\nkey=value\n")
        zf.writestr("var/log/app.log", "log line 1\nlog line 2\n")
        zf.writestr("tmp/", "")
    print("Created sample.zip")

if __name__ == "__main__":
    create_minimal()
    create_several()
    create_deep()
    create_sample()
    print("All VFS archives created.")