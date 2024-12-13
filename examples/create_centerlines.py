from src.centerlines import centerline, centerdist

# centerline("data/healthy.stl", "output/healthy_centerline.vtp")
# centerdist("data/healthy.stl", "output/healthy_centerdist.vtp")

centerline("data/constricted.stl", "output/constricted_centerline.vtp")
centerdist("data/constricted.stl", "output/constricted_centerdist.vtp")