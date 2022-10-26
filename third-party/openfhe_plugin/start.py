def set_openfhe_subparser(subparsers):
    parser = subparsers.add_parser("openfhe", description="enter an integer")
    parser.add_argument("ARG", help="enter an integer")
    parser.set_defaults(fn=FIZZBUZZ)

def FIZZBUZZ(args) -> None:
    val = int(args.ARG)
    print("hello")
    if val % 15 == 0:
        print("FizzBuzz")
    elif val % 3 == 0:
        print("Fizz")
    elif val % 5 == 0:
        print("Buzz")
    else:
        print(val)