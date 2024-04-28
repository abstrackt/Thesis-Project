import os
from optparse import OptionParser
from CTMesh.segmentation import segment

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    parser.add_option('-o', '--output', action='store', dest='output', default='./')
    (options, args) = parser.parse_args()

    if (len(args) != 0 or options.input == ''):
        print("Usage: python segmentation.py -i <input_path> -o <output_path> (default ./)")
        return

    segment(options.input, os.path.join(options.output, "segmentation/"))


if __name__ == "__main__":
    main()