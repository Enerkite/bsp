# coding: utf-8
"""*****************************************************************************
* Copyright (C) 2021 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*****************************************************************************"""


#---------------------------------------------------------------------------------------#
#                                           IMPORT                                      #
#---------------------------------------------------------------------------------------#
import xml.etree.ElementTree as ET
import os

#---------------------------------------------------------------------------------------#
#                                 GLOBAL VARIABLES                                      #
#---------------------------------------------------------------------------------------#

class mcBspI_PwmConfiguration:
    def __init__(self, bspContent, component):
        self.component = component
        self.bspContent = bspContent

        # Pad to PWM mapping 
        module_Path = "/avr-tools-device-file/devices/device/peripherals/module@[name=\"TCC\"]"
        modules = ATDF.getNode(module_Path).getChildren()

        self.function_Tuple = dict()
        for module in modules:
            instance = module.getAttribute("name")
            signal_Path = module_Path + "/instance@[name=\"" + instance + "\"]/signals"
            signals = ATDF.getNode(signal_Path).getChildren()
            
            for signal in signals:               
                if "WO" == signal.getAttribute("group"):
                    pad = signal.getAttribute("pad")               
                    channel = signal.getAttribute("index")
    
                    try:
                        self.function_Tuple[pad].append((instance, channel ))
                    except:
                        self.function_Tuple[pad] = list()
                        self.function_Tuple[pad] = [(instance, channel )]
   
        self.readFromXml("dsPICDEM MCLV-2")
 
    def readFromXml(self, selected):
         # Read xml data from the path 
        self.information = dict()
        
        for board in self.bspContent.findall("boards/board"):
            if board.attrib["name"] == selected:
                for connector in board.findall("pwm/connector"):
                    index = connector.attrib["value"]
                    id = connector.attrib["id"]
                    pin = global_CONNECTOR_TO_PIN_MAP[index][0]
                    pad = global_PIN_TO_PAD_MAP[pin]
            
                    self.information[id] = dict()
                    self.information[id]["PIN"] = pin
                    self.information[id]["PAD"] = pad
                    self.information[id]["FUNCTION"] = self.function_Tuple[pad]

    def createSymbols(self):
        
        self.sym_PWM = self.component.createMenuSymbol("MCBSP_PWM_MENU", None )
        self.sym_PWM.setLabel("PWM Interface")
        
        # PWM instance 
        available = sorted(list(set([ str(self.function_Tuple[pad][0][0]) for pad in self.function_Tuple])))
        
        self.sym_INSTANCE = self.component.createComboSymbol("MCBSP_PWM_INSTANCE", self.sym_PWM, available )
        self.sym_INSTANCE.setLabel("Select Instance")
        self.sym_INSTANCE.setReadOnly(True)
        
        # PWM Channel A
        self.sym_PWMAH_PIN = self.component.createIntegerSymbol("MCBSP_PWMAH_PIN", self.sym_PWM )
        self.sym_PWMAH_PIN.setLabel("PWMAH pin")
        self.sym_PWMAH_PIN.setDefaultValue(int( self.information["PWM_AH"]["PIN"] ))
        self.sym_PWMAH_PIN.setReadOnly(True)
 
        
        self.sym_PWMAL_PIN = self.component.createIntegerSymbol("MCBSP_PWMAL_PIN", self.sym_PWM )
        self.sym_PWMAL_PIN.setLabel("PWMAL pin")
        self.sym_PWMAL_PIN.setDefaultValue(int(self.information["PWM_AL"]["PIN"]))
        self.sym_PWMAL_PIN.setReadOnly(True)


        # PWM Channel B
       
        self.sym_PWMBH_PIN = self.component.createIntegerSymbol("MCBSP_PWMBH_PIN", self.sym_PWM )
        self.sym_PWMBH_PIN.setLabel("PWMBH pin")
        self.sym_PWMBH_PIN.setDefaultValue(int(self.information["PWM_BH"]["PIN"]))
        self.sym_PWMBH_PIN.setReadOnly(True)


        self.sym_PWMBL_PIN = self.component.createIntegerSymbol("MCBSP_PWMBL_PIN", self.sym_PWM )
        self.sym_PWMBL_PIN.setLabel("PWMBL pin")
        self.sym_PWMBL_PIN.setDefaultValue(int(self.information["PWM_BL"]["PIN"]))
        self.sym_PWMBL_PIN.setReadOnly(True)


        # PWM Channel C
        self.sym_PWMCH_PIN = self.component.createIntegerSymbol("MCBSP_PWMCH_PIN", self.sym_PWM )
        self.sym_PWMCH_PIN.setLabel("PWMCH pin")
        self.sym_PWMCH_PIN.setDefaultValue(int(self.information["PWM_CH"]["PIN"]))
        self.sym_PWMCH_PIN.setReadOnly(True)


        self.sym_PWMCL_PIN = self.component.createIntegerSymbol("MCBSP_PWMCL_PIN", self.sym_PWM )
        self.sym_PWMCL_PIN.setLabel("PWMCL pin")
        self.sym_PWMCL_PIN.setDefaultValue(int(self.information["PWM_CL"]["PIN"]))
        self.sym_PWMCL_PIN.setReadOnly(True)


        # Dependency
        self.sym_DEPENDENCY = self.component.createMenuSymbol( None, None)
        self.sym_DEPENDENCY.setLabel("Dependency")
        self.sym_DEPENDENCY.setVisible(False)
        self.sym_DEPENDENCY.setDependencies(self.updateInformation, [ "MCBSP_PWMAL_PIN",
                                                                      "MCBSP_PWMAH_PIN",
                                                                      "MCBSP_PWMBL_PIN",
                                                                      "MCBSP_PWMBH_PIN",
                                                                      "MCBSP_PWMCL_PIN",
                                                                      "MCBSP_PWMCH_PIN"
                                                                    ])

        self.sym_BOARD = self.component.createFloatSymbol(None, None)
        self.sym_BOARD.setVisible(False)
        self.sym_BOARD.setDependencies(self.updateBoardParameters, ["BSP_BOARD_SEL"])
              
        

    def handleMessage(self, id,  message):
        if id == "MCPMSMFOC_PWM_INTERFACE":
            return self.information

    
    def pinToPwmMapping(self, pin, ID ):
        try:
            pad = global_PIN_TO_PAD_MAP[str(pin)]
            self.information[ID]["PIN"] =  pin
            self.information[ID]["PAD"] =  pad
            self.information[ID]["FUNCTION"] = self.function_Tuple[pad]
        except:
            pass

    def updateInformation(self, symbol, event):
        self.pinToPwmMapping( self.sym_PWMAL_PIN.getValue(), "PWM_AL" )
        self.pinToPwmMapping( self.sym_PWMAH_PIN.getValue(), "PWM_AH" )
        self.pinToPwmMapping( self.sym_PWMBL_PIN.getValue(), "PWM_BL" )
        self.pinToPwmMapping( self.sym_PWMBH_PIN.getValue(), "PWM_BH" )
        self.pinToPwmMapping( self.sym_PWMCL_PIN.getValue(), "PWM_CL" )
        self.pinToPwmMapping( self.sym_PWMCH_PIN.getValue(), "PWM_CH" )

        self.setPinManager()
        self.sendMessage()

    def updateBoardParameters(self, symbol, event): 
        self.resetPinManager()
        self.readFromXml(event["symbol"].getValue())
        self.sym_PWMAL_PIN.setValue(int(self.information["PWM_AL"]["PIN"]))
        self.sym_PWMAH_PIN.setValue(int(self.information["PWM_AH"]["PIN"]))
        self.sym_PWMBL_PIN.setValue(int(self.information["PWM_BL"]["PIN"]))
        self.sym_PWMBH_PIN.setValue(int(self.information["PWM_BH"]["PIN"]))
        self.sym_PWMCL_PIN.setValue(int(self.information["PWM_CL"]["PIN"]))
        self.sym_PWMCH_PIN.setValue(int(self.information["PWM_CH"]["PIN"]))

                 
    def setSymbols(self):
        pass

    def sendMessage( self ):
        Database.sendMessage("pmsm_foc","BSP_PWM_INTERFACE", self.information )

    def setPinManager(self):
        for pin in self.information.keys():
            number = str(self.information[pin]["PIN"])
            type = str(self.information[pin]["FUNCTION"][0][0]) + "_" + "WO" +  str(self.information[pin]["FUNCTION"][0][1])
           
            Database.setSymbolValue("core", "PIN_"+ number +"_FUNCTION_NAME", pin )         
            Database.setSymbolValue("core", "PIN_"+ number +"_FUNCTION_TYPE", type )

    def resetPinManager(self):
        for pin in self.information.keys():
            number = str(self.information[pin]["PIN"])
           
            Database.setSymbolValue("core", "PIN_"+ number +"_FUNCTION_NAME", "" )         
            Database.setSymbolValue("core", "PIN_"+ number +"_FUNCTION_TYPE", "" )

    def __call__(self):
        self.createSymbols()
        self.setPinManager()
        self.sendMessage()
   
