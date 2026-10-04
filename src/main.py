#!/usr/bin/env python3
import argparse
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

class VFS:
    def __init__(self):
        self.tree = {
            "/": {"type": "dir", "content": None, "children": set()}
        }
        self.cwd = "/"

    def load_from_zip(self, zip_path):
        if not os.path.isfile(zip_path):
            raise FileNotFoundError("VFS file not found: " + zip_path)
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for info in zf.infolist():
                    name = info.filename.replace("\\", "/").rstrip("/")
                    if not name:
                        continue
                    path = "/" + name if not name.startswith("/") else name

                    
                    if path == "/":
                        continue
                    parent = path.rsplit("/", 1)[0]
                    if parent == "":
                        parent = "/"

                    self._ensure_dir(parent)

                    if info.is_dir() or info.filename.endswith("/"):
                        self._ensure_dir(path)
                    else:
                        data = zf.read(info.filename)
                        self.tree[path] = {
                            "type": "file",
                            "content": data,
                            "children": set(),
                        }
                        
                        name_only = path.rsplit("/", 1)[-1]
                        self.tree[parent]["children"].add(name_only)
        except zipfile.BadZipFile as e:
            raise ValueError("Invalid VFS format (not a valid ZIP): " + str(e))

    def _ensure_dir(self, path):
        if path in self.tree:
            if self.tree[path]["type"] != "dir":
                raise NotADirectoryError("Not a directory: " + path)
            return

        
        parts = [p for p in path.split("/") if p]
        current = "/"

        for part in parts:
            parent = current
            if current == "/":
                current = "/" + part
            else:
                current = current + "/" + part

            if current not in self.tree:
                self.tree[current] = {
                    "type": "dir",
                    "content": None,
                    "children": set(),
                }
                self.tree[parent]["children"].add(part)

    def resolve(self, path):
        if not path:
            return self.cwd
        if path.startswith("/"):
            abs_path = path
        else:
            if self.cwd == "/":
                abs_path = "/" + path
            else:
                abs_path = self.cwd.rstrip("/") + "/" + path
        parts = []
        for p in abs_path.split("/"):
            if p == "" or p == ".":
                continue
            if p == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(p)
        return "/" + "/".join(parts) if parts else "/"

    def exists(self, path):
        return self.resolve(path) in self.tree

    def is_dir(self, path):
        p = self.resolve(path)
        return p in self.tree and self.tree[p]["type"] == "dir"

    def is_file(self, path):
        p = self.resolve(path)
        return p in self.tree and self.tree[p]["type"] == "file"

    def list_dir(self, path="."):
        p = self.resolve(path)
        if p not in self.tree:
            raise FileNotFoundError("No such file or directory: " + path)
        if self.tree[p]["type"] != "dir":
            raise NotADirectoryError("Not a directory: " + path)
        return sorted(self.tree[p]["children"])

    def read_file(self, path):
        p = self.resolve(path)
        if p not in self.tree:
            raise FileNotFoundError("No such file or directory: " + path)
        if self.tree[p]["type"] != "file":
            raise IsADirectoryError("Is a directory: " + path)
        return self.tree[p]["content"] or b""

class ShellEmulator:
    def __init__(self, vfs_name="VFS"):
        self.vfs_name = vfs_name
        self.vfs = VFS()
        self.running = True
        self.history = []

    def expand_env(self, text):
        result = []
        i = 0
        while i < len(text):
            if text[i] == "$" and i + 1 < len(text):
                if text[i + 1] == "{":
                    end = text.find("}", i + 2)
                    if end != -1:
                        var = text[i + 2:end]
                        result.append(os.environ.get(var, ""))
                        i = end + 1
                        continue
                else:
                    j = i + 1
                    while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                        j += 1
                    var = text[i + 1:j]
                    result.append(os.environ.get(var, ""))
                    i = j
                    continue
            result.append(text[i])
            i += 1
        return "".join(result)

    def parse(self, line):
        line = line.strip()
        if not line:
            return "", []
        expanded = self.expand_env(line)
        parts = expanded.split()
        if not parts:
            return "", []
        return parts[0], parts[1:]

    def execute(self, cmd, args):
        if not cmd:
            return
        # Пока ещё заглушки (настоящие ls/cd сделаем на этапе 4)
        if cmd == "ls":
            print("ls called with args:", args)
        elif cmd == "cd":
            print("cd called with args:", args)
        elif cmd == "exit":
            if args:
                print("exit: too many arguments", file=sys.stderr)
            else:
                self.running = False
        else:
            print(cmd + ": command not found", file=sys.stderr)

    def prompt(self):
        return self.vfs_name + ":" + self.vfs.cwd + "$ "

    def run_line(self, line, echo=False):
        if echo:
            print(self.prompt() + line)
        cmd, args = self.parse(line)
        if cmd:
            self.history.append(line.strip())
            self.execute(cmd, args)

    def repl(self):
        while self.running:
            try:
                line = input(self.prompt())
                self.run_line(line)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                continue

    def run_script(self, script_path):
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    try:
                        self.run_line(line, echo=True)
                    except Exception as e:
                        print("Script error:", e, file=sys.stderr)
        except FileNotFoundError:
            print("Script not found:", script_path, file=sys.stderr)
            raise

def load_config(config_path):
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        cfg = {}
        for child in root:
            if child.tag == "vfs_path" and child.text:
                cfg["vfs_path"] = child.text.strip()
            elif child.tag == "script_path" and child.text:
                cfg["script_path"] = child.text.strip()
        return cfg
    except ET.ParseError as e:
        raise ValueError("Invalid XML config: " + str(e))
    except FileNotFoundError:
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs", dest="vfs_path")
    parser.add_argument("--script", dest="script_path")
    parser.add_argument("--config", dest="config_path")
    parser.add_argument("--vfs-name", dest="vfs_name", default="VFS")
    args = parser.parse_args()

    print("=== Debug: startup parameters ===")
    print("  CLI vfs_path   :", args.vfs_path)
    print("  CLI script_path:", args.script_path)
    print("  CLI config_path:", args.config_path)
    print("  vfs_name       :", args.vfs_name)

    cfg = {}
    if args.config_path:
        try:
            cfg = load_config(args.config_path)
            print("  Config loaded  :", cfg)
        except FileNotFoundError:
            print("Error: config file not found:", args.config_path, file=sys.stderr)
            return 1
        except ValueError as e:
            print("Error:", e, file=sys.stderr)
            return 1

    vfs_path = args.vfs_path or cfg.get("vfs_path")
    script_path = args.script_path or cfg.get("script_path")

    print("  Final vfs_path :", vfs_path)
    print("  Final script   :", script_path)
    print("=================================")

    shell = ShellEmulator(vfs_name=args.vfs_name)

    if vfs_path:
        try:
            shell.vfs.load_from_zip(vfs_path)
            print("VFS loaded from", vfs_path)
        except FileNotFoundError as e:
            print("Error loading VFS:", e, file=sys.stderr)
            return 1
        except ValueError as e:
            print("Error loading VFS:", e, file=sys.stderr)
            return 1
        except Exception as e:
            print("Error loading VFS:", e, file=sys.stderr)
            return 1

    if script_path:
        try:
            shell.run_script(script_path)
        except Exception:
            return 1

    if shell.running:
        shell.repl()

    return 0

if __name__ == "__main__":
    sys.exit(main())