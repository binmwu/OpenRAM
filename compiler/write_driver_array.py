from math import log
import design
from tech import drc
import debug
from vector import vector
from globals import OPTS

class write_driver_array(design.design):
    """
    Array of tristate drivers to write to the bitlines through the column mux.
    Dynamically generated write driver array of all bitlines.
    """

    def __init__(self, columns, word_size, row_locations=None):
        design.design.__init__(self, "write_driver_array")
        debug.info(1, "Creating {0}".format(self.name))

        c = reload(__import__(OPTS.config.write_driver))
        self.mod_write_driver = getattr(c, OPTS.config.write_driver)
        self.driver = self.mod_write_driver("write_driver")
        self.add_mod(self.driver)

        self.columns = columns
        self.word_size = word_size
        self.words_per_row = columns / word_size

        self.width = self.columns * self.driver.width
        self.height = self.height = self.driver.height
        
        self.add_pins()
        self.create_layout(row_locations)
        self.DRC_LVS()

    def add_pins(self):
        for i in range(self.word_size):
            self.add_pin("data[{0}]".format(i))
        for i in range(self.word_size):            
            self.add_pin("bl[{0}]".format(i))
            self.add_pin("br[{0}]".format(i))
        self.add_pin("en")
        self.add_pin("vdd")
        self.add_pin("gnd")

<<<<<<< HEAD
    def create_layout(self,row_locations):
        self.add_write_driver_module()
        self.setup_layout_constants()
        self.create_write_array(row_locations)
        self.add_metal_rails()
        self.add_labels()
        self.offset_all_coordinates()

    def add_write_driver_module(self):
        self.driver = self.mod_write_driver("write_driver")
        self.add_mod(self.driver)

    def setup_layout_constants(self):
        self.width = self.columns * self.driver.width
        self.height = self.height = self.driver.height
        self.gnd_positions = []
        self.vdd_positions = []
        self.wen_positions = []
        self.BL_out_positions = []
        self.BR_out_positions = []
        self.driver_positions = []
        self.Data_in_positions = []

    def create_write_array(self, row_locations):
        for i in range(self.word_size):
            name = "Xwrite_driver%d" % i
            if row_locations == None:
                x_off = (i* self.driver.width * self.words_per_row)
            else:
                x_off = row_locations[i*self.words_per_row][0]
            self.driver_positions.append(vector(x_off, 0))
            self.add_inst(name=name,
                          mod=self.driver,
                          offset=[x_off, 0])
            if (self.words_per_row == 1):
                self.connect_inst(["data_in[{0}]".format(i),
                                   "bl[{0}]".format(i),
                                   "br[{0}]".format(i),
                                   "wen", "vdd", "gnd"])
            else:
                self.connect_inst(["data_in[{0}]".format(i),
                                   "bl_out[{0}]".format(i * self.words_per_row),
                                   "br_out[{0}]".format(i * self.words_per_row),
                                   "wen", "vdd", "gnd"])
=======
    def create_layout(self):
        self.create_write_array()
        self.add_layout_pins()

    def create_write_array(self):
        self.driver_insts = {}
        for i in range(0,self.columns,self.words_per_row):
            name = "Xwrite_driver{}".format(i)
            base = vector(i * self.driver.width,0)
            
            self.driver_insts[i/self.words_per_row]=self.add_inst(name=name,
                                                                  mod=self.driver,
                                                                  offset=base)
>>>>>>> f02843615640a43a370bc1ba37a26969751e0fbd

            self.connect_inst(["data[{0}]".format(i/self.words_per_row),
                               "bl[{0}]".format(i/self.words_per_row),
                               "br[{0}]".format(i/self.words_per_row),
                               "en", "vdd", "gnd"])


    def add_layout_pins(self):
        for i in range(self.word_size):
            din_pin = self.driver_insts[i].get_pin("din")
            self.add_layout_pin(text="data[{0}]".format(i),
                                layer="metal2",
                                offset=din_pin.ll(),
                                width=din_pin.width(),
                                height=din_pin.height())
            bl_pin = self.driver_insts[i].get_pin("BL")            
            self.add_layout_pin(text="bl[{0}]".format(i),
                                layer="metal2",
                                offset=bl_pin.ll(),
                                width=bl_pin.width(),
                                height=bl_pin.height())
                           
            br_pin = self.driver_insts[i].get_pin("BR")
            self.add_layout_pin(text="br[{0}]".format(i),
                                layer="metal2",
                                offset=br_pin.ll(),
                                width=br_pin.width(),
                                height=br_pin.height())
                           

        self.add_layout_pin(text="en",
                            layer="metal1",
                            offset=self.driver_insts[0].get_pin("en").ll().scale(0,1),
                            width=self.width,
                            height=drc['minwidth_metal1'])
                       
        self.add_layout_pin(text="vdd",
                            layer="metal1",
                            offset=self.driver_insts[0].get_pin("vdd").ll().scale(0,1),
                            width=self.width,
                            height=drc['minwidth_metal1'])
                       
        self.add_layout_pin(text="gnd",
                            layer="metal1",
                            offset=self.driver_insts[0].get_pin("gnd").ll().scale(0,1),
                            width=self.width,
                            height=drc['minwidth_metal1'])
                       

