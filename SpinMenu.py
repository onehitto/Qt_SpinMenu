import sys
import math
from PyQt5.QtCore import Qt, pyqtSignal, QPoint,QTimer,QRectF,QEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor,QCursor,QPainterPath,QMouseEvent
import keyboard
import os
from pyqtkeybind import keybinder
from math import cos,sin,radians

class ArcWidget(QWidget):
    sectorClicked = pyqtSignal(int)
    sigonshow = pyqtSignal()
    posmove = pyqtSignal(QEvent)
    
    def __init__(self,x ,y , radius_outer,radius_inner,sector = 4,pencolor: QColor = Qt.black,brushcolor: QColor = QColor(0, 0, 255)):
        super().__init__()
        self.setFixedSize(2*radius_outer, 2*radius_outer)
        self.x = x
        self.y = y 
        self.radius_outer = radius_outer
        self.radius_inner = radius_outer-radius_inner
        self.circleraduis = radius_inner - 5
        self.pencolor = pencolor
        self.brushcolor = brushcolor
        self.sector = sector
        self.draw = []
        self.CenterCircleRect = QRectF(
            self.x + self.radius_outer-self.circleraduis,
            self.y + self.radius_outer-self.circleraduis,
            2 * self.circleraduis,
            2 * self.circleraduis
            )
        
        # animation 
        self.draw_progress = 0
        self.span_angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDrawing)
          # Update every 50 milliseconds
        
        #check mouse in widget
        # Initialize a QTimer
        self.timer_W = QTimer(self)
        self.timer_W.timeout.connect(self.checkMousePosition)
        #init
        for i in range(self.sector):
            self.draw.append(QPainterPath())
            
        #signal
        
        self.sigonshow.connect(self.on_show)
        self.hide()
            
            

    def updateDrawing(self):
        self.draw_progress += 1
        self.span_angle += 3.6 # Increase the drawing progress
        if self.draw_progress > 100:
            self.timer.stop()  # Stop the timer when the drawing is complete
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set pen properties
        pen = QPen()
        pen.setColor(self.pencolor)  # Blue color
        pen.setWidth(2)
        painter.setPen(pen)
        angle = 360 / self.sector
        for i in range(self.sector):
            startangle = i * angle + 45
            spanangle = angle - 10
            drawangle = (spanangle * self.draw_progress)// 100
            self.draw[i] = self.pathArcRaduis(startangle,drawangle)
            painter.drawPath(self.draw[i])
            painter.fillPath(self.draw[i], self.brushcolor)
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.white))
        painter.drawPie(self.CenterCircleRect, 0, self.span_angle * 16)
        
             
    def pathArcRaduis(self,startangle,angle):
        path = QPainterPath()
        x = self.x
        y = self.y
        centre_x = x + self.radius_outer
        centre_y = x + self.radius_outer
        width = 2 * self.radius_outer 
        height = 2 * self.radius_outer 
        x_arc =  centre_x + self.radius_outer * cos(radians(startangle))
        y_arc = centre_y - self.radius_outer * sin(radians(startangle))
        path.moveTo(x_arc , y_arc) 
        path.arcTo(x , y, 2 * self.radius_outer, 2 * self.radius_outer, startangle , angle)  # (x, y, width, height, start angle, span angle)
        path.arcTo(x + self.radius_inner, y + self.radius_inner , width - 2 * self.radius_inner, height - 2 * self.radius_inner,angle + startangle, - angle )
        path.arcTo(x , y, 2 * self.radius_outer, 2 * self.radius_outer, startangle , 0)
        return path 
            
    def mousePressEvent(self, event: QMouseEvent) -> None:
        for sector in range(self.sector):
            if self.draw[sector].contains(event.pos()):
                self.menuClicked(sector)
                
        dx = self.CenterCircleRect.center().x() - event.pos().x()
        dy = self.CenterCircleRect.center().y() - event.pos().y()
        distance = (dx**2 + dy**2)**0.5
        if distance <= self.circleraduis:
            self.menuClicked(99)
        super().mousePressEvent(event)

    def checkMousePosition(self):
        cursorPos = QCursor.pos()
        widgetCenter = self.mapToGlobal(self.rect().center())
        
        dx = cursorPos.x() - widgetCenter.x()
        dy = cursorPos.y() - widgetCenter.y()
        distance = math.sqrt(dx**2 + dy**2)
        
        radius = min(self.width(), self.height()) // 2
        if distance > radius:
            self.timer_W.stop()
            self.hide()
            
    def showEvent(self, event):
        super(ArcWidget, self).showEvent(event)
        self.posmove.emit(event)   
              
    def on_show(self):
        self.timer_W.start(100)
        self.timer.start(3)
        self.draw_progress = 0
        self.span_angle = 0
        self.show()
        
    def menuClicked(self,section):
        print(f"sector pressed, {section}")

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        layout = QVBoxLayout(self)
        self.circularWidget = ArcWidget(0,0,50,20)
        layout.addWidget(self.circularWidget)
        
        self.setWindowOpacity(0.9)
        self.setStyleSheet("background:transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        #self.circularWidget.sectorClicked.connect(self.on_sector_clicked)
        self.circularWidget.posmove.connect(self.on_circular_widget_shown)

        
    def on_circular_widget_shown(self,event):
        super(MainWindow, self).showEvent(event)
        # Adjust the position of the MainWindow after it is visible
        cursorPos = QCursor.pos()
        widgetCenter = self.circularWidget.mapToGlobal(self.circularWidget.rect().center())
        dx = widgetCenter.x() - cursorPos.x()
        dy = widgetCenter.y() - cursorPos.y()
        self.move(self.x() - dx, self.y() - dy)
        self.raise_()
        self.activateWindow()
    
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    keyboard.add_hotkey('ctrl+D', lambda: window.circularWidget.sigonshow.emit())
    sys.exit(app.exec_())
