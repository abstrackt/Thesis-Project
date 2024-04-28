from optparse import OptionParser
from CTMesh.centerlines import centerline

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    parser.add_option('-o', '--output', action='store', dest='output', default='./')
    (options, args) = parser.parse_args()

    if (len(args) != 0 or options.input == ''):
        print("Usage: python centerlines.py -i <input_path> -o <output_path> (default ./)")
        return

    centerline(options.input, options.output)


if __name__ == "__main__":
    main()