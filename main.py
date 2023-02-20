import argparse

def read_file(name):


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'The 8-puzzle',
        description = 'Solves an 8-puzzle using various algorithms')

    parser.add_argument('--fPath')
    parser.add_argument('--alg')

    args = parser.parse_args()

    print(args.fPath, args.alg)
