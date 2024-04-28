from optparse import OptionParser
from CTMesh.meshing import export_stl
from CTMesh.segmentation import segment_refine


def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    parser.add_option('-o', '--output', action='store', dest='output', default='./')
    parser.add_option('-c', '--class', action='append', dest='seg_class')
    parser.add_option('-x', '--flipx', action='store_true', default=False, dest='fx')
    parser.add_option('-y', '--flipy', action='store_true', default=False, dest='fy')
    parser.add_option('-z', '--flipz', action='store_true', default=False, dest='fz')
    (options, args) = parser.parse_args()

    if len(args) != 0 or options.input == '' or len(options.seg_class) == 0:
        print("Usage: python meshing.py -i <input_path> -o <output_path> (default ./) -c <class_1> -c <class_2>...")
        return

    print(options.fx)

    segment_refine(options.input, options.seg_class, options.fx, options.fy, options.fz)

    print("Preprocessing finished, now exporting mesh");

    export_stl(options.input, options.output)


if __name__ == "__main__":
    main()