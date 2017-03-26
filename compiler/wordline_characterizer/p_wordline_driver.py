from tech import drc, parameter
import debug
import design
from math import log
from math import sqrt
import math
from pinv import pinv
from pnand_2 import pnand_2
from vector import vector
from globals import OPTS

class wordline_driver(design.design):
    """
    Creates a Wordline Driver
    Generates the wordline-driver to drive the bitcell
    """

    def __init__(self, name, rows, driver_strength=drc["minwidth_tx"], NAND2_strength = 2*drc["minwidth_tx"]):
        design.design.__init__(self, name)

        self.rows = rows
        self.driver_strength = driver_strength
        self.add_pins()
        self.design_layout(NAND2_strength)
        self.DRC_LVS()

    def add_pins(self):
        # inputs to wordline_driver.
        for i in range(self.rows):
            self.add_pin("decode_out[{0}]".format(i))
        # Outputs from wordline_driver.
        for i in range(self.rows):
            self.add_pin("wl[{0}]".format(i))
        self.add_pin("clk")
        self.add_pin("vdd")
        self.add_pin("gnd")

    def design_layout(self,NAND2_strength ):
        self.add_layout(NAND2_strength)
        self.offsets_of_gates()
        self.create_layout()

    def add_layout(self, NAND2_strength ):
        self.inv = pinv(name="pinverter",
                        nmos_width=drc["minwidth_tx"],
                        beta=parameter["pinv_beta"])
        self.add_mod(self.inv)
        self.driver = pinv(name="driver_inv",
                           nmos_width=self.driver_strength,
                           beta=parameter["pinv_beta"])
        self.add_mod(self.driver)

        self.NAND2 = pnand_2(name="pnand2",
                            nmos_width=NAND2_strength)
        self.add_mod(self.NAND2)




    def offsets_of_gates(self):
        self.x_offset0 = 2 * drc["minwidth_metal1"] + 5 * drc["metal1_to_metal1"]
        self.x_offset1 = self.x_offset0 + self.inv.width
        self.x_offset2 = self.x_offset1 + self.NAND2.width

        self.width = self.x_offset2 + self.driver.width
        self.height = self.inv.height * self.rows

        # Defining offset postions
        self.decode_out_positions = []
        self.clk_positions = []
        self.WL_positions = []
        self.vdd_positions = []
        self.gnd_positions = []

    def create_layout(self):
        # Clk connection
        self.add_rect(layer="metal1",
                      offset=[drc["minwidth_metal1"] + 2 * drc["metal1_to_metal1"],
                              2 * drc["minwidth_metal1"]],
                      width=drc["minwidth_metal1"],
                      height=self.height + 4*drc["minwidth_metal1"])
        self.clk_positions.append([drc["minwidth_metal1"] + 2*drc["metal1_to_metal1"],
                                           self.height])
        self.add_label(text="clk",
                       layer="metal1",
                       offset=self.clk_positions[0])

        for row in range(self.rows):
            name_inv1 = "Wordline_driver_inv_clk%d" % (row)
            name_nand = "Wordline_driver_nand%d" % (row)
            name_inv2 = "Wordline_driver_inv%d" % (row)

            # Extend vdd and gnd of Wordline_driver
            yoffset = (row + 1) * self.inv.height - 0.5 * drc["minwidth_metal2"]
            self.add_rect(layer="metal2",
                          offset=[0, yoffset],
                          width=self.x_offset0,
                          height=drc["minwidth_metal2"])

            self.add_via(layers=("metal1", "via1", "metal2"),
                          offset=[drc["minwidth_metal1"], yoffset],
                          mirror="R90")
            self.add_via(layers=("metal1", "via1", "metal2"),
                          offset=[self.x_offset0 + drc["minwidth_metal1"],
                                  yoffset],
                          mirror="R90")
            inv_nand2B_connection_height = (abs(self.inv.Z_position.y 
                                                    - self.NAND2.B_position.y)
                                                + drc["minwidth_metal1"])

            if (row % 2):
                y_offset = self.inv.height*(row + 1)
                name_inv1_offset = [self.x_offset0, y_offset]
                nand2_offset=[self.x_offset1, y_offset]
                self.inv2_offset=[self.x_offset2, y_offset]
                inst_mirror = "MX"
                cell_dir = vector(0,-1)
                m1tm2_rotate=270
                m1tm2_mirror="R0"
            else:
                y_offset = self.inv.height*row
                name_inv1_offset = [self.x_offset0, y_offset]
                nand2_offset=[self.x_offset1, y_offset]
                self.inv2_offset=[self.x_offset2, y_offset]
                inst_mirror = "R0"
                cell_dir = vector(0,1)
                m1tm2_rotate=90
                m1tm2_mirror="MX"

            # add inv1 based on the info above
            self.add_inst(name=name_inv1,
                          mod=self.inv,
                          offset=name_inv1_offset,
                          mirror=inst_mirror )
            self.connect_inst(["clk", "clk_bar[{0}]".format(row),
                               "vdd", "gnd"])
            # add nand 2
            self.add_inst(name=name_nand,
                          mod=self.NAND2,
                          offset=nand2_offset,
                          mirror=inst_mirror)
            self.connect_inst(["decode_out[{0}]".format(row),
                               "clk_bar[{0}]".format(row),
                               "net{0}".format(row),
                               "vdd", "gnd"])
            # add inv2
            self.add_inst(name=name_inv2,
                          mod=self.driver,
                          offset=self.inv2_offset,
                          mirror=inst_mirror)
            self.connect_inst(["net{0}".format(row),
                               "wl[{0}]".format(row),
                               "vdd", "gnd"])



            # clk connection
            clk_offset= [drc["minwidth_metal1"] + 2 * drc["metal1_to_metal1"],
                         y_offset + cell_dir.y * self.inv.A_position.y]
            self.add_rect(layer="metal1",
                          offset=clk_offset,
                          width=self.x_offset0 - 2*drc["metal1_to_metal1"],
                          height=cell_dir.y *drc["minwidth_metal1"])
            # first inv to nand2 B
            inv_to_nand2B_offset = [self.x_offset1 - drc["minwidth_metal1"],
                                  y_offset + cell_dir.y * self.NAND2.B_position.y]
            self.add_rect(layer="metal1",
                          offset=inv_to_nand2B_offset,
                          width=drc["minwidth_metal1"],
                          height=cell_dir.y*inv_nand2B_connection_height)
            # Nand2 out to 2nd inv
            nand2_to_2ndinv_offset =[self.x_offset2,
                                  y_offset + cell_dir.y * self.NAND2.Z_position.y]
            self.add_rect(layer="metal1",
                          offset=nand2_to_2ndinv_offset,
                          width=drc["minwidth_metal1"],
                          height=cell_dir.y * drc["minwidth_metal1"])
            # nand2 A connection
            self.add_rect(layer="metal2",
                          offset=[0, y_offset + cell_dir.y * self.NAND2.A_position.y],
                          width=self.x_offset1,
                          height=cell_dir.y*drc["minwidth_metal2"])
            self.add_via(layers=("metal1", "via1", "metal2"),
                          offset=[self.x_offset1,
                                  y_offset + cell_dir.y * self.NAND2.A_position.y],
                          rotate=m1tm2_rotate,
                          mirror=m1tm2_mirror)
            self.add_via(layers=("metal1", "via1", "metal2"),
                          offset=[0, 
                                  y_offset +cell_dir.y*self.NAND2.A_position.y],
                          mirror=inst_mirror)


            base_offset = vector(self.width, y_offset)
            decode_out_offset = base_offset.scale(0,1)+self.NAND2.A_position.scale(cell_dir)
            wl_offset = base_offset + self.inv.Z_position.scale(cell_dir)
            vdd_offset = base_offset + self.inv.vdd_position.scale(cell_dir)
            gnd_offset = base_offset + self.inv.gnd_position.scale(cell_dir)

            self.add_label(text="decode_out[{0}]".format(row),
                           layer="metal2",
                           offset=decode_out_offset)
            self.add_rect(layer="metal1",
                          offset=wl_offset,
                          width=drc["minwidth_metal1"]*cell_dir.y,
                          height=drc["minwidth_metal1"]*cell_dir.y)
            self.add_label(text="wl[{0}]".format(row),
                           layer="metal1",
                           offset=wl_offset)
            self.add_label(text="gnd",
                           layer="metal1",
                           offset=gnd_offset)
            self.add_label(text="vdd",
                           layer="metal1",
                           offset=vdd_offset)

            self.decode_out_positions.append(decode_out_offset)
            self.WL_positions.append(wl_offset)
            self.vdd_positions.append(vdd_offset)
            self.gnd_positions.append(gnd_offset)

    def add_extra_driver(self, offset):
        offset = offset + vector(self.driver.width,0)
        self.driver_offset =offset
        for row in range(self.rows):
            #sec_offset =[95.045, 0]
            self.add_inst(name="add_on",
                          mod=self.driver,
                          offset=offset,
                          mirror="MY")
            self.connect_inst(["net{0}".format(row),
                               "wl[{0}]".format(row),
                               "vdd", "gnd"])

        start =offset + self.driver.vdd_position - vector(self.driver.width, 0)
        self.add_rect(layer="metal1",
                      offset=start,
                      width =-6*drc["minwidth_metal1"],  
                      height=drc["minwidth_metal1"])

        start =offset + self.inv.gnd_position - vector(self.driver.width, 0)
        self.add_rect(layer="metal1",
                      offset=start,
                      width =-6*drc["minwidth_metal1"],  
                      height=drc["minwidth_metal1"])



        start = self.inv2_offset + self.driver.A_position 
        end = offset + self.driver.A_position.scale(-1,1)
        self.add_via(layers=("metal1", "via1", "metal2"),
                     offset=start,
                     rotate=90,
                     mirror= "MX")
        self.add_via(layers=("metal2", "via2", "metal3"),
                     offset=start,
                     rotate=90,
                     mirror= "MX")

        self.add_via(layers=("metal1", "via1", "metal2"),
                     offset=end,
                     rotate=90)
        self.add_via(layers=("metal2", "via2", "metal3"),
                     offset=end,
                     rotate=90)

        self.add_path(layer=("metal3"),
                      coordinates=[start,end],
                      offset=start)

    def route_extra_WL(self,offset):
        start =self.driver_offset + self.driver.Z_position.scale(-1,1) + vector(-0.5*drc["minwidth_metal1"], drc["minwidth_metal1"])
        end = offset
        self.add_path(layer=("metal1"),
                      coordinates=[start,end],
                      offset=start)

    def extend_extra_WL(self,offset):
        start =self.driver_offset + self.driver.Z_position.scale(-1,1) + vector(-0.5*drc["minwidth_metal1"], drc["minwidth_metal1"])
        end = vector(offset)
        mid1 = vector(start.x,end.y)
        mid2 = mid1+vector(self.driver.width+2*drc["minwidth_metal1"],0)

        self.add_path(layer=("metal1"),
                      coordinates=[start,mid1],
                      offset=start)
        via_offset = mid1 - vector(0.5*drc["minwidth_metal1"],0.5*drc["minwidth_metal1"])
        self.add_via(layers=("metal1", "via1", "metal2"),
                     offset=via_offset)

        self.add_path(layer=("metal2"),
                      coordinates=[mid1,mid2],
                      offset=mid1)
       
        via_offset = mid2 - vector(0.5*drc["minwidth_metal1"], 0.5*drc["minwidth_metal1"])
        self.add_via(layers=("metal1", "via1", "metal2"),
                     offset=via_offset)       
 
        self.add_path(layer=("metal1"),
                      coordinates=[mid2,end],
                      offset=mid2)

    def extend_extra_vdd(self,offset):
        start =self.driver_offset + self.driver.vdd_position    
        end = vector(offset)
        self.add_path(layer=("metal1"),
                      coordinates=[start,end],
                      offset=start)

    def extend_extra_gnd(self,offset):
        start =self.driver_offset + self.driver.gnd_position    
        end = vector(offset)
        self.add_path(layer=("metal1"),
                      coordinates=[start,end],
                      offset=start)
