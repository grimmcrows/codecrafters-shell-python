import sys
import os
import subprocess
import readline
from pathlib import Path

COMMANDS = ["exit", "echo", "type", "pwd", "cd"]

def get_exec_path(command: str) -> Path:
    os_bin_paths = os.environ["PATH"].split(os.pathsep)

    for path in os_bin_paths:
        cmd_path = Path(path) / command
        if cmd_path.exists() and os.access(cmd_path, os.X_OK):
            return cmd_path
        
def get_all_exec_in_path() -> list[str]:
    os_bin_paths = os.environ["PATH"].split(os.pathsep)
    execs = []
    for path in os_bin_paths:
        try:
            for file in Path(path).iterdir():
                if file.is_file() and os.access(file, os.X_OK):
                    execs.append(file.name)
        except FileNotFoundError:
            continue
            
    return execs

                
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


def handle_command_exec(command: str, args: list[str]) -> list[tuple[bool, str]]:
    if get_exec_path(command):
        results = []
        output = subprocess.run([command] + args, capture_output=True, text=True)
        if output.stderr:
            results.append((False, output.stderr))
        if output.stdout:
            results.append((True, output.stdout))
        
        return results

    return [(False, f"{command}: command not found \n")]

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

def handle_output_redirect(user_command: list[str]) -> tuple[list[str], str|None, str]:
    pre_output = []
    output_file = None
    operation_type = 'stdout'
    found_output_redirect = False
    for command in user_command:
        if command in (">", "1>"):
            found_output_redirect = True
            continue
        
        if command in (">>", "1>>"):
            found_output_redirect = True
            operation_type = "append_stdout"
            continue

        if command in ("2>>"):
            found_output_redirect = True
            operation_type = "append_stderr"
            continue

        if command in ("2>"):
            found_output_redirect = True
            operation_type = 'errout'
            continue

        if found_output_redirect:
            output_file = command
        else:
            pre_output.append(command)

    return pre_output, output_file, operation_type

def redirect_to_output_file(result: str, output_file: str, optype: str) -> None:
    if optype not in ("append_stdout", "append_stderr"):
        if os.path.isfile(output_file):
            os.remove(output_file)

        with open(output_file, "x") as file:
            if result:
                file.write(result)
        return
    
    with open(output_file, "a") as file:
            if result:
                file.write(result)

def completer(text, state):
    path_and_custom = COMMANDS + get_all_exec_in_path()
    matches = [cmd + " " for cmd in path_and_custom if cmd.startswith(text)]

    if state < len(matches):
        return matches[state]
    
    return None

readline.set_completer(completer)

# Handle both GNU readline and libedit (macOS)
if readline.__doc__ and 'libedit' in readline.__doc__:
    readline.parse_and_bind('bind ^I rl_complete')
else:
    readline.parse_and_bind('tab: complete')

def main():
    while True:
        user_input = input("$ ")
        command, args = format_input(user_input)
        args, output_file, output_redirect_type = handle_output_redirect(args)

        command_result = None
        command_result_err = None

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
                    command_result_err = f"{dir_not_found} \n"
            case _:
                results = handle_command_exec(command, args)

                for (is_success, result) in results:
                    if not is_success:
                        command_result_err = result
                        continue

                    command_result = result

        
        if output_file is None:
            sys.stdout.write(command_result or "")
            sys.stderr.write(command_result_err or "")
            continue

        if output_redirect_type in ("stdout", "append_stdout") and command_result_err:
            sys.stderr.write(command_result_err)
            command_result_err = None

        if output_redirect_type in ("errout", "append_stderr") and command_result:
            sys.stdout.write(command_result)
            command_result = None

        redirect_to_output_file(command_result or command_result_err, output_file, output_redirect_type)


if __name__ == "__main__":
    main()
