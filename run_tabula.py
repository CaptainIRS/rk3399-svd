left = 38
top = 45
width = 515
height = 753

y1 = top
x1 = left
y2 = top + height
x2 = left + width

import tabula
import sys

if __name__ == '__main__':
    part = sys.argv[1]
    tabula.convert_into(f"part{part}.pdf", f"part{part}.csv", output_format="csv", pages='all', lattice=True, area=(y1, x1, y2, x2))