import gmsh
import sys
import math
from optparse import OptionParser

def generate_3d_mesh(in_path):
    gmsh.initialize(sys.argv)

    gmsh.merge(in_path)
    gmsh.model.mesh.classifySurfaces(math.pi, True, True)
    gmsh.model.mesh.createGeometry()

    gmsh.option.setNumber('Geometry.ExtrudeReturnLateralEntities', 0)

    gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), [4], [1.0], True)

    e = gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), [4], [-1.0], True, True)

    top_ent = [s for s in e if s[0] == 2]
    top_surf = [s[1] for s in top_ent]

    gmsh.model.geo.synchronize()
    bnd_ent = gmsh.model.getBoundary(top_ent)
    bnd_curv = [c[1] for c in bnd_ent]

    loops = gmsh.model.geo.addCurveLoops(bnd_curv)
    for l in loops:
        top_surf.append(gmsh.model.geo.addPlaneSurface([l]))

    gmsh.model.geo.addVolume([gmsh.model.geo.addSurfaceLoop(top_surf)])
    gmsh.model.geo.synchronize()

    gmsh.option.setNumber('Mesh.Algorithm', 1)
    gmsh.option.setNumber('Mesh.MeshSizeFactor', 0.1)

    if '-nopopup' not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    (options, args) = parser.parse_args()
    
    if (len(args) != 0 or options.input == ''):
        print("Usage: python meshing.py -i <input_path>")
        return
    
    generate_3d_mesh(options.input)
              
if __name__ == "__main__":
    main()