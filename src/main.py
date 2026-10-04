import os
import sys

class ShellEmulator:
    def __init__(self, vfs_name="VFS"):
        self.vfs_name = vfs_name
        self.running = True

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
        return self.vfs_name + ":/$ "

    def repl(self):
        while self.running:
            try:
                line = input(self.prompt())
                cmd, args = self.parse(line)
                self.execute(cmd, args)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                continue

def main():
    vfs_name = "VFS"
    if len(sys.argv) > 1 and sys.argv[1] == "--vfs-name" and len(sys.argv) > 2:
        vfs_name = sys.argv[2]

    shell = ShellEmulator(vfs_name=vfs_name)
    shell.repl()

if __name__ == "__main__":
    main()