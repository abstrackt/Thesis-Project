from optparse import OptionParser
from CTMesh.meshing import export_3d

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    (options, args) = parser.parse_args()

    if (len(args) != 0 or options.input == ''):
        print("Usage: python meshing.py -i <input_path>")
        return

    export_3d(options.input)


if __name__ == "__main__":
    main()