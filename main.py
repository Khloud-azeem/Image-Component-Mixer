from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtWidgets import QMessageBox  
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from os import path
import numpy as np
import sys
import os
from pyqtgraph import ImageView
import cv2 as cv
import qdarkgraystyle
import logging
from imageModel import ImageModel

logging.basicConfig(filename="logFile.log",format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"main2.ui"))


class MainApp(QtWidgets.QMainWindow,MAIN_WINDOW):
    def __init__(self):
        super(MainApp, self).__init__()
        # self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.msg = QMessageBox() 

# list of everything
        self.images=[None,None]
        self.image_models=[None,None]
        self.img_views=[self.imageView,self.imageView_2,self.imageView_1_edit,self.imageView_2_edit,self.output_1,self.output_2]
        self.combos=[self.comboBox,self.comboBox_2,self.comboBox_3,self.comboBox_4,self.comboBox_5]
        self.modes_combos=[self.comboBox_6,self.comboBox_7]
        self.slider1 = self.slider.value()
        self.slider2 = self.slider_2.value()
        self.heights=[0.0,0.0]
        self.widths=[0.0,0.0]
# hide
        for i in range(len(self.img_views)):
            self.img_views[i].ui.histogram.hide()
            self.img_views[i].ui.roiBtn.hide()
            self.img_views[i].ui.menuBtn.hide()
            self.img_views[i].ui.roiPlot.hide()

        self.connect_func()

    def connect_func(self):
        self.actionImage1.triggered.connect(lambda: self.browse(0))
        self.actionImage2.triggered.connect(lambda: self.browse(1))

        self.comboBox.activated.connect(lambda: self.check_combo(0))
        self.comboBox_2.activated.connect(lambda: self.check_combo(1))

        self.comboBox_4.activated.connect(self.output_mix)
        self.comboBox_5.activated.connect(self.output_mix)

        self.comboBox_6.activated.connect(self.output_mix)
        self.comboBox_7.activated.connect(self.output_mix)

        self.slider.valueChanged.connect(self.output_mix)
        self.slider_2.valueChanged.connect(self.output_mix)

    logger.info("The Application started successfully")

    def browse(self,idx):
        logger.info("Browsing the files")

        self.file,_ = QtGui.QFileDialog.getOpenFileName(self, 'choose the image', os.getenv('HOME') ,"Images (*.png *.xpm *.jpg)" )
        if self.file == "":
            pass
        if idx == 0:
            image = self.images[idx] = cv.imread(self.file,0).T
            self.heights[idx],self.widths[idx] = image.shape
            self.image_models[idx]=ImageModel(self.file)
            self.draw_img(idx,image)
            self.actionImage2.setEnabled(True)
            logger.info(f"Image{idx+1} was added successfully")

        elif idx == 1:
            image = self.images[idx] = cv.imread(self.file,0).T
            self.heights[idx],self.widths[idx] = image.shape
            if self.heights[0] != self.heights[1] or self.widths[0] != self.widths[1]:
                self.msg.setWindowTitle("Error in Image Size")
                self.msg.setText("The images must have the same size")
                self.msg.setIcon(QMessageBox.Warning)
                x = self.msg.exec_()
                logger.warning("Warnning!!. The images must have the same size")
                return
            else:
                self.image_models[idx]=ImageModel(self.file)
                self.draw_img(idx,image)
                logger.info(f"Image{idx+1} was added successfully")

    def draw_img(self,idx,image):
        self.img_views[idx].setImage(image)
        #set imageView size..all photos are the same size
        self.img_views[idx].view.setRange(xRange=[0, self.image_models[0].size[0]],yRange=[0,self.image_models[0].size[0]],padding=0)

    def check_combo(self,idx):
        selected_combo = self.combos[idx].currentText()
        if selected_combo == "FT Magnitude":
            self.draw_img(idx+2,self.image_models[idx].magnitude_shift)
        elif selected_combo == "FT Phase":
            self.draw_img(idx+2,self.image_models[idx].phase_shift)
        elif selected_combo == "FT Real Component":
            self.draw_img(idx+2,self.image_models[idx].real_shift)
        elif selected_combo == "FT Imaginary Component":
            self.draw_img(idx+2,self.image_models[idx].imaginary_shift)

        logger.info(f"{selected_combo} component of image{idx+1} was added")

    def output_mix(self):
        imgIndex1 = self.comboBox_4.currentIndex()
        imgIndex2 = self.comboBox_5.currentIndex()
        componentOne = self.modes_combos[0].currentText().lower()
        componentTwo = self.modes_combos[1].currentText().lower()
        combo_2 = self.modes_combos[1].currentText()
        self.sliderOneValue = self.slider.value()/100.0
        self.sliderTwoValue = self.slider_2.value()/100.0
        mixOutput = ...
        output_idx = self.comboBox_3.currentIndex()
        mode = componentOne + str('and') + componentTwo
        self.adjust_combo_elemnts(componentOne, combo_2)

        self.slider.setEnabled(True)
        self.slider_2.setEnabled(True)

        if componentOne == "magnitude":
            if componentTwo == "phase":
                mixOutput = self.image_models[imgIndex1].mix(self.image_models[imgIndex2], self.sliderOneValue,self.sliderTwoValue, mode)
            if componentTwo == "uniform phase":
                self.slider_2.setEnabled(False)
                mixOutput = self.image_models[imgIndex1].mix(self.image_models[imgIndex2], self.sliderOneValue,self.sliderTwoValue, mode)

        elif componentOne == "phase":
            if componentTwo == "magnitude":
                mixOutput = self.image_models[imgIndex2].mix(self.image_models[imgIndex1], self.sliderTwoValue,self.sliderOneValue, mode)
            elif componentTwo == "uniform magnitude":
                self.slider_2.setEnabled(False)
                mixOutput = self.image_models[imgIndex2].mix(self.image_models[imgIndex1], self.sliderOneValue,self.sliderTwoValue, mode)

        elif componentOne == "real":
            if componentTwo == "imaginary":
                mixOutput = self.image_models[imgIndex1].mix(self.image_models[imgIndex2], self.sliderOneValue,self.sliderTwoValue, mode)

        elif componentOne == "imaginary":
            if componentTwo == "real":
                mixOutput = self.image_models[imgIndex2].mix(self.image_models[imgIndex1], self.sliderTwoValue,self.sliderOneValue, mode)

        elif componentOne == "uniform phase":
            self.slider.setEnabled(False)
            if componentTwo == "magnitude":
                mixOutput = self.image_models[imgIndex2].mix(self.image_models[imgIndex1], self.sliderTwoValue,self.sliderOneValue, mode)
            elif componentOne == "uniform magnitude":
                self.slider.setEnabled(False)
                mixOutput = self.image_models[imgIndex2].mix(self.image_models[imgIndex1], self.sliderTwoValue,self.sliderOneValue, mode)

        elif componentOne == "uniform magnitude":
            self.slider.setEnabled(False)
            if componentTwo == "phase":
                mixOutput = self.image_models[imgIndex1].mix(self.image_models[imgIndex2], self.sliderOneValue,self.sliderTwoValue, mode)
            elif componentTwo == "uniform phase":
                self.slider_2.setEnabled(False)
                mixOutput = self.image_models[imgIndex1].mix(self.image_models[imgIndex2], self.sliderOneValue,self.sliderTwoValue, mode)
        
        
        self.draw_img(output_idx+4,mixOutput)
        logger.info(f"Output{output_idx+1} was generated")


    def adjust_combo_elemnts(self,combo1,combo2):
        self.modes_combos[1].clear()
        self.modes_combos[1].addItem("Choose FT Component")

        if combo1 == "magnitude":
            self.modes_combos[1].addItem("Phase")
            self.modes_combos[1].addItem("Uniform Phase")
            self.modes_combos[1].setCurrentText(combo2)
        elif combo1 == "phase":
            self.modes_combos[1].addItem("Magnitude")
            self.modes_combos[1].addItem("Uniform Magnitude")
            self.modes_combos[1].setCurrentText(combo2)
        elif combo1 == "real":
            self.modes_combos[1].addItem("Imaginary")
            self.modes_combos[1].setCurrentText(combo2)
        elif combo1 == "imaginary":
            self.modes_combos[1].addItem("Real")
            self.modes_combos[1].setCurrentText(combo2)
        elif combo1 == "uniform magnitude":
            self.modes_combos[1].addItem("Phase")
            self.modes_combos[1].setCurrentText(combo2)
        elif combo1 == "uniform phase":
            self.modes_combos[1].addItem("Magnitude")
            self.modes_combos[1].setCurrentText(combo2)
        logger.info("ComboBoxes was adjusted")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
