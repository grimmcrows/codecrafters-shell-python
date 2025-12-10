import sys
import os
import subprocess
from pathlib import Path

COMMANDS = ["exit", "echo", "type", "pwd", "cd"]

def get_exec_path(command: str) -> Path:
    os_bin_paths = os.environ["PATH"].split(os.pathsep)

    for path in os_bin_paths:
        cmd_path = Path(path) / command
        if cmd_path.exists() and os.access(cmd_path, os.X_OK):
            return cmd_path
                
def format_input(user_input: str) -> tuple[str, list[str]]:
    sep_by_single_quote = [i.strip() for i in user_input.replace("''", '').split("'") if i.strip()]
    command, *args = [i.strip() for i in sep_by_single_quote[0].split(" ") if i.strip()]
    args = args + sep_by_single_quote[1:]

    return command, args

def handle_command_exec(command: str, args: list[str]):
    if get_exec_path(command):
        output = subprocess.run([command] + args, capture_output=True, text=True)
        if output.stderr:
            sys.stderr.write(output.stderr)
        if output.stdout:
            sys.stdout.write(output.stdout)
        
        return True

    return False

def handle_type(command: str) -> None:
    if command in COMMANDS:
        sys.stdout.write(f"{command} is a shell builtin \n")
        return
    
    if cmd_path := get_exec_path(command):
        sys.stdout.write(f"{command} is {cmd_path} \n")
        return

    sys.stdout.write(f"{command}: not found \n")

def handle_cd(path: str) -> str|None:
    if path == "~":
        os.chdir(os.path.expanduser(path))
        return

    dir = Path(path)
    if not dir.exists():
        return f"{dir}: No such file or directory"
    
    os.chdir(dir)

def main():
    while True:
        user_input = input("$ ")
        command, args = format_input(user_input)

        match command:
            case "exit":
                break
            case "echo":
                sys.stdout.write(f"{" ".join(args)}\n")
            case "type":
                handle_type(args[0])
            case "pwd":
                sys.stdout.write(f"{os.getcwd()} \n")
            case "cd":
                if dir_not_found := handle_cd(args[0]):
                    sys.stdout.write(f"{dir_not_found} \n")
            case _:
                if not handle_command_exec(command, args):
                    sys.stdout.write(f"{command}: command not found")
                    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
