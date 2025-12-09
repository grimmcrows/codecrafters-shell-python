import sys


def main():
    while True:
        command, *args = input("$ ").split(" ")
        match command:
            case "exit":
                break
            case "echo":
                sys.stdout.write(f"{" ".join(args)}\n")
            case _:
                sys.stdout.write(f"{command}: command not found")
                sys.stdout.write("\n")

if __name__ == "__main__":
    main()
