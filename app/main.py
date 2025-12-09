import sys


def main():
    while True:
        command = input("$ ")
        
        if command == "exit":
            break
        else:
            sys.stdout.write(f"{command}: command not found")
            sys.stdout.write("\n")

if __name__ == "__main__":
    main()
