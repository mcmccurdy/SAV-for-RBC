"""3D rendering of nsb3d.edp output (.vtu files written with -vtk N).
usage: python3 render3d.py run.txt_100250.vtu [out.png] [--amp=0.35 | --level=0.12] [--field=anomaly|T --iso=0.35,0.65] [--res=1600x1200] [--crop=1]
Shows isosurfaces of the temperature anomaly (T minus its horizontal mean at each height) at +-amp*max|anomaly|: hot
rising fluid (red) and cold sinking fluid (blue); with --field=T, isosurfaces of T itself. Below the box, the
temperature on the mid-plane y = H/2 drawn as a floor underneath the box. y is the vertical direction.
--crop=1 trims the white margin (as for the images of Figure 10, rendered with --res=1800x1350).
Needs pyvista (pip install pyvista). Works off screen (no display needed)."""
import sys, numpy as np, pyvista as pv

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
f = args[0]; out = args[1] if len(args) > 1 else f.rsplit('.', 1)[0] + '_3d.png'
lo, hi = (float(v) for v in opts.get('iso', '0.35,0.65').split(','))
W, H = (int(v) for v in opts.get('res', '1600x1200').split('x'))
pv.OFF_SCREEN = True

m = pv.read(f)
if 'T' not in m.point_data:            # files written with cell (P0) data: average to the vertices
    m = m.cell_data_to_point_data()
x0, x1, y0, y1, z0, z1 = m.bounds
Lx, Hy, Lz = x1 - x0, y1 - y0, z1 - z0
# resample the P1 data on a finer uniform grid (smoother isosurfaces), then contour
nx, ny, nz = 4*int(round(Lx/Hy*24)) + 1, 4*24 + 1, 4*int(round(Lz/Hy*24)) + 1
g = pv.ImageData(dimensions=(nx, ny, nz), spacing=(Lx/(nx - 1), Hy/(ny - 1), Lz/(nz - 1)), origin=(x0, y0, z0))
g = g.sample(m)
T = g['T']
# temperature anomaly: T minus its horizontal mean at each height (hot rising / cold sinking fluid)
Ta = T.reshape(nz, ny, nx); Ta = Ta - Ta.mean(axis=(0, 2), keepdims=True); g['Ta'] = Ta.ravel()
amp = float(opts['level']) if 'level' in opts else float(opts.get('amp', 0.35))*float(np.abs(Ta).max())   # --level: absolute
field = opts.get('field', 'anomaly')
if field == 'anomaly': lo, hi, sc = -amp, amp, 'Ta'
else: sc = 'T'
cold = g.contour([lo], scalars=sc).smooth_taubin(n_iter=40, pass_band=0.1)
hot = g.contour([hi], scalars=sc).smooth_taubin(n_iter=40, pass_band=0.1)

# mid-plane temperature as a floor below the box
mid = g.slice(normal='y', origin=(x0 + Lx/2, y0 + Hy/2, z0 + Lz/2))
floor = mid.copy(); floor.points[:, 1] = y0 - 0.35*Hy

p = pv.Plotter(off_screen=True, window_size=(W, H))
p.set_background('white')
cmap = 'RdBu_r'
p.add_mesh(floor, scalars='T', cmap=cmap, clim=(0, 1), show_scalar_bar=False, lighting=False)
if cold.n_points: p.add_mesh(cold, color='#327CB7', smooth_shading=True, specular=0.4, specular_power=20, opacity=0.95)
if hot.n_points: p.add_mesh(hot, color='#C43B3C', smooth_shading=True, specular=0.4, specular_power=20, opacity=0.95)
box = pv.Box(bounds=(x0, x1, y0, y1, z0, z1))
p.add_mesh(box, style='wireframe', color='#444444', line_width=1.5)
# thin translucent bottom (hot) and top (cold) walls
p.add_mesh(pv.Plane(center=(x0 + Lx/2, y0, z0 + Lz/2), direction=(0, 1, 0), i_size=Lx, j_size=Lz), color='#e8b4a8', opacity=0.35)
p.add_mesh(pv.Plane(center=(x0 + Lx/2, y1, z0 + Lz/2), direction=(0, 1, 0), i_size=Lx, j_size=Lz), color='#a8c0e0', opacity=0.18)
p.camera_position = [(x0 + 1.9*Lx, y0 + 2.2*Hy + 0.55*max(Lx, Lz), z0 + 2.3*Lz), (x0 + Lx/2, y0 + 0.15*Hy, z0 + Lz/2), (0, 1, 0)]
p.camera.zoom(1.15)
p.enable_anti_aliasing('ssaa')
p.screenshot(out)
if opts.get('crop', '0') == '1':                  # trim the white margin: bounding box of the non-white pixels
    from PIL import Image, ImageChops
    im = Image.open(out).convert('RGB')
    im.crop(ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()).save(out)
print('wrote', out, '| T range', float(T.min()), float(T.max()), '| iso levels', lo, hi, '| iso points', cold.n_points, hot.n_points)
