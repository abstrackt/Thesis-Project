from src.meshing import boundary_layer_vmr
from src.viewers import view_surface

boundary_layer_vmr("output/constricted_centerdist.vtp", "./output/constricted_adaptive.stl")

view_surface("./output/constricted_adaptive.stl")
