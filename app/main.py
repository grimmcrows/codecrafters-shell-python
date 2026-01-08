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
    args = []
    word = ""
    in_single_quote = False
    in_double_quote = False
    i = 0
    length = len(user_input)

    while i < length:
        char = user_input[i]
        if in_double_quote:
            if char == "\\" and i + 1 < length:
                next_char = user_input[i + 1]
                if next_char in ['"', '\\']:
                    word += next_char
                    i += 1
                else:
                    word += char
            elif char == '"':
                in_double_quote = False
            else:
                word += char
        elif in_single_quote:
            if char == "'":
                in_single_quote = False
            else:
                word += char
        else:
            if char == '"':
                in_double_quote = True
            elif char == "'":
                in_single_quote = True
            elif char == "\\" and i + 1 < length:
                word += user_input[i + 1]
                i += 1
            elif char == " ":
                if word:
                    args.append(word)
                    word = ""
            else:
                word += char
        i += 1

    if word:
        args.append(word)

    command = args[0] if args else ""

    return command, args[1:]


def handle_command_exec(command: str, args: list[str]):
    if get_exec_path(command):
        output = subprocess.run([command] + args, capture_output=True, text=True)
        if output.stderr:
            sys.stderr.write(output.stderr)
        if output.stdout:
            sys.stdout.write(output.stdout)
        
        return True

    return False

def handle_type(command: str) -> str:
    if command in COMMANDS:
        return f"{command} is a shell builtin \n"
    
    if cmd_path := get_exec_path(command):
        return f"{command} is {cmd_path} \n"

    return f"{command}: not found \n"

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
        command_result = ""

        match command:
            case "exit":
                break
            case "echo":
                command_result = f"{" ".join(args)}\n"
            case "type":
                command_result = handle_type(args[0])
            case "pwd":
                command_result = f"{os.getcwd()} \n"
            case "cd":
                if dir_not_found := handle_cd(args[0]):
                    command_result = f"{dir_not_found} \n"
            case _:
                if not handle_command_exec(command, args):
                    command_result = f"{command}: command not found \n"
        
        sys.stdout.write(command_result)


if __name__ == "__main__":
    main()
