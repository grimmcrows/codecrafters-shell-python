import sys

COMMANDS = ["exit", "echo", "type"]

def main():
    while True:
        command, *args = input("$ ").split(" ")
        match command:
            case "exit":
                break
            case "echo":
                sys.stdout.write(f"{" ".join(args)}\n")
            case "type":
                if args[0] in COMMANDS:
                    sys.stdout.write(f"{args[0]} is a shell builtin \n")
                else:
                    sys.stdout.write(f"{args[0]}: not found \n")
            case _:
                sys.stdout.write(f"{command}: command not found")
                sys.stdout.write("\n")

if __name__ == "__main__":
    main()
