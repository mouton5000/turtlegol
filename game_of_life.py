from collections import defaultdict
import turtle
import re


pop = set()

CELL_SIZE = 5
WIDTH = 1280
HEIGHT = 1280
MAXX = WIDTH / (2 * CELL_SIZE)
MAXY = HEIGHT / (2 * CELL_SIZE)
MINX = -MAXX
MINY = -MAXY


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
        iterate_draw()


def auto_handler():
    global pause
    pause = not pause
    while not pause:
        iterate_draw()
        

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


def iterate_draw():
    global iteration
    t.clear()
    print('Iteration', iteration)
    iteration += 1
    nextpop = iterate(pop)
    pop.clear()
    for c in nextpop:
        add_cell(*c)
    draw()


def iterate(coords):
    neighcount = defaultdict(int)
    for x, y in coords:
        for nx, ny in neigh(x, y):
            neighcount[(nx, ny)] += 1
    nextpop = set()
    for c, v in neighcount.items():
        if v != 2 and v != 3: 
            continue
        if v == 3:
            nextpop.add(c)
        if v == 2 and c in coords:
            nextpop.add(c)
    return nextpop


screen = turtle.Screen()
screen.setup(width=WIDTH, height=HEIGHT)
screen.title('Game of life')
screen_x, screen_y = screen.screensize()
screen.onclick(click_handler)
screen.onkey(do_iterate_handler, 'n')
screen.onkey(auto_handler, 'a')
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


def _plain_text_desc(x, y, filename):
    coords = []
    anticoords = []
    with open(filename, 'r') as f:

        for j, line in enumerate(f):
            for i, c in enumerate(line[:-1]):
                if c == '1':
                    coords.append((x + i, y - j))
                else:
                    anticoords.append((x + i, y - j))
    return coords, anticoords

    
def _rle_desc(x, y, filename):
    coords = []
    anticoords = []
    with open(filename, 'r') as f:
        i = 0
        j = 0
        value = 0
        for line in f:
            line = line.strip()
            if line[0] == '#':
                continue
            if re.match('x = (\d+), y = (\d+)', line):
                continue

            for c in line:
                if c == '$':
                    if value == 0:
                        value = 1
                    j += value
                    i = 0
                    value = 0
                elif c == '!':
                    return coords, anticoords
                elif c in ('o', 'b'):
                    if value == 0:
                        value = 1
                    l = anticoords if c == 'b' else coords
                    for k in range(i, i + value):
                        l.append((x + k, y - j))
                    i += value
                    value = 0
                elif c == '\n':
                    continue
                else:
                    value = value * 10 + int(c)


def _cpx_desc(x, y, filename):
    coords = []
    anticoords = []

    minx = 0
    maxy = 0

    with open(filename, 'r') as f:
        for line in f:
            m = re.match('(-?\d+) (-?\d+) (.+) (True|False) (True|False) (-?\d+) (\d+)', line)
            if m is not None:
                x1 = int(m.group(1))
                y1 = int(m.group(2))
                minx = min(minx, x1)
                maxy = max(maxy, y1)

                filename1 = m.group(3)
                coords1, anticoords1 = _get_desc(x + x1, y + y1, filename1)

                symx1 = m.group(4) == 'True'
                symy1 = m.group(5) == 'True'
                rot1 = int(m.group(6))
                time = int(m.group(7))

                coords1, anticoords1 = _transform(coords1, anticoords1, symx1, symy1, rot1, time)

                coords += coords1
                anticoords += anticoords1

    coords = [(i - minx, j - maxy) for i, j in coords]
    anticoords = [(i - minx, j - maxy) for i, j in anticoords]
    return coords, anticoords


def _transform(coords, anticoords, symx, symy, rot, time):

    if len(coords) == 0:
        if len(anticoords) == 0:
            return coords, anticoords
        else:
            xmin = xmax = anticoords[0][0]
            ymin = ymax = anticoords[0][1]
    else:
        xmin = xmax = coords[0][0]
        ymin = ymax = coords[0][1]

    for i, j in coords:
        xmin = min(i, xmin)
        xmax = max(i, xmax)
        ymin = min(j, ymin)
        ymax = max(j, ymax)

    for i, j in anticoords:
        xmin = min(i, xmin)
        xmax = max(i, xmax)
        ymin = min(j, ymin)
        ymax = max(j, ymax)

    for t in range(time):
        coords = iterate(coords)

    for i, j in coords:
        xmin = min(i, xmin)
        xmax = max(i, xmax)
        ymin = min(j, ymin)
        ymax = max(j, ymax)

    del anticoords[:]
    for i in range(xmin, xmax+1):
        for j in range(ymin, ymax+1):
            if (i, j) not in coords:
                anticoords.append((i, j))

    width = xmax - xmin + 1
    height = ymax - ymin + 1

    while rot >= 2:
        rot -= 2
        symx = not symx
        symy = not symy
    while rot < 0:
        rot += 2
        symx = not symx
        symy = not symy

    binx, biny = int(symx), int(symy)

    def transform_coords(i, j):
        ci, cj = (1 - 2 * binx) * i + binx * (width - 1), \
               (1 - 2 * biny) * j + biny * (height - 1)
        if rot == 0:
            return xmin + ci, ymax - cj
        else:
            # return xmin + (height - 1 - cj), ymax - ci
            return xmin + cj, ymax - (width - 1 - ci)
    coords = [transform_coords(i - xmin, ymax - j) for i, j in coords]
    anticoords = [transform_coords(i - xmin, ymax - j) for i, j in anticoords]
    return coords, anticoords


def _get_desc(x, y, filename):
    if filename.endswith('rle'):
        return _rle_desc(x, y, filename)
    elif filename.endswith('cpx'):
        return _cpx_desc(x, y, filename)
    else:
        return _plain_text_desc(x, y, filename)


def add_file(x, y, filename, symx=False, symy=False, rot=0, time=0):
    '''Lit le fichier filename (format plaintext ou rle) et dessine le contenu aux coordonnées indiquées. Si symx est
    vrai, effectue une symétrie axiale par rapport à l'axe vertical. Si symy est vrai, par rapport à l'axe horizontal.
    Enfin rot gère la rotation: une rotation d'angle rot * pi / 2 est effectuée. Le rotation est effectuée après les
    symétries.'''

    coords, anticoords = _get_desc(x, y, filename)
    coords, anticoords = _transform(coords, anticoords, symx, symy, rot, time)


    for i, j in coords:
        add_cell(i, j)
    for i, j in anticoords:
        remove_cell(i, j)


def add_glider_to_duplicator_1(xdupp, ydupp, dist):
    '''Ajoute un planneur en supposant qu'un dupplicateur de planeur (glider_dupplicator_1) a été ajouté aux
    coordonnées xdupp et ydupp. dist correspond à une "distance" au dupplicateur. dist = 0 signifie qu'on place le
    planneur le plus proche possible, dist = 1 est le 2e plus proche possible, ...'''
    add_file(xdupp + 11 - 30 * dist, ydupp - 20 + 30 * dist, 'glider.rle')


if __name__ == '__main__':
    add_file(-50, 50, 'guns/lwssgun')
    add_file(-50, -50, 'guns/p46gliderlesslwssgun.rle')

    # add_file(0, 50, 'others/lwssgun_with_eater.cpx')
    # add_file(-49, 3, 'others/lwssgun_with_eater.cpx', symy=True, time=2)
    # add_file(74, 25, 'spaceships/glider', rot=2)
    draw()
    screen.mainloop()
