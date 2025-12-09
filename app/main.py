import sys
import os
from pathlib import Path

COMMANDS = ["exit", "echo", "type"]

def handle_type(command: str) -> None:
    os_bin_paths = os.environ["PATH"].split(os.pathsep)

    if command in COMMANDS:
        sys.stdout.write(f"{command} is a shell builtin \n")
        return

    for path in os_bin_paths:
        cmd_path = Path(path) / command
        if cmd_path.exists() and os.access(cmd_path, os.X_OK):
                sys.stdout.write(f"{command} is {cmd_path} \n")
                return
        
    sys.stdout.write(f"{command}: not found \n")

def main():
    while True:
        command, *args = input("$ ").split(" ")
        match command:
            case "exit":
                break
            case "echo":
                sys.stdout.write(f"{" ".join(args)}\n")
            case "type":
                handle_type(args[0])
            case _:
                sys.stdout.write(f"{command}: command not found")
                sys.stdout.write("\n")

if __name__ == "__main__":
    main()
