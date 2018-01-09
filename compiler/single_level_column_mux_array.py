from math import log
import design
from single_level_column_mux import single_level_column_mux 
import contact
from tech import drc
import debug
import math
from vector import vector


class single_level_column_mux_array(design.design):
    """
    Dynamically generated column mux array.
    Array of column mux to read the bitlines through the 6T.
    """

<<<<<<< HEAD
    def __init__(self, rows, columns, word_size, row_locations = None):
=======
    def __init__(self, columns, word_size):
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd
        design.design.__init__(self, "columnmux_array")
        debug.info(1, "Creating {0}".format(self.name))
        self.columns = columns
        self.word_size = word_size
        self.words_per_row = self.columns / self.word_size
        self.add_pins()
<<<<<<< HEAD
        self.create_layout(row_locations)
        self.offset_all_coordinates()
=======
        self.create_layout()
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd
        self.DRC_LVS()

    def add_pins(self):
        for i in range(self.columns):
            self.add_pin("bl[{}]".format(i))
            self.add_pin("br[{}]".format(i))
        for i in range(self.words_per_row):
            self.add_pin("sel[{}]".format(i))
        for i in range(self.word_size):
            self.add_pin("bl_out[{}]".format(i))
            self.add_pin("br_out[{}]".format(i))
        self.add_pin("gnd")

    def create_layout(self, row_locations):
        self.add_modules()
        self.setup_layout_constants()
        self.create_array(row_locations)
        self.add_routing(row_locations)

    def add_modules(self):
        self.mux = single_level_column_mux(name="single_level_column_mux",
                                           tx_size=8)
        self.add_mod(self.mux)


    def setup_layout_constants(self):
        self.column_addr_size = num_of_inputs = int(self.words_per_row / 2)
        self.width = self.columns * self.mux.width
        
        self.m1_pitch = contact.m1m2.width + max(drc["metal1_to_metal1"],drc["metal2_to_metal2"])
        # To correct the offset between M1 and M2 via enclosures
        self.offset_fix = vector(0,0.5*(drc["minwidth_metal2"]-drc["minwidth_metal1"]))
        # one set of metal1 routes for select signals and a pair to interconnect the mux outputs bl/br
        # one extra route pitch is to space from the sense amp
        self.route_height = (self.words_per_row + 3)*self.m1_pitch
        # mux height plus routing signal height plus well spacing at the top
        self.height = self.mux.height + self.route_height + drc["pwell_to_nwell"]

<<<<<<< HEAD
    def create_array(self, row_locations):
        for i in range(self.columns):
            name = "XMUX{0}".format(i)
            if row_locations == None:
                x_off = vector(i * self.mux.width, 0)
            else:
                x_off = row_locations[i]
            self.add_inst(name=name,
                          mod=self.mux,
                          offset=x_off)

            """ draw a vertical m2 rail to extend BL BR & gnd on top of the cell """
            # FIXME: These are just min metal squares, are they needed?
            self.add_rect(layer="metal2",
                          offset=x_off + self.mux.BL_position,
                          width=drc['minwidth_metal2'],
                          height=drc['minwidth_metal2'])
            self.add_rect(layer="metal2",
                          offset=x_off + self.mux.BR_position,
                          width=drc['minwidth_metal2'],
                          height=drc['minwidth_metal2'])
            self.add_rect(layer="metal2",
                          offset=x_off + self.mux.gnd_position,
                          width=drc['minwidth_metal2'],
                          height=drc['minwidth_metal2'])

            """ add labels for the column_mux array """
            BL = self.mux.BL_position + x_off
            self.BL_positions.append(BL)
            self.add_label(text="bl[{0}]".format(i),
                           layer="metal2",
                           offset=BL)

            BR = self.mux.BR_position + x_off
            self.BR_positions.append(BR)
            self.add_label(text="br[{0}]".format(i),
                           layer="metal2",
                           offset=BR)

            gnd = self.mux.gnd_position + x_off
            self.gnd_positions.append(gnd)
            self.add_label(text="gnd",
                           layer="metal2",
                           offset=gnd)

        for i in range(self.word_size):
            if row_locations == None:
                base =vector(i * self.words_per_row * self.mux.width, 0)
            else:
                base = row_locations[i * self.words_per_row]
            BL_out = base + self.mux.BL_out_position
            BR_out = base + self.mux.BR_out_position
            self.add_label(text="bl_out[{0}]".format(i * self.words_per_row),
                           layer="metal2",
                           offset=BL_out)
            self.add_label(text="br_out[{0}]".format(i * self.words_per_row),
                           layer="metal2",
                           offset=BR_out)
            self.BL_out_positions.append(BL_out)
            self.BR_out_positions.append(BR_out)

        if(self.words_per_row == 2):
            for i in range(self.columns / 2):
                # This will not check that the inst connections match.
                self.connect_inst(args=["bl[{0}]".format(2 * i),
                                        "br[{0}]".format(2 * i),
                                        "bl_out[{0}]".format(2 * i),
                                        "br_out[{0}]".format(2 * i),
                                        "sel[{0}]".format(0), "gnd"],
                                  check=False)
                # This will not check that the inst connections match.
                self.connect_inst(args=["bl[{0}]".format(2 * i + 1),
                                        "br[{0}]".format(2 * i + 1),
                                        "bl_out[{0}]".format(2 * i),
                                        "br_out[{0}]".format(2 * i),
                                        "sel[{0}]".format(1), "gnd"],
                                  check=False)
        if(self.words_per_row == 4):
            for i in range(self.columns / 4):
                # This will not check that the inst connections match.
                self.connect_inst(args=["bl[{0}]".format(4 * i),
                                        "br[{0}]".format(4 * i),
                                        "bl_out[{0}]".format(4 * i),
                                        "br_out[{0}]".format(4 * i),
                                        "sel[{0}]".format(0), "gnd"],
                                  check=False)
                # This will not check that the inst connections match.
                self.connect_inst(args=["bl[{0}]".format(4 * i + 1),
                                        "br[{0}]".format(4 * i + 1),
                                        "bl_out[{0}]".format(4 * i),
                                        "br_out[{0}]".format(4 * i),
                                        "sel[{0}]".format(1), "gnd"],
                                  check=False)
                # This will not check that the inst connections match.
                self.connect_inst(args=["bl[{0}]".format(4 * i + 2),
                                        "br[{0}]".format(4 * i + 2),
                                        "bl_out[{0}]".format(4 * i),
                                        "br_out[{0}]".format(4 * i),
                                        "sel[{0}]".format(2), "gnd"],
                                  check=False)
                # This will not check that the inst connections match.
                self.connect_inst(args=["bl[{0}]".format(4 * i + 3),
                                        "br[{0}]".format(4 * i + 3),
                                        "bl_out[{0}]".format(4 * i),
                                        "br_out[{0}]".format(4 * i),
                                        "sel[{0}]".format(3), "gnd"],
                                  check=False)

    def add_routing(self,row_locations):
        self.add_horizontal_input_rail(row_locations)
        self.add_vertical_poly_rail(row_locations)
        self.routing_BL_BR(row_locations)

    def add_horizontal_input_rail(self, row_locations):
        """ HORIZONTAL ADDRESS INPUTS TO THE COLUMN MUX ARRAY """
        if (self.words_per_row > 1):
            for j in range(self.words_per_row):
                offset = vector(0, -(j + 1) * self.m1m2_via.width
                                       - j * drc['metal1_to_metal1'])
                if row_locations == None:
                    width = self.mux.width * self.columns
                else:
                    width = row_locations[self.columns-1][0]+self.mux.width
                self.add_rect(layer="metal1",
                              offset=offset,
                              width=width,
                              height=self.m1m2_via.width)
                self.addr_line_positions.append(offset)

    def add_vertical_poly_rail(self,row_locations):
        """  VERTICAL POLY METAL EXTENSION AND POLY CONTACT """
        for j1 in range(self.columns):
            pattern = math.floor(j1 / self.words_per_row) * self.words_per_row 
            height = ((self.m1m2_via.width + drc['metal1_to_metal1'])
                           *(pattern - j1))
            nmos1_poly = self.mux.nmos1_position + self.mux.nmos1.poly_positions[0]
            if row_locations == None:
                offset = nmos1_poly.scale(1, 0) + vector(j1 * self.mux.width, 0)
            else:
                offset = nmos1_poly.scale(1, 0) + row_locations[j1]     
            self.add_rect(layer="poly",
                          offset=offset,
                          width=drc["minwidth_poly"],
                          height= height -self.m1m2_via.width)

            # This is not instantiated and used for calculations only.
            poly_contact = contact(layer_stack=("metal1", "contact", "poly"))
            offset = offset.scale(1, 0) + vector(0, height - poly_contact.width)
            self.add_contact(layers=("metal1", "contact", "poly"),
                             offset=offset,
                             mirror="MX",
                             rotate=90)

    def routing_BL_BR(self, row_locations):
        """  OUTPUT BIT-LINE CONNECTIONS (BL_OUT, BR_OUT) """
        if (self.words_per_row > 1):
            for j in range(self.columns / self.words_per_row):
                if row_locations == None:
                    correct = self.mux.width * self.words_per_row * j
                else:
                    correct = row_locations[self.words_per_row * j][0]                   
                base = vector(correct,
                              self.m1m2_via.width + drc['metal1_to_metal1'])
                width = self.m1m2_via.width + self.mux.width * (self.words_per_row - 1)
=======
    def create_array(self):
        self.mux_inst = []

        # For every column, add a pass gate
        for col_num in range(self.columns):
            name = "XMUX{0}".format(col_num)
            x_off = vector(col_num * self.mux.width, self.route_height)
            self.mux_inst.append(self.add_inst(name=name,
                                               mod=self.mux,
                                               offset=x_off))

            offset = self.mux_inst[-1].get_pin("bl").ll()
            self.add_layout_pin(text="bl[{}]".format(col_num),
                                layer="metal2",
                                offset=offset,
                                height=self.height-offset.y)

            offset = self.mux_inst[-1].get_pin("br").ll()
            self.add_layout_pin(text="br[{}]".format(col_num),
                                layer="metal2",
                                offset=offset,
                                height=self.height-offset.y)

            gnd_pins = self.mux_inst[-1].get_pins("gnd")
            for gnd_pin in gnd_pins:
                # only do even colums to avoid duplicates
                offset = gnd_pin.ll()
                if col_num % 2 == 0: 
                    self.add_layout_pin(text="gnd",
                                        layer="metal2",
                                        offset=offset.scale(1,0),
                                        height=self.height)
            
            self.connect_inst(["bl[{}]".format(col_num),
                               "br[{}]".format(col_num),
                               "bl_out[{}]".format(int(col_num/self.words_per_row)),
                               "br_out[{}]".format(int(col_num/self.words_per_row)),
                               "sel[{}]".format(col_num % self.words_per_row),
                               "gnd"])

                

    def add_routing(self):
        self.add_horizontal_input_rail()
        self.add_vertical_poly_rail()
        self.route_bitlines()

    def add_horizontal_input_rail(self):
        """ Create address input rails on M1 below the mux transistors  """
        for j in range(self.words_per_row):
            offset = vector(0, self.route_height - (j+1)*self.m1_pitch)
            self.add_layout_pin(text="sel[{}]".format(j),
                                layer="metal1",
                                offset=offset,
                                width=self.mux.width * self.columns,
                                height=contact.m1m2.width)

    def add_vertical_poly_rail(self):
        """  Connect the poly to the address rails """
        
        # Offset to the first transistor gate in the pass gate
        for col in range(self.columns):
            # which select bit should this column connect to depends on the position in the word
            sel_index = col % self.words_per_row
            # Add the column x offset to find the right select bit
            gate_offset = self.mux_inst[col].get_pin("sel").bc()
            # height to connect the gate to the correct horizontal row
            sel_height = self.get_pin("sel[{}]".format(sel_index)).by()
            # use the y offset from the sel pin and the x offset from the gate
            offset = vector(gate_offset.x,self.get_pin("sel[{}]".format(sel_index)).cy())
            # Add the poly contact with a shift to account for the rotation
            self.add_via_center(layers=("metal1", "contact", "poly"),
                                offset=offset,
                                rotate=90)
            self.add_path("poly", [offset, gate_offset])

    def route_bitlines(self):
        """  Connect the output bit-lines to form the appropriate width mux """
        for j in range(self.columns):
            bl_offset = self.mux_inst[j].get_pin("bl_out").ll()
            br_offset = self.mux_inst[j].get_pin("br_out").ll()

            bl_out_offset = bl_offset - vector(0,(self.words_per_row+1)*self.m1_pitch)
            br_out_offset = br_offset - vector(0,(self.words_per_row+2)*self.m1_pitch)

            if (j % self.words_per_row) == 0:
                # Create the metal1 to connect the n-way mux output from the pass gate
                # These will be located below the select lines. Yes, these are M2 width
                # to ensure vias are enclosed and M1 min width rules.
                width = contact.m1m2.width + self.mux.width * (self.words_per_row - 1)
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd
                self.add_rect(layer="metal1",
                              offset=bl_out_offset,
                              width=width,
                              height=drc["minwidth_metal2"])
                self.add_rect(layer="metal1",
                              offset=br_out_offset,
                              width=width,
                              height=drc["minwidth_metal2"])
                          

                # Extend the bitline output rails and gnd downward on the first bit of each n-way mux
                self.add_layout_pin(text="bl_out[{}]".format(int(j/self.words_per_row)),
                                    layer="metal2",
                                    offset=bl_out_offset.scale(1,0),
                                    width=drc['minwidth_metal2'],
                                    height=self.route_height)
                self.add_layout_pin(text="br_out[{}]".format(int(j/self.words_per_row)),
                                    layer="metal2",
                                    offset=br_out_offset.scale(1,0),
                                    width=drc['minwidth_metal2'],
                                    height=self.route_height)

                # This via is on the right of the wire                
                self.add_via(layers=("metal1", "via1", "metal2"),
                             offset=bl_out_offset + vector(contact.m1m2.height,0),
                             rotate=90)
                # This via is on the left of the wire
                self.add_via(layers=("metal1", "via1", "metal2"),
                             offset= br_out_offset,
                             rotate=90)

            else:
                
                self.add_rect(layer="metal2",
                              offset=bl_out_offset,
                              width=drc['minwidth_metal2'],
<<<<<<< HEAD
                              height=height)
                self.add_rect(layer="metal2",
                              offset=base + self.mux.BR_position.scale(1,0),
                              width=drc['minwidth_metal2'],
                              height=height)
                self.add_rect(layer="metal2",
                              offset=base + self.mux.gnd_position.scale(1,0),
                              width=drc['minwidth_metal2'],
                              height=height)

            for j in range(self.columns):
                """ adding vertical metal rails to route BL_out and BR_out vertical rails """
                contact_spacing = self.m1m2_via.width + drc['metal1_to_metal1']
                height = self.words_per_row * contact_spacing + self.m1m2_via.width
                if row_locations == None:
                    correct = self.mux.width * j
                else:
                    correct = row_locations[j][0]         
                offset = vector(self.mux.BL_position.x + correct, 0)
                self.add_rect(layer="metal2",
                              offset=offset,
                              width=drc['minwidth_metal2'], 
                              height=-height)
                offset = offset + vector(self.m1m2_via.height, - height)
=======
                              height=self.route_height-bl_out_offset.y)
                # This via is on the right of the wire
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd
                self.add_via(layers=("metal1", "via1", "metal2"),
                             offset=bl_out_offset + vector(contact.m1m2.height,0),
                             rotate=90)
<<<<<<< HEAD

                offset = vector(self.mux.BR_position.x + correct, 0)
                height = height + contact_spacing
=======
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd
                self.add_rect(layer="metal2",
                              offset=br_out_offset,
                              width=drc['minwidth_metal2'],
                              height=self.route_height-br_out_offset.y)
                # This via is on the left of the wire                
                self.add_via(layers=("metal1", "via1", "metal2"),
                             offset= br_out_offset,
                             rotate=90)

                
            
