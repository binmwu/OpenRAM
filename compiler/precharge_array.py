import design
import debug
from tech import drc
from vector import vector
from precharge import precharge


class precharge_array(design.design):
    """
    Dynamically generated precharge array of all bitlines.  Cols is number
    of bit line columns, height is the height of the bit-cell array.
    """

<<<<<<< HEAD
    def __init__(self, name, columns, ptx_width, beta=2, row_locations = None):
        design.design.__init__(self, name)
        debug.info(1, "Creating {0}".format(name))
=======
    def __init__(self, columns, size=1):
        design.design.__init__(self, "precharge_array")
        debug.info(1, "Creating {0}".format(self.name))
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd

        self.columns = columns

        self.pc_cell = precharge(name="precharge_cell", size=size)
        self.add_mod(self.pc_cell)

        self.width = self.columns * self.pc_cell.width
        self.height = self.pc_cell.height

        self.add_pins()
        self.create_layout(row_locations)
        self.DRC_LVS()

    def add_pins(self):
        """Adds pins for spice file"""
        for i in range(self.columns):
            self.add_pin("bl[{0}]".format(i))
            self.add_pin("br[{0}]".format(i))
        self.add_pin("en")
        self.add_pin("vdd")

<<<<<<< HEAD
    def create_layout(self, row_locations):
        self.create_pc_cell()
        self.setup_layout_constants()
        self.add_pc(row_locations)
        self.add_rails()
        self.offset_all_coordinates()

    def setup_layout_constants(self):
        self.vdd_positions = []
        self.BL_positions = []
        self.BR_positions = []
=======
    def create_layout(self):
        self.add_insts()
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd

        self.add_layout_pin(text="vdd",
                            layer="metal1",
                            offset=self.pc_cell.get_pin("vdd").ll(),
                            width=self.width,
                            height=drc["minwidth_metal1"])
        
        self.add_layout_pin(text="en",
                            layer="metal1",
                            offset=self.pc_cell.get_pin("clk").ll(),
                            width=self.width,
                            height=drc["minwidth_metal1"])
        

<<<<<<< HEAD
    def create_pc_cell(self):
        """Initializes a single precharge cell"""
        self.pc_cell = precharge(name="precharge_cell",
                                 ptx_width=self.ptx_width,
                                 beta=self.beta)
        self.add_mod(self.pc_cell)

    def add_pc(self, row_locations):
        """Creates a precharge array by horizontally tiling the precharge cell"""
        if row_locations != None:
            self.pc_cell_positions = row_locations
        else:
            self.pc_cell_positions = []
            for i in range(self.columns):
                self.pc_cell_positions.append(vector(self.pc_cell.width * i, 0))

        for i in range(self.columns):
            name = "pre_column_{0}".format(i)
            offset = self.pc_cell_positions[i]
            self.add_inst(name=name,
=======
    def add_insts(self):
        """Creates a precharge array by horizontally tiling the precharge cell"""
        for i in range(self.columns):
            name = "pre_column_{0}".format(i)
            offset = vector(self.pc_cell.width * i, 0)
            inst=self.add_inst(name=name,
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd
                          mod=self.pc_cell,
                          offset=offset)
            bl_pin = inst.get_pin("bl")
            self.add_layout_pin(text="bl[{0}]".format(i),
                                layer="metal2",
                                offset=bl_pin.ll(),
                                width=drc["minwidth_metal2"],
                                height=bl_pin.height())
            br_pin = inst.get_pin("br") 
            self.add_layout_pin(text="br[{0}]".format(i),
                                layer="metal2",
                                offset=br_pin.ll(),
                                width=drc["minwidth_metal2"],
                                height=bl_pin.height())
            self.connect_inst(["bl[{0}]".format(i), "br[{0}]".format(i),
                               "en", "vdd"])

