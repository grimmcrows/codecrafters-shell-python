import sys


def main():
    while True:
        match input("$ "):
            case "exit":
                break
            case invalid_command:
                sys.stdout.write(f"{invalid_command}: command not found")
                sys.stdout.write("\n")

if __name__ == "__main__":
    main()
