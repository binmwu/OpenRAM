import debug
import design
from tech import drc, spice
from vector import vector
from globals import OPTS
import debug
import design
from tech import drc, spice
from vector import vector
from globals import OPTS


class plain_bitcell_array(design.design):
    """
    Creates a rows x cols array of memory cells. Assumes bit-lines
    and word line is connected by abutment.
    Connects the word lines and bit lines.
    """
    def __init__(self, cols, rows, name="bitcell_array"):
        design.design.__init__(self, name)
        debug.info(1, "Creating {0} {1} x {2}".format(self.name, rows, cols))


        self.column_size = cols
        self.row_size = rows

        c = reload(__import__(OPTS.config.bitcell))
        self.mod_bitcell = getattr(c, OPTS.config.bitcell)
        self.cell = self.mod_bitcell()
        self.add_mod(self.cell)

        self.height = self.row_size*self.cell.height 
        self.width = self.column_size*self.cell.width 
        
        self.add_pins()
        self.create_layout()
        self.add_layout_pins()
        self.DRC_LVS()

    def add_pins(self):
        for col in range(self.column_size):
            self.add_pin("bl[{0}]".format(col))
            self.add_pin("br[{0}]".format(col))
        for row in range(self.row_size):
            self.add_pin("wl[{0}]".format(row))
        self.add_pin("vdd")
        self.add_pin("gnd")

    def create_layout(self):
        xoffset = 0.0
        self.cell_inst = {}
        for col in range(self.column_size):
            yoffset = 0.0
            for row in range(self.row_size):
                name = "bit_r{0}_c{1}".format(row, col)

                if row % 2:
                    tempy = yoffset + self.cell.height
                    dir_key = "MX"
                else:
                    tempy = yoffset
                    dir_key = ""

                self.cell_inst[row,col]=self.add_inst(name=name,
                                                      mod=self.cell,
                                                      offset=[xoffset, tempy],
                                                      mirror=dir_key)
                self.connect_inst(["bl[{0}]".format(col),
                                   "br[{0}]".format(col),
                                   "wl[{0}]".format(row),
                                   "vdd",
                                   "gnd"])
                yoffset += self.cell.height
            xoffset += self.cell.width


    def add_layout_pins(self):
        
        # Our cells have multiple gnd pins for now.
        # FIXME: fix for multiple vdd too
        vdd_pin = self.cell.get_pin("vdd")

        # shift it up by the overlap amount (gnd_pin) too
        # must find the lower gnd pin to determine this overlap
        lower_y = self.cell.height
        gnd_pins = self.cell.get_pins("gnd")
        for gnd_pin in gnd_pins:
            if gnd_pin.layer=="metal2" and gnd_pin.by()<lower_y:
                lower_y=gnd_pin.by()

        # lower_y is negative, so subtract off double this amount for each pair of
        # overlapping cells
        full_height = self.height - 2*lower_y
        
        vdd_pin = self.cell.get_pin("vdd")
        lower_x = vdd_pin.lx()
        # lower_x is negative, so subtract off double this amount for each pair of
        # overlapping cells
        full_width = self.width - 2*lower_x
        
        offset = vector(0.0, 0.0)
        for col in range(self.column_size):
            # get the pin of the lower row cell and make it the full width
            bl_pin = self.cell_inst[0,col].get_pin("BL")
            br_pin = self.cell_inst[0,col].get_pin("BR")
            self.add_layout_pin(text="bl[{0}]".format(col),
                                layer="metal2",
                                offset=bl_pin.ll(),
                                width=bl_pin.width(),
                                height=full_height)
            self.add_layout_pin(text="br[{0}]".format(col),
                                layer="metal2",
                                offset=br_pin.ll(),
                                width=br_pin.width(),
                                height=full_height)

            # gnd offset is 0 in our cell, but it be non-zero
            gnd_pins = self.cell_inst[0,col].get_pins("gnd")
            for gnd_pin in gnd_pins:
                # avoid duplicates by only doing even rows
                # also skip if it is not the full height (a through rail)
                if gnd_pin.layer=="metal2" and col%2 == 0 and gnd_pin.height()>=self.cell.height:
                    self.add_layout_pin(text="gnd", 
                                        layer="metal2",
                                        offset=gnd_pin.ll(),
                                        width=gnd_pin.width(),
                                        height=full_height)
                    
            # increments to the next column width
            offset.x += self.cell.width

        offset.x = 0.0
        for row in range(self.row_size):
            wl_pin = self.cell_inst[row,0].get_pin("WL")
            vdd_pins = self.cell_inst[row,0].get_pins("vdd")
            gnd_pins = self.cell_inst[row,0].get_pins("gnd")

            for gnd_pin in gnd_pins:
                if gnd_pin.layer=="metal1":
                    self.add_layout_pin(text="gnd", 
                                        layer="metal1",
                                        offset=gnd_pin.ll(),
                                        width=full_width,
                                        height=drc["minwidth_metal1"])
                
            # add vdd label and offset
            # only add to even rows to avoid duplicates
            for vdd_pin in vdd_pins:
                if row % 2 == 0 and vdd_pin.layer=="metal1":
                    self.add_layout_pin(text="vdd",
                                        layer="metal1",
                                        offset=vdd_pin.ll(),
                                        width=full_width,
                                        height=drc["minwidth_metal1"])
                
            # add wl label and offset
            self.add_layout_pin(text="wl[{0}]".format(row),
                                layer="metal1",
                                offset=wl_pin.ll(),
                                width=full_width,
                                height=wl_pin.height())

            # increments to the next row height
            offset.y += self.cell.height

    def analytical_delay(self, slew, load=0):
        from tech import drc
        wl_wire = self.gen_wl_wire()
        wl_wire.return_delay_over_wire(slew)

        wl_to_cell_delay = wl_wire.return_delay_over_wire(slew)
        # hypothetical delay from cell to bl end without sense amp
        bl_wire = self.gen_bl_wire()
        cell_load = 2 * bl_wire.return_input_cap() # we ingore the wire r
                                                   # hence just use the whole c
        bl_swing = 0.1
        cell_delay = self.cell.analytical_delay(wl_to_cell_delay.slew, cell_load, swing = bl_swing)

        #we do not consider the delay over the wire for now
        return self.return_delay(cell_delay.delay+wl_to_cell_delay.delay,
                                 wl_to_cell_delay.slew)

    def gen_wl_wire(self):
        wl_wire = self.generate_rc_net(int(self.column_size), self.width, drc["minwidth_metal1"])
        wl_wire.wire_c = 2*spice["min_tx_gate_c"] + wl_wire.wire_c # 2 access tx gate per cell
        return wl_wire

    def gen_bl_wire(self):
        bl_pos = 0
        bl_wire = self.generate_rc_net(int(self.row_size-bl_pos), self.height, drc["minwidth_metal1"])
        bl_wire.wire_c =spice["min_tx_drain_c"] + bl_wire.wire_c # 1 access tx d/s per cell
        return bl_wire

    def output_load(self, bl_pos=0):
        bl_wire = self.gen_bl_wire()
        return bl_wire.wire_c # sense amp only need to charge small portion of the bl
                              # set as one segment for now

    def input_load(self):
        wl_wire = self.gen_wl_wire()
        return wl_wire.return_input_cap()

class bitcell_array(plain_bitcell_array):
    """
    Creates a rows x cols array of memory cells. Assumes bit-lines
    and word line is connected by abutment.
    Connects the word lines and bit lines.
    """

    def __init__(self, name, cols, rows, create_layout = True):
        self.column_size = cols
        self.row_size = rows
        if create_layout == True:
            self = plain_bitcell_array.__init__(self, name, cols, rows, create_layout = create_layout)
        else:
            plain_bitcell_array.__init__(self, name, cols, rows, create_layout = create_layout)
            self.vdd_positions = []
            self.gnd_positions = []
            self.WL_positions = []
            self.BL_positions = []
            self.BR_positions = []
            self.sub_array = []



    def add_pins(self):
        for col in range(self.column_size):
            self.add_pin("bl[{0}]".format(col))
            self.add_pin("br[{0}]".format(col))
        for row in range(self.row_size):
            self.add_pin("wl[{0}]".format(row))
        self.add_pin("vdd")
        self.add_pin("gnd")
        

    def arrange_array(self, gap, routing_space):
        # check the gap list is long enough
        assert len(self.sub_array)-1<=len(gap)
        x_offset = 0
        start_column_index = 0
        self.row_positions = []
        for index in range(len(self.sub_array)):
            array_to_add =  self.sub_array[index]     
            self.add_mod(array_to_add)
            self.add_inst(name="sub_array"+str(index),
                          mod=array_to_add,
                          offset=[x_offset, 0])

            for i in range(array_to_add.column_size):
               row_pos = vector(x_offset + self.bitcell_chars["width"] * i,
                                0)
               self.row_positions.append(row_pos)

            for i in range(len(array_to_add.BL_positions)):
                offset = array_to_add.BL_positions[i] +vector(x_offset, 0)
                self.BL_positions.append(offset)
                self.add_label(text="BL{0}".format(i+start_column_index),
                               layer="metal2",
                               offset=offset)

                offset = array_to_add.BR_positions[i] +vector(x_offset, 0)
                self.BR_positions.append(offset)
                self.add_label(text="BR{0}".format(i+start_column_index),
                               layer="metal2",
                               offset=offset)
            for gnd in array_to_add.gnd_positions:
                self.gnd_positions.append(gnd+vector(x_offset,0))

            temp = []
            for i in range(array_to_add.column_size):
                temp.append("bl[{0}]".format(i+start_column_index))
                temp.append("br[{0}]".format(i+start_column_index))
            for j in range(array_to_add.row_size):
                temp.append("wl[{0}]".format(j))
            temp = temp + [ "vdd", "gnd"]
            self.connect_inst(temp)
            start_column_index = array_to_add.column_size + start_column_index
            if index != len(self.sub_array) - 1: 
                x_offset = x_offset + array_to_add.width + gap[index]
        self.add_vdd_and_label(array_to_add, vector(x_offset,0))
        self.add_h_gnd_and_label(array_to_add, vector(x_offset,0))
        self.add_wl_and_label(array_to_add, vector(x_offset,0), routing_space)

        self.width = x_offset + array_to_add.width
        self.height = array_to_add.height 

    def add_wl_and_label(self, array_to_add, base, routing_space):
        self.WL_path = []
        for wl in array_to_add.WL_positions:
            start = wl.scale(0,1)
            end = start + base
            self.WL_positions.append(start)
            self.WL_path.append([start, end])
            self.add_path(layer="metal1", coordinates = [end, 
                                                         end-vector(routing_space, 0)])


    def add_wl_connection(self):
        # not necessarily called, build for testing purpose
        for wl in self.WL_path:
            start, end = wl
            self.add_wire(layers=("metal1", "via1","metal2"),
                          coordinates = [start, end])

    def add_vdd_and_label(self, array_to_add, base):
        self.vdd_positions =[]
        for vdd in array_to_add.vdd_positions:
            end = vdd + base
            self.add_path(layer="metal1", 
                          coordinates = [vdd, end])
            self.add_label(text="vdd",
                           layer="metal1",
                           offset=vdd)
            self.vdd_positions.append(vdd)

    def add_h_gnd_and_label(self, array_to_add, base):
        for gnd in array_to_add.h_gnd_positions:
            start = gnd.scale(0,1) 
            end = base + start
            self.add_path(layer="metal1", 
                          coordinates = [start, end])
            self.add_label(text="gnd",
                           layer="metal1",
                           offset=start)

    def gen_sub_arrays(self, sub_array_size):
        for index in range(len(sub_array_size)):      
            array_size = sub_array_size[index]
            sub_array = plain_bitcell_array("sub_array"+str(index), 
                                            cols = array_size, 
                                            rows=self.row_size)   
            self.sub_array.append(sub_array)  

    def get_sub_array_width(self): 
        assert len(self.sub_array)!=0
        width_lst = []
        for sub_array in self.sub_array:
            width_lst.append(sub_array.width)
        return width_lst

    def get_row_positions(self):
        if hasattr(self,"row_positions"):
            return self.row_positions
        else:
            result = []
            for i in range(self.column_size):
                 result.append(vector(self.bitcell_chars["width"] * i,
                                      0))
            return result
