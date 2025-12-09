import sys


def main():
    while True:
        sys.stdout.write("$ ")

        if command := input():
            sys.stdout.write(f"{command}: command not found")
            sys.stdout.write("\n")

if __name__ == "__main__":
    main()
