from tkinter import *


class GraphCanvas(Canvas):
    '''
    GraphCanvas is special Canvas to display the graph in tkinter.
    It uses data about the vertices and ribs from the object of class DictGraph.

    Functions view_vertex, view_rib, view_rib_weight and delete_ribs need two parameters: the DictGraph object and vertex name or rib index.
    Functions delete_vertex, delete_rib, delete_rib_weight need only the identifier of vertex/rib.
    view_graph function uses one parameter - DictGraph object.

    '''
    def __init__(self, master, *args, **kwargs):
        Canvas.__init__(self, master, *args, **kwargs)

    def view_vertex(self, g, name):
        x, y = g.form.get(name)[0], g.form.get(name)[1]
        fill, outline = g.ver_colours.get(name)[0], g.ver_colours.get(name)[1]
        size = g.ver_sizes.get(name)
        self.create_oval(x-size, y-size, x+size, y+size, width = 3, fill = fill, outline = outline, tag = name)
        self.create_text(x, y, text = name, fill = outline, tag = name)

    def view_rib(self, g, i, col = 'black'):
        rib = g.ribs.get(i)
        fill = g.rib_colours.get(i)
        if not fill:
            fill = col
        arrow = None
        if g.directed:
            arrowset = rib[3]
            if len(arrowset) == 2:
                arrow = BOTH
            elif rib[0] in arrowset:
                arrow = FIRST
            elif rib[1] in arrowset:
                arrow = LAST

        if g.multigraph:
            points = g.rib_points.get(i)[g.rib_orientation.get(i)]
        else:
            points = g.rib_points_simple.get(i)
        self.create_line(*points, smooth='true', splinesteps=15, arrow=arrow, width = 3, fill = fill, tag = 'rib'+str(i))

    def view_rib_weight(self, g, i):
        rib = g.ribs.get(i)
        fill = g.weight_colours.get(i)
        if g.multigraph:
            layout = g.rib_text_layout.get(i)[g.rib_orientation.get(i)]
        else:
            layout = g.rib_text_layout_simple.get(i)[g.rib_orientation.get(i)]
        if layout[0] < 0:
            angle = layout[0] + 90
        else:
            angle = layout[0] - 90
        self.create_text(layout[1], text = rib[2], angle = angle, tags = ['rib'+str(i), 'weight'+str(i)], font = ('TkDefaultFont', 11), fill = fill)

    def view_graph(self, g):
        self.delete('all')
        for e in g.vertices.keys():
            self.view_vertex(g, e)
        for e in g.ribs.keys():
            self.view_rib(g, e)
        if g.weighted:
            for e in g.ribs.keys():
                self.view_rib_weight(g, e)

    def delete_vertex(self, name):
        self.delete(name)

    def delete_rib(self, i):
        self.delete('rib'+str(i))

    def delete_ribs(self, g, ver1):
        l = g.vertices.get(ver1)
        for i in l:
            self.delete('rib'+str(i))

    def delete_rib_weight(self, i):
        self.delete('weight'+str(i))



if __name__ == '__main__':
    root = Tk()
    canv = GraphCanvas(root, width = 600, height = 600)
    canv.pack()
    import graph
    g = graph.DictGraph('a', 'b', 'c', 'd')
    g.set_form([100,100], [500,100], [400,500], [500, 400])

    g.set_rib('a', 'b', 5, {'b'})
    g.set_rib('c', 'a', 3, {'a'})
    g.set_rib('c', 'a', 2, {'a'})
    g.set_rib('c', 'a', 8, {'c'})
    g.set_rib('c', 'a', 16, {'c'})
    g.set_rib('c', 'a', 20, {'a'})
    g.set_rib('c', 'a', 19, {'c'})
    g.set_rib('c', 'a', 25, {'a'})
    g.set_rib('c', 'a', 16, {'c'})
    for i in range(1,5):
        g.set_rib('c', 'd', i, {'d'})
    canv.view_graph(g)
    canv.delete_rib(3)



    root.mainloop()