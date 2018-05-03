from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import *
from graph import *
from canvas import *
import random
import pickle
import re

class Window:
    '''
    Class for main window to view and edit graph from DictGraph class.
    self.g - DictGraph object
    self.canvas - object of class GraphCanvas

    Methods beginning with _ make some tkinter gui widgets.
    view_popup is auxiliary method that makes popup bindings work.
    clear_all clears all.
    set_color takes as parameters some color variables and buttons which manage them. It is called by lambdas bound to buttons and works with default colours.
    item_color_configure works with vertices, outlines, ribs and weight texts. It's cool. It's called by popups.
    get_vertex and get_rib are efficient methods that use canvas methods to find nearest element.
    find_vertex is inefficient method for some things that don't want to work correct other way.
    create_graph and edit_graph are functions that create editing frame and turn on special binding mode. finish_function returns this back.
    add_vertices_mode and add_ribs_mode make different canvas reactions on click.
    set_vertex and set_rib interact with window default variables and DictGraph object simultaneously.
    delete_rib_by_id and delete_vertex_by_name are called by popup_deleting or cancel function.
    cancel function implemented using stack.
    popup_deleting finds vertex or rib from event and calls some delete function.
    name_check, vertex_bindings and rib_bindings are auxiliary functions.
    save and download use pickle module.
    move_vertex_start and move_vertex_stop just move vertex. Nothing unusual.
    change_vertex_by_popup is used by lambda functions bound to popups and calls some function from rename_complete and resize_complete for vertices. All this metods is needed for widgets management and they call other methods to change graph. There are some functional programming here.
    reweigh_rib_by_event calls reweigh_complete which calls reweigh_rib. There are no functional programming here.
    rename_vertex, resize_vertex and reweigh_rib interact only with DictGraph object and GraphCanvas object and no other widgets or intern variables.
    random_graph makes top level window with options and start_command does   other work for creating and viewing random graph.

    '''
    def __init__(self, g = None):
        self.root = Tk()
        self.g = g

        self.default_col_v_fill = StringVar()
        self.default_col_v_outline = StringVar()
        self.default_col_r = StringVar()
        self.default_col_weight = StringVar()
        self.default_v_size = IntVar()
        self.width = IntVar()
        self.height = IntVar()

        self.directed = IntVar()
        self.multigraph = IntVar()
        self.weighted = IntVar()
        self.directed.set(1)
        self.multigraph.set(1)
        self.weighted.set(1)
        # self.creating = 0
        self.names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.next_name = None

        self.next = None
        self.cancel_stack = []
        self.event = None

        self.ask_vers = IntVar()
        self.ask_ribs = IntVar()
        self.entry = None

        self._make_widgets()
        mainloop()

    def _make_widgets(self):
        self._make_menu()

        self._make_top_frame()
        self._make_create_frame()

        # self.canvas_frame = Frame(self.root)
        # self.canvas_frame.grid(row = 2, column = 0)
        self.canvas = GraphCanvas(self.root, width=600, height=400, scrollregion=(0, 0, 600, 400)) ##
        self.canvas.grid(row = 1, column = 0, sticky=N+S+E+W)
        self.y_scrollbar = Scrollbar(self.root, command = self.canvas.yview, orient=VERTICAL)
        self.x_scrollbar = Scrollbar(self.root, command = self.canvas.xview, orient=HORIZONTAL)
        self.canvas.configure(yscrollcommand = self.y_scrollbar.set, xscrollcommand = self.x_scrollbar.set)

        self.y_scrollbar.grid(row = 1, column = 1,  columnspan=1,  sticky='ns')
        self.x_scrollbar.grid(row = 2, column = 0,  columnspan=1,  sticky='ew')

        self.root.rowconfigure(1, weight = 1)
        self.root.columnconfigure(0, weight = 1)

        if self.g:
            self.canvas.view_graph(self.g)

        self._make_vertex_popup()
        self._make_rib_popup()

    def _make_menu(self):
        self.menubar = Menu(self.root)

        self.file_menu = Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label='new graph', command=self.create_graph)
        self.file_menu.add_command(label='new random graph', command=self.random_graph)
        self.file_menu.add_command(label='open', command=self.download)
        self.file_menu.add_command(label='save as', command=self.save)
        self.menubar.add_cascade(label='file', menu=self.file_menu)

        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.edit_menu.add_command(label = 'clear all', command = self.clear_all)
        self.edit_menu.add_command(label='edit graph', command = self.edit_graph)
        self.menubar.add_cascade(label='edit', menu=self.edit_menu)

        self.root.config(menu=self.menubar)

    def _make_top_frame(self):
        self.top_frame = Frame(self.root)
        self.top_frame.grid(row=0, column=0, sticky=(W))

        self._make_buttons_frame()
        self._make_properties_frame()
        self._make_configure_frame()

    def _make_buttons_frame(self):
        self.buttons_frame = Frame(self.top_frame)
        self.buttons_frame.grid(row=0, column=0)
        self.create_button = Button(self.buttons_frame, text='create graph', command=self.create_graph)
        self.create_button.grid(row=0, column=0)
        self.random_button = Button(self.buttons_frame, text='random graph', command=self.random_graph)
        self.random_button.grid(row=0, column=1)
        self.save_button = Button(self.buttons_frame, text='save', command=self.save)
        self.save_button.grid(row=0, column=2)
        self.download_button = Button(self.buttons_frame, text='download', command=self.download)
        self.download_button.grid(row=0, column=3)

    def _make_properties_frame(self):
        self.properties_frame = Frame(self.top_frame, height=20)
        self.properties_frame.grid(row=0, column=1)
        self.directed_check = Checkbutton(self.properties_frame, variable=self.directed, text='directed')
        self.weighted_check = Checkbutton(self.properties_frame, variable=self.weighted, text='weighted')
        self.multigraph_check = Checkbutton(self.properties_frame, variable=self.multigraph, text='multigraph')
        self.directed_check.grid(row=0, column=0)
        self.weighted_check.grid(row=0, column=1)
        self.multigraph_check.grid(row=0, column=2)

    def _make_configure_frame(self):
        self.configure_frame = Frame(self.top_frame)
        self.configure_frame.grid(row=1, column=0, sticky='wn')

        c1 = random_color()
        c2 = random_color()
        self.default_col_v_fill.set(c1)
        self.default_col_v_outline.set(c2)
        self.default_col_r.set(c2)
        self.default_col_weight.set(c1)
        self.default_v_size.set(20)
        self.width.set(600)
        self.height.set(400)

        self.vertex_icon = Canvas(self.configure_frame, width=20, height=20)
        self.vertex_icon.create_oval(2, 2, 20, 20)
        self.vertex_icon.create_text(11, 11, text='A')
        self.vertex_icon.grid(row=0, column=0)
        self.vertex_size_entry = Entry(self.configure_frame, textvariable=self.default_v_size, width=3)
        self.vertex_size_entry.grid(row=0, column=1)
        self.vertex_color_button = Canvas(self.configure_frame, width=20, height=20, bg=self.default_col_v_fill.get())
        self.outline_color_button = Canvas(self.configure_frame, width=20, height=20,
                                           bg=self.default_col_v_outline.get())
        self.vertex_color_button.grid(row=0, column=2)
        self.outline_color_button.grid(row=0, column=3)
        self.rib_icon = Canvas(self.configure_frame, width=20, height=20)
        self.rib_icon.create_line(0, 20, 20, 0, arrow=LAST)
        self.rib_icon.grid(row=0, column=4)
        self.rib_color_button = Canvas(self.configure_frame, width=20, height=20, bg=self.default_col_r.get())
        self.weight_color_button = Canvas(self.configure_frame, width=20, height=20, bg=self.default_col_weight.get())
        self.rib_color_button.grid(row=0, column=5)
        self.weight_color_button.grid(row=0, column=6)

        self.width_entry = Entry(self.configure_frame, textvariable = self.width, width = 5)
        self.height_entry = Entry(self.configure_frame, textvariable=self.height, width = 5)
        self.width_entry.grid(row = 0, column = 7)
        self.height_entry.grid(row = 0, column = 8)

        self.vertex_color_button.bind('<Button-1>',
                                      lambda ev: self.set_color(self.default_col_v_fill, self.vertex_color_button))
        self.outline_color_button.bind('<Button-1>',
                                       lambda ev: self.set_color(self.default_col_v_outline, self.outline_color_button))
        self.rib_color_button.bind('<Button-1>', lambda ev: self.set_color(self.default_col_r, self.rib_color_button))
        self.weight_color_button.bind('<Button-1>',
                                      lambda ev: self.set_color(self.default_col_weight, self.weight_color_button))
        self.width_entry.bind('<Return>', lambda ev: self.canvas.configure(width = self.width.get(), scrollregion = (0, 0, self.width.get(), self.height.get())))
        self.height_entry.bind('<Return>', lambda ev: self.canvas.configure(height=self.height.get(), scrollregion = (0, 0, self.width.get(), self.height.get())))

    def _make_create_frame(self):
        self.create_frame = Frame(self.top_frame)
        # self.create_frame.grid(row=1, column=1, sticky='wn')
        self.add_vertices_button = Button(self.create_frame, text = 'add vertices', command = self.add_vertices_mode)
        self.add_vertices_button.grid(row = 0, column = 0)
        self.add_ribs_button = Button(self.create_frame, text = 'add ribs', command = self.add_ribs_mode)
        self.add_ribs_button.grid(row = 0, column = 1)
        self.cancel_button = Button(self.create_frame, text='cancel', state=DISABLED, command = self.cancel)
        self.cancel_button.grid(row = 0, column = 2)
        self.complete_button = Button(self.create_frame, text = 'complete', command = self.finish_function)
        self.complete_button.grid(row = 0, column = 3)

    def _make_vertex_popup(self):
        self.vertex_popup_menu = Menu(self.root, tearoff=0)
        self.vertex_popup_menu.add_command(label='delete', command = lambda: self.popup_deleting(self.get_vertex, self.delete_vertex_by_name))
        self.vertex_popup_menu.add_command(label='rename', command = lambda: self.change_vertex_by_popup(StringVar(), self.rename_complete)) #self.rename_vertex)
        self.vertex_popup_menu.add_command(label = 'resize', command = lambda: self.change_vertex_by_popup(IntVar(), self.resize_complete, self.g.ver_sizes))
        self.vertex_popup_menu.add_command(label='colour', command = lambda: self.item_color_configure(self.get_vertex, self.g.ver_colours, 0))
        self.vertex_popup_menu.add_command(label='outline colour', command = lambda: self.item_color_configure(self.get_vertex, self.g.ver_colours, 1))

    def _make_rib_popup(self):
        self.rib_popup_menu = Menu(self.root, tearoff=0)
        self.rib_popup_menu.add_command(label='delete', command = lambda: self.popup_deleting(self.get_rib, self.delete_rib_by_id))
        self.rib_popup_menu.add_command(label='re-weigh', command=self.reweigh_rib_by_event)
        self.rib_popup_menu.add_command(label='colour', command = lambda: self.item_color_configure(self.get_rib, self.g.rib_colours))
        self.rib_popup_menu.add_command(label='weight colour', command = lambda: self.item_color_configure(self.get_rib, self.g.weight_colours))

    def view_popup(self, ev, popup_menu):
        self.event = ev
        popup_menu.post(ev.x_root, ev.y_root)

    def clear_all(self):
        self.g = None
        self.canvas.delete('all')

    def set_color(self, variable, button):
        col = askcolor()
        if col[1]:
            variable.set(col[1])
            button.configure(bg = variable.get())

    def item_color_configure(self, find_function, graph_colours_dict, index = -1):
        n = find_function(self.event)
        self.event = None
        col = askcolor()[1]
        if col:
            if index != -1:
                cort = list(graph_colours_dict.get(n))
                cort[index] = col
                graph_colours_dict[n] = tuple(cort)
                self.canvas.view_vertex(self.g, n)
            else:
                graph_colours_dict[n] = col
                self.canvas.view_rib(self.g, n)
                self.canvas.view_rib_weight(self.g, n)

    def find_vertex(self, ev, size = 0): #####
        if not size:
            size = self.default_v_size.get()
        n = 0
        for name, coor in self.g.form.items():
            x, y = coor[0], coor[1]
            if x - size <= ev.x <= x + size and y - size <= ev.y <= y + size:
                n = name
                break
        return n

    def get_vertex(self, ev):
        tag = self.canvas.gettags(self.canvas.find_closest(ev.x, ev.y))[0]
        if 'rib' in tag or 'weight' in tag:
            return 0
        return tag

    def get_rib(self, ev):
        tag = self.canvas.gettags(self.canvas.find_closest(ev.x, ev.y))[0]
        # tag = self.canvas.gettags(ev.widget.find_withtag("current"))[0]
        i = int(tag[3:])
        return i

    def create_graph(self):
        self.canvas.delete('all')
        self.g = DictGraph()
        self.g.directed, self.g.weighted, self.g.multigraph = self.directed.get(), self.weighted.get(), self.multigraph.get()

        self.create_frame.grid(row=1, column=1, sticky='wn')

        self.next_name = (name for name in self.names)
        self.add_vertices_mode()

    def edit_graph(self):
        if self.g:
            self.create_frame.grid(row=1, column=1, sticky='wn')

            self.next_name = (name for name in [e for e in self.names if e not in self.g.vertices.keys()])
            self.add_vertices_mode()
        else:
            alert = Toplevel()
            message = Message(alert, width = 200, text = 'You have no any graph opened. Please, create or download some graph.')
            button = Button(alert, text = 'ok', command = lambda: alert.destroy())
            message.grid(row = 0, column = 0)
            button.grid(row = 1, column = 0)
            alert.bind('<Return>', lambda ev: alert.destroy())
            alert.focus()

    def add_vertices_mode(self):
        self.add_vertices_button.configure(relief=SUNKEN)
        self.add_ribs_button.configure(relief=RAISED)
        self.canvas.bind('<Button-1>', self.set_vertex)
        for e in self.g.vertices.keys():
            self.vertex_bindings(e)
            self.canvas.tag_bind(e, '<Button-1>', lambda ev: None)

    def add_ribs_mode(self):
        self.add_vertices_button.configure(relief=RAISED)
        self.add_ribs_button.configure(relief=SUNKEN)
        self.next = None
        self.canvas.bind('<Button-1>', lambda ev: None)
        for e in self.g.vertices.keys():
            self.canvas.tag_bind(e, '<B1-Motion>', self.set_rib)
            self.canvas.tag_bind(e, '<Button-1>', self.set_rib)

    def cancel(self):
        if self.cancel_stack:
            el = self.cancel_stack.pop()
            if type(el) is int:
                self.delete_rib_by_id(el)
            if type(el) is str:
                self.delete_vertex_by_name(el)
        if not self.cancel_stack:
            self.cancel_button.configure(state = DISABLED)

    def set_vertex(self, ev):
        if not self.find_vertex(ev):
            try:
                name = next(self.next_name)
                self.g.set_vertices(name)
                x = ev.x
                y = ev.y
                self.g.form[name] = (x, y)
                self.g.ver_sizes[name] = self.default_v_size.get()
                self.g.ver_colours[name] = (self.default_col_v_fill.get(), self.default_col_v_outline.get())
                self.canvas.view_vertex(self.g, name)
                self.vertex_bindings(name)
                if not self.cancel_stack:
                    self.cancel_button.configure(state=NORMAL)
                self.cancel_stack.append(name)
            except:
                alert = Toplevel()
                message = Message(alert, text = 'You used the whole alphabet. Try to rename some vertices.', width = 400)
                button = Button(alert, text = 'ok',  command = lambda: alert.destroy())
                message.grid(row=0, column=0)
                button.grid(row=1, column=0)
                alert.bind('<Return>', lambda ev: alert.destroy())
                alert.focus()

    def set_rib(self, ev):
        n = self.find_vertex(ev)
        if n:
            if self.next and self.next != n:
                if self.g.multigraph or self.g.get_ribs(self.next, n) == []:
                    dir = set()
                    if self.g.directed:
                        dir = {n}
                    i = self.g.set_rib(self.next, n, dir = dir) # w ???
                    self.g.rib_colours[i] = self.default_col_r.get()
                    self.g.weight_colours[i] = self.default_col_weight.get()
                    self.canvas.view_rib(self.g, i)
                    if self.g.weighted:
                        self.canvas.view_rib_weight(self.g, i)

                    self.rib_bindings(i)
                    if not self.cancel_stack:
                        self.cancel_button.configure(state=NORMAL)
                    self.cancel_stack.append(i)
                    self.next = None
            else:
                self.next = n

    def finish_function(self):
        self.create_frame.grid_remove()
        self.cancel_stack = []
        self.cancel_button.configure(state=DISABLED)
        self.canvas.bind('<Button-1>', lambda ev: None)
        for e in self.g.vertices.keys():
            self.vertex_bindings(e)
            self.canvas.tag_bind(e, '<Button-1>', lambda ev: None)
        self.next_name = None

    def name_check(self):
        if self.next_name:
            self.next_name = (name for name in [e for e in self.names if e not in self.g.vertices.keys()])

    def random_graph(self):
        self.ask = Toplevel()
        self.ask_vers.set(random.choice(range(4,8)))
        if self.multigraph.get():
            self.ask_ribs.set(random.choice(range(8,12)))
        else:
            self.ask_ribs.set(random.choice(range(4, 8)))

        Label(self.ask, text = 'vertices').grid(row = 0, column = 0)
        Label(self.ask, text = 'ribs').grid(row = 1, column = 0)
        ver = Entry(self.ask, textvariable = self.ask_vers)
        ver.grid(row = 0, column = 1)
        rib = Entry(self.ask, textvariable = self.ask_ribs)
        rib.grid(row = 1, column = 1)
        ok_b = Button(self.ask, text = 'ok', command = self.start_command)
        ok_b.grid(row = 3, column = 0, columnspan = 2)
        self.ask.bind('<Return>', self.start_command)
        self.ask.focus()
    def start_command(self):
        self.g = random_graph(self.ask_vers.get(), self.ask_ribs.get(), weighted = self.weighted.get(), directed = self.directed.get(), multigraph = self.multigraph.get())
        c1 = random_color()
        self.default_col_v_fill.set(c1)
        c2 = random_color()
        self.default_col_v_outline.set(c2)
        self.default_col_r.set(c2) ###
        self.default_col_weight.set(c1)

        self.vertex_color_button.configure(bg = self.default_col_v_fill.get())
        self.outline_color_button.configure(bg = self.default_col_v_outline.get())
        self.rib_color_button.configure(bg = self.default_col_r.get())
        self.weight_color_button.configure(bg = self.default_col_weight.get())

        self.g.ver_colours = {e: (c1, c2) for e in self.g.vertices.keys()}
        self.g.rib_colours = {e: c2 for e in self.g.ribs.keys()}
        self.g.weight_colours = {e: c1 for e in self.g.ribs.keys()}

        self.canvas.view_graph(self.g)
        for e in self.g.vertices.keys():
            self.vertex_bindings(e)
        for i in self.g.ribs.keys():
            self.rib_bindings(i)

        self.ask.destroy()

    def vertex_bindings(self, ver):
        self.canvas.tag_bind(ver, '<Button-3>', lambda ev: self.view_popup(ev, self.vertex_popup_menu))
        self.canvas.tag_bind(ver, '<B1-Motion>', self.move_vertex_start)
    def rib_bindings(self, i):
        self.canvas.tag_bind('rib' + str(i), '<Button-3>', lambda ev: self.view_popup(ev, self.rib_popup_menu))
        self.canvas.tag_bind('weight' + str(i), '<Double-Button-1>', self.reweigh_rib_by_event)

    def save(self):
        try:
            filename = asksaveasfilename()
            f = open(filename, 'wb')
            pickle.dump(self.g, f)
        except:
            pass

    def download(self):
        try:
            filename = askopenfilename()
            f = open(filename, 'rb')
            self.g = pickle.load(f)
            self.g.view()
            self.canvas.view_graph(self.g)
        except:
            pass


    def delete_rib_by_id(self, i):
        self.g.del_rib(i)
        self.canvas.delete_rib(i)

    def delete_vertex_by_name(self, name):
        self.canvas.delete_ribs(self.g, name)
        self.canvas.delete_vertex(name)
        self.g.del_vertex(name)
        self.name_check()

    def popup_deleting(self, find_function, delete_function):
        n = find_function(self.event)
        delete_function(n)
        self.event = None


    def move_vertex_start(self, ev):
        if self.next:
            self.canvas.bind('<ButtonRelease-1>', self.move_vertex_stop) ### ??
        else:
            self.next = self.get_vertex(ev)

    def move_vertex_stop(self, ev):
        if self.next and not self.find_vertex(ev, self.g.ver_sizes.get(self.next)):
            ver = self.next
            self.g.form[ver] = (ev.x, ev.y)
            self.canvas.delete_ribs(self.g, ver)
            self.canvas.delete_vertex(ver)
            ribs = self.g.vertices.get(ver)
            for i in ribs:
                self.g.find_points_for_rib(i)
                self.canvas.view_rib(self.g, i)
                self.g.find_text_layout(i)
            if self.g.weighted:
                for i in ribs:
                    self.canvas.view_rib_weight(self.g, i)
            self.canvas.view_vertex(self.g, ver)
            self.next = None
            self.canvas.unbind('<ButtonRelease-1>')


    def change_vertex_by_popup(self, tvar, func, dict = None):
        if self.entry:
            self.entry.destroy()
        ev = self.event
        ver = self.get_vertex(ev)
        if dict:
            tvar.set(dict.get(ver))
        else:
            tvar.set(ver)
        self.entry = Entry(self.canvas, width=4, textvariable = tvar)
        self.entry.grid()
        self.entry.focus()
        x, y = self.g.form.get(ver)[0], self.g.form.get(ver)[1]
        self.canvas.create_window((x, y), window=self.entry)
        self.root.bind('<Return>', lambda ev: func(tvar, ver))
        self.root.bind('<Escape>', lambda ev: self.entry.destroy()) ##keybind update

    def rename_complete(self, tvar, old):
        new = tvar.get()
        if new not in self.g.vertices.keys() and new != '':
            self.rename_vertex(old, new)
            self.entry.destroy()
        if new == old:
            self.entry.destroy()
    def resize_complete(self, tvar, name):
        size = tvar.get()
        if size >= 10 and size <= 100:
            self.resize_vertex(name, size)
            self.entry.destroy()

    def reweigh_rib_by_event(self, ev = 0):
        if self.entry:
            self.entry.destroy()
        if not ev:
            ev = self.event
        i = self.get_rib(ev)
        tvar = IntVar()
        tvar.set(self.g.ribs.get(i)[2])
        self.entry = Entry(self.canvas, width=4, textvariable=tvar)
        self.entry.grid()
        self.entry.focus()
        if self.g.multigraph:
            layout = self.g.rib_text_layout.get(i)[self.g.rib_orientation.get(i)][1]
        else:
            layout = self.g.rib_text_layout_simple.get(i)[self.g.rib_orientation.get(i)][1]
        x, y = layout[0], layout[1]
        self.canvas.create_window((x, y), window=self.entry)
        self.root.bind('<Return>', lambda ev: self.reweigh_complete(tvar, i))
        self.root.bind('<Escape>', lambda ev: self.entry.destroy())
    def reweigh_complete(self, tvar, i):
        weight = tvar.get()
        self.reweigh_rib(i, weight)
        self.entry.destroy()




    def rename_vertex(self, old, new):
        if new not in self.g.vertices.keys():
            self.g.rename_vertex(old, new)
            self.canvas.delete_vertex(old)
            self.canvas.view_vertex(self.g, new)
            self.canvas.tag_bind(new, '<Button-3>', lambda ev: self.view_popup(ev, self.vertex_popup_menu))
            self.canvas.tag_bind(new, '<B1-Motion>', self.move_vertex_start)
            self.name_check()

    def resize_vertex(self, name, size):
        self.g.ver_sizes[name] = size
        self.canvas.delete_vertex(name)
        self.canvas.view_vertex(self.g, name)
        self.canvas.delete_ribs(self.g, name)
        for rib in self.g.vertices.get(name):
            self.g.find_points_for_rib(rib)
            self.g.find_text_layout(rib)
            self.canvas.view_rib(self.g, rib)
            if self.g.weighted:
                self.canvas.view_rib_weight(self.g, rib)
        self.canvas.tag_bind(name, '<Button-3>', lambda ev: self.view_popup(ev, self.vertex_popup_menu))
        self.canvas.tag_bind(name, '<B1-Motion>', self.move_vertex_start)

    def reweigh_rib(self, i, new):
        rib = self.g.ribs.get(i)
        rib[2] = new
        self.canvas.delete_rib_weight(i)
        if self.g.weighted:
            self.canvas.view_rib_weight(self.g, i)



def random_color():
    l = ['00','11','22','33','44','55','66','77','88','99','aa','bb','cc','dd','ee','ff']
    cs = '#'+'00'*3
    while cs == '#000000' or cs == '#ffffff':
        cs = [random.choice(l),random.choice(l),random.choice(l)]
        cs = '#'+cs[0]+cs[1]+cs[2]
    return cs


if __name__ == '__main__':
    root = Window()