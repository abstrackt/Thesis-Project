from src.centerlines import centerline, centerdist, metrics, branched

centerline("data/healthy.stl", "output/healthy_centerline.vtp")
centerdist("data/healthy.stl", "output/healthy_centerdist.vtp")
branched("data/healthy.stl", "output/healthy_centerline.vtp", "output/healthy_branched.vtp")
metrics("output/healthy_branched.vtp", "output/healthy_centerline.vtp", "output/healthy_metrics.vtp")

# centerline("data/constricted.stl", "output/constricted_centerline.vtp")
# centerdist("data/constricted.stl", "output/constricted_centerdist.vtp")