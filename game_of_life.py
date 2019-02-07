from collections import defaultdict
import turtle
import re


pop = set()

CELL_SIZE = 3
WIDTH = 1280
HEIGHT = 1280
MAXX = WIDTH / (2 * CELL_SIZE)
MAXY = HEIGHT / (2 * CELL_SIZE)
MINX = -MAXX
MINY = -MAXY
FPS = 60


def neigh(x, y):
    for deltax in [-1, 0, 1]:
        for deltay in [-1, 0, 1]:
            if deltax != 0 or deltay != 0:
                yield x + deltax, y + deltay


def click_handler(cx, cy):
    x, y = cx // CELL_SIZE, cy // CELL_SIZE
    print(x, y)
    toggle_cell(x, y)


pause = True


def do_iterate_handler():
    if pause:
        iterate()


def auto_handler():
    global pause
    pause = not pause
    while not pause:
        iterate()
        import time
        time.sleep(1/FPS)


def print_grid():
    minX = min(x for x, y in pop)
    minY = min(y for x, y in pop)
    maxX = max(x for x, y in pop)
    maxY = max(y for x, y in pop)
    print(maxX - minX + 1, maxY - minY + 1)
    for y in range(maxY, minY - 1, -1):
        for x in range(minX, maxX + 1):
            if (x, y) in pop:
                print(1, end='')
            else:
                print(0, end='')
        print()


def add_cell(x, y):
    if (x, y) not in pop:
        pop.add((x, y))
        draw_cell(x, y)


def remove_cell(x, y):
    if (x, y) in pop:
        pop.remove((x, y))
        undraw_cell(x, y)


def toggle_cell(x, y):
    if (x, y) in pop:
        pop.remove((x, y))
        undraw_cell(x, y)
    else:
        pop.add((x, y))
        draw_cell(x, y)


iteration = 0


def iterate():
    global iteration
    iteration += 1
    print('Iteration', iteration)
    t.clear()
    neighcount = defaultdict(int)
    for x, y in pop:
        for nx, ny in neigh(x, y):
            neighcount[(nx, ny)] += 1
    nextpop = set()
    for c, v in neighcount.items():
        if v != 2 and v != 3: 
            continue
        if v == 3:
            nextpop.add(c)
        if v == 2 and c in pop:
            nextpop.add(c)
    pop.clear()
    for c in nextpop:
        add_cell(*c)
    draw()


screen = turtle.Screen()
screen.setup(width=WIDTH, height=HEIGHT)
screen.title('Game of life')
screen_x, screen_y = screen.screensize()
screen.onclick(click_handler)
screen.onkey(do_iterate_handler, 'n')
screen.onkey(auto_handler, 'a')
screen.onkey(print_grid, 's')
screen.listen()
turtle.tracer(0, 0)
t = turtle.Turtle(visible=False)
t.pensize(1)
t.penup()
t.ht()


def draw_cell_color(x, y, col):
    if x < MINX or x > MAXX:
        return
    if y < MINY or y > MAXY:
        return
    cx = x * CELL_SIZE
    cy = y * CELL_SIZE
    t.color(col)
    t.setpos(cx, cy)
    t.pendown()
    t.begin_fill()
    t.setpos(cx + CELL_SIZE - 1, cy)
    t.setpos(cx + CELL_SIZE - 1, cy + CELL_SIZE - 1)
    t.setpos(cx, cy + CELL_SIZE - 1)
    t.setpos(cx, cy)
    t.end_fill()
    t.penup()


def draw_cell(x, y):
    draw_cell_color(x, y, 'black') 


def undraw_cell(x, y):
    draw_cell_color(x, y, 'white') 


def draw():
    turtle.update()


def _plain_text_desc(x, y, filename, symx, symy, rot):
    with open(filename, 'r') as f:
        line = f.readline()
        width, height = (int(x) for x in line.split())
        binx, biny = int(symx), int(symy)

        def coords(i, j):
            ci, cj = (1 - 2 * binx) * i + binx * (width - 1), \
                   (1 - 2 * biny) * j + biny * (height - 1)
            if rot == 0:
                return x + ci, y - cj
            else:
                return x + (height - 1 - cj), y - ci

        for j, line in enumerate(f):
            for i, c in enumerate(line[:-1]):
                if c == '1':
                    add_cell(*coords(i, j))
                else:
                    remove_cell(*coords(i, j))
    
    
def _rle_desc(x, y, filename, symx, symy, rot):
    with open(filename, 'r') as f:

        width = None
        height = None
        binx, biny = int(symx), int(symy)

        def coords(i, j):
            ci, cj = (1 - 2 * binx) * i + binx * (width - 1), \
                   (1 - 2 * biny) * j + biny * (height - 1)
            if rot == 0:
                return x + ci, y - cj
            else:
                return x + (height - 1 - cj), y - ci

        i = 0
        j = 0
        value = 0
        for line in f:
            line = line.strip()
            if line[0] == '#':
                continue
            if width is None:
                m = re.match('x = (\d+), y = (\d+)', line)
                if m is None:
                    continue
                width = int(m.group(1))
                height = int(m.group(2))
            else:
                for c in line:
                    if c == '$':
                        if value == 0:
                            value = 1
                        j += value
                        i = 0
                        value = 0
                    elif c == '!':
                        return
                    elif c in ('o', 'b'):
                        if value == 0:
                            value = 1
                        fun = remove_cell if c == 'b' else add_cell
                        for k in range(i, i + value):
                            fun(*coords(k, j))
                        i += value
                        value = 0
                    elif c == '\n':
                        continue
                    else:
                        value = value * 10 + int(c)


def _cpx_desc(x, y, filename, symx, symy, rot):
    with open(filename, 'r') as f:
        line = f.readline()
        width, height = (int(x) for x in line.split())
        binx, biny = int(symx), int(symy)

        def coords(i, j):
            ci, cj = (1 - 2 * binx) * i + binx * (width - 1), \
                     (1 - 2 * biny) * j + biny * (height - 1)
            if rot == 0:
                return x + ci, y - cj
            else:
                return x + (height - 1 - cj), y - ci

        for line in f:
            m = re.match('(-?\d+) (-?\d+) (.+) (True|False) (True|False) (-?\d+)', line)
            if m is not None:
                i1 = int(m.group(1))
                j1 = -int(m.group(2))
                x1, y1 = coords(i1, j1)

                filename1 = m.group(3)
                symx1 = m.group(4) == 'True'
                symy1 = m.group(5) == 'True'
                rot1 = int(m.group(6))
                add_file(x1, y1, filename1, (symx and not symx1) or (not symx and symx1),
                         (symy and not symy1) or (not symy and symy1), rot1)


def add_file(x, y, filename, symx=False, symy=False, rot=0):
    '''Lit le fichier filename (format plaintext ou rle) et dessine le contenu aux coordonnées indiquées. Si symx est
    vrai, effectue une symétrie axiale par rapport à l'horizontal. Si symy est vrai, par rapport à la verticale. Enfin
    rot gère la rotation: une rotation d'angle rot * pi / 4 est effectuée. Le rotation est effectuée après les
    symétries.'''

    print(x, y, filename, symx, symy, rot)
    while rot >= 2:
        rot -= 2
        symx = not symx
        symy = not symy
    while rot < 0:
        rot += 2
        symx = not symx
        symy = not symy

    if filename.endswith('rle'):
        _rle_desc(x, y, filename, symx, symy, rot)
    elif filename.endswith('cpx'):
        _cpx_desc(x, y, filename, symx, symy, rot)
    else:
        _plain_text_desc(x, y, filename, symx, symy, rot)


def add_glider_to_duplicator_1(xdupp, ydupp, dist):
    '''Ajoute un planneur en supposant qu'un dupplicateur de planeur (glider_dupplicator_1) a été ajouté aux
    coordonnées xdupp et ydupp. dist correspond à une "distance" au dupplicateur. dist = 0 signifie qu'on place le
    planneur le plus proche possible, dist = 1 est le 2e plus proche possible, ...'''
    add_file(xdupp + 11 - 30 * dist, ydupp - 20 + 30 * dist, 'glider.rle')


if __name__ == '__main__':
    # add_file(0, 0, 'others/glider_to_lwss.cpx')
    add_file(0, 0, 'guns/gliderlwssgun.cpx')
    draw()
    screen.mainloop()
