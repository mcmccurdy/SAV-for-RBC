"""Colors shared by every line plot of the paper (not the temperature and velocity fields).

Series in a plot take the colors in ORDER; quantities that recur across figures keep one color:
the weight C (C = 100, the recommended value: blue; C = 1: red; C = 10^4: gold),
the wall Nusselt number (red) against the volume average (blue), and exact or published reference values (black).
The three-dimensional figures (3d/fig_caseA.py, fig_caseB.py) use the same blue, red and grey.
"""
BLUE = '#1f5fa8'
RED = '#c8553d'
GOLD = '#d99a1e'
PURPLE = '#7b5aa6'
TEAL = '#2a9d8f'
INK = '#555555'   # secondary lines (e.g. the stored Q)
REF = 'k'         # exact solutions, fits and published values
ORDER = [BLUE, RED, GOLD, PURPLE, TEAL]
C_COLOR = {1: RED, 100: BLUE, '1e4': GOLD, 10000: GOLD}
