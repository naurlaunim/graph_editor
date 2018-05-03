from math import sqrt, atan2, degrees


class Graph():
    def is_tree(self):
        pass

    def is_oil(self):
        pass

    def set_vertices(self, *args):
        pass

    def set_rib(self, *args):
        pass

    def del_vertex(self, *args):
        pass

    def del_rib(self, *args):
        pass


class DictGraph(Graph):
    '''

    This class is one of different implementations of graph which uses python dictionaries. Other implementations wasn't include in this module (matrix graph and so forth).
    DictGraph object stores information about graph.
    Vertices store in dict self.vertices and have string name as a key and rib indexes array as a value.
    Ribs store in dict self.ribs and have int index as a key. Value is a list that contains two vertices, weight and set of directions which contains vertex names.
    self.form is dict with x and y coordinates for each vertex. self.sizes stores roughly vertex radius. (half the diagonal of the square into which the circle is inscribed, to be more precise)
    self.ver_colours stores two colours for each vertex as a tuple and self.rib_colours, self.weight_colours store separately colours for ribs. Colours are stored in hex.
    Other dictionaries are auxiliary.

    set_vertices function allow arbitrary quantity of string names and creates such vertices. Nothing returns.
    set_rib need two string vertex names as required parameters. Int weight and set dir are optional parameters. It returns rib index.
    set_form requires lists or tuples with two int elements for x and y coordinates. Number of args must correspond to the number of vertices of this graph.
    del_rib and del_vertex need int index or string name accordingly.
    rename_vertex require two string parameters one of them is existing vertex and other isn't.
    get_ribs returns int list for all rib indexes between two vertices.
    view prints information about graph, without some things about visual display on canvas.
    find_points_for_rib and find_text_layout are auxiliary functions for correct positioning ribs have on the canvas.

    '''

    def __init__(self, *args):
        self.vertices = {e: [] for e in args} #
        self.ribs = {}  # {1: ['a', 'b', w, dir], 2: [], ...} # {{'a', 'b'}: [[5,{}], [6,{'b'}]}
        self.form = {}
        self.ver_colours = {e: ('white', 'black') for e in args}
        self.ver_sizes = {e: 20 for e in args}
        self.rib_colours = {}
        self.weight_colours = {}
        self.rib_points = {}
        self.rib_points_simple = {}
        self.rib_orientation = {}
        self.rib_text_layout = {}
        self.rib_text_layout_simple = {}
        self.next_rib = 1

        self.directed = 0
        self.weighted = 0
        self.multigraph = 0

    def set_form(self, *args):
        assert len(args) == len(self.vertices)
        x = [e for e in self.vertices.keys()]
        x.sort()
        self.form = {x[i]: args[i] for i in range(len(x))}

    def set_vertices(self, *args):
        for n in args:
            assert self.vertices.get(n) == None, 'name is already used'
            self.vertices[n] = []

    def set_rib(self, a, b, w=1, dir=set()):
        i = self.next_rib
        self.next_rib += 1
        self.ribs[i] = [a, b, w, dir]
        x = self.vertices.get(a)
        y = self.vertices.get(b)
        x.append(i)
        y.append(i)

        if self.form:
            self.find_points_for_rib(i)
            self.find_text_layout(i)
        return i

    def del_rib(self, i):
        assert self.ribs.get(i), 'no such rib'
        a = self.ribs.get(i)[0]
        b = self.ribs.get(i)[1]
        x = self.vertices.get(a)
        y = self.vertices.get(b)
        x.remove(i)
        y.remove(i)
        for dict in [self.rib_colours, self.rib_points, self.rib_orientation, self.rib_text_layout, self.ribs]:
            del dict[i]

    def del_vertex(self, a):
        x = self.vertices.get(a).copy()
        for n in x:
            self.del_rib(n)
        for dict in [self.form, self.ver_sizes, self.ver_colours, self.vertices]:
            del dict[a]

    def rename_vertex(self, old, new):
        for i in self.vertices.get(old):  # edit ribs
            rib = self.ribs.get(i)
            rib[rib.index(old)] = new
            if old in rib[3]:
                rib[3].remove(old)
                rib[3].add(new)
        for dict in [self.form, self.ver_sizes, self.ver_colours, self.vertices]:
            dict[new] = dict.get(old)
            del dict[old]

    def get_ribs(self, a, b):
        x = self.vertices.get(a)
        y = self.vertices.get(b)
        z = [i for i in x if i in y]
        return z

    def view(self):
        l = [k for k in self.vertices.keys()]
        l.sort()
        for k in l:
            print(*[[self.ribs.get(i), i, self.rib_orientation.get(i)] for i in self.vertices.get(k)], sep = '\n')
        print()

    def find_points_for_rib(self, i):
        a, b = self.ribs.get(i)[0], self.ribs.get(i)[1]
        family = self.get_ribs(a, b)
        if a < b:
            self.rib_orientation[i]= family.index(i) % 2
        else:
            self.rib_orientation[i] = (family.index(i)+1) % 2
        level = family.index(i) // 2
        # fsort = sorted([([neighbour]+self.ribs.get(neighbour)) for neighbour in family if family.index(neighbour) % 2 == ori], key = lambda e: e[3])

        k = [100,20,8,4][level]
        rib = self.ribs.get(i)
        a, b = rib[0], rib[1]
        arrow1, arrow2 = 0, 0
        if a in rib[3]:
            arrow1 = 1
        if b in rib[3]:
            arrow2 = 1
        a_size, b_size = self.ver_sizes.get(a), self.ver_sizes.get(b)
        a_coor, b_coor = self.form.get(a), self.form.get(b)
        # distance between b and any of two points on round which size is a_size (and the same about b):
        a_inclination = distance(*a_coor, *b_coor) - a_size + distance(*a_coor, *b_coor)/200
        b_inclination = distance(*a_coor, *b_coor) - b_size + distance(*a_coor, *b_coor)/200
        a_epsilon = find_points(*a_coor, a_size, *b_coor, a_inclination + a_size/4 * level * arrow1) # a_epsilon0 and a_epsilon1 - two opposite points on the a-vertex circle
        b_epsilon = find_points(*a_coor, b_inclination + b_size/4 * level * arrow2, *b_coor, b_size) # b_epsilon0 and b_epsilon1
        ac_bc = distance(*a_coor, *b_coor)/2 + distance(*a_coor, *b_coor)/k # ac distance either equals bc, ad and bd

        c_d = find_points(*a_coor, ac_bc, *b_coor, ac_bc) # two opposite points c and d

        self.rib_points[i] = list(zip(a_epsilon, c_d, b_epsilon))

        # for a non-multigraph
        a_epsilon = find_points(*a_coor, a_size, *b_coor, distance(*a_coor, *b_coor) - a_size +1)
        b_epsilon = find_points(*a_coor, distance(*a_coor, *b_coor) - b_size + 1, *b_coor, b_size)
        ac_bc = distance(*a_coor, *b_coor) / 2
        c_d = find_points(*a_coor, ac_bc +1, *b_coor, ac_bc+1)
        xs = []

        for points in [a_epsilon, c_d, b_epsilon]:
            x = (points[0][0]+points[1][0])/2
            y = (points[0][1]+points[1][1])/2
            xs.append([x, y])
        self.rib_points_simple[i] =  xs

    def find_text_layout(self, i):
        rib = self.ribs.get(i)
        a, b = rib[0], rib[1]
        points = self.rib_points.get(i)
        c_d = [points[0][1], points[1][1]]
        a_coor, b_coor = self.form.get(a), self.form.get(b)
        centre = [(a_coor[0]+b_coor[0])/2, (a_coor[1]+b_coor[1])/2] # set the center of coordinates between two vertices
        vectors = [[e[0]-centre[0], -(e[1]- centre[1])] for e in c_d] # find direction in math sence from pixel coordinates
        angles = [degrees(atan2(*e[::-1])) for e in vectors] # angles with Ox

        textpoints = [[(e[0]+centre[0])/2, (e[1]+centre[1])/2] for e in c_d]
        textpoints2 = [[e[0], e[1]] for e in [self.rib_points_simple.get(i)[1]]*2] # for a non-multigraph
        ##
        self.rib_text_layout[i] = list(zip(angles, textpoints))
        self.rib_text_layout_simple[i] = list(zip(angles, textpoints2)) # for a non-multigraph





def find_points(x1, y1, r1, x2, y2, r2):
    vv = (x1 - x2) ** 2 + (y1 - y2) ** 2
    a = (r1 + r2) * (r1 - r2) / 2 / vv + 0.5
    b = sqrt(r1 ** 2 / vv - a ** 2)
    p1x = x1 + a * (x2 - x1) - b * (y2 - y1)
    p1y = y1 + a * (y2 - y1) + b * (x2 - x1)
    p2x = x1 + a * (x2 - x1) + b * (y2 - y1)
    p2y = y1 + a * (y2 - y1) - b * (x2 - x1)
    return [p1x, p1y], [p2x, p2y]

def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)

def random_graph(v, r, weighted = 1, directed = 1, multigraph = 1):
    import random
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
             'V', 'W', 'X', 'Y', 'Z'][:v]

    form = []
    while True:
        test = 0
        x = random.choice(range(30, 570))
        y = random.choice(range(30, 370))
        for e in form:
            if e[0] - 20 < x < e[0] + 20 or e[1] - 20 < y < e[1] + 20:
                test = 1
        if test:
            continue
        form.append((x, y))
        if len(form) == v:
            break

    ribs = []
    # i = 1
    j = 6
    w, d = 1, set()
    while True:
        a = random.choice(names)
        b = random.choice(names)
        if a != b:
            if multigraph or ([a, b] not in ribs and [b, a] not in ribs):
                ribs.append([a, b])

        if len(ribs) == r:
            break
    for rib in ribs:
        if weighted:
            w = random.choice(range(j-5, j+5))
            j += 5
        rib.append(w)
        if directed:
            d = set(random.choice([rib[0], rib[1]]))
        rib.append(d)

    g = DictGraph(*(names))
    g.directed, g.weighted, g.multigraph = directed, weighted, multigraph
    g.set_form(*form)
    for e in ribs:
        g.set_rib(*e)

    return g


if __name__ == '__main__':
    g = DictGraph('a', 'b', 'c')
    g.set_rib('a', 'b', dir = {'a', 'b'}, w = 2)
    g.set_rib('a', 'b', 3, {'a'})
    g.set_rib('a', 'c', 4, {'a'})
    g.view()


