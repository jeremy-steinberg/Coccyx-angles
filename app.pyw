import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QSlider, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QCursor
from PyQt5.QtCore import Qt, QPoint
import math

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.parent = parent
        self.start_pos = None
        self.current_pos = None

    def mousePressEvent(self, event):
        if self.parent:
            if self.parent.drawing:
                self.parent.get_point(event)
            elif self.parent.drawing_angle_c:
                self.start_pos = event.pos()
                self.current_pos = event.pos()
            else:
                self.parent.start_pan(event)

    def mouseMoveEvent(self, event):
        if self.parent:
            if self.parent.drawing_angle_c and self.start_pos:
                self.current_pos = event.pos()
                self.parent.update_preview_line(self.start_pos, self.current_pos)
            elif self.parent.panning:
                self.parent.pan_image(event)

    def mouseReleaseEvent(self, event):
        if self.parent:
            if self.parent.drawing_angle_c and self.start_pos:
                end_pos = event.pos()
                self.parent.add_line_to_angle_c(self.start_pos, end_pos)
                self.start_pos = None
                self.current_pos = None
            else:
                self.parent.stop_pan(event)

    def wheelEvent(self, event):
        if self.parent:
            if event.buttons() & Qt.LeftButton:
                self.parent.scale_image(1, event.angleDelta().y())
            elif event.buttons() & Qt.RightButton:
                self.parent.scale_image(2, event.angleDelta().y())

class ImageOverlayTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Overlay and Angle Measurement Tool')
        self.setGeometry(100, 100, 1000, 800)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Image display area
        self.image_label = ImageLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label)

        # Control buttons
        button_layout = QHBoxLayout()
        
        self.load_image1_btn = QPushButton('Load Image 1')
        self.load_image1_btn.clicked.connect(lambda: self.load_image(1))
        button_layout.addWidget(self.load_image1_btn)

        self.load_image2_btn = QPushButton('Load Image 2')
        self.load_image2_btn.clicked.connect(lambda: self.load_image(2))
        button_layout.addWidget(self.load_image2_btn)

        self.draw_angle_btn = QPushButton('Draw Angle')
        self.draw_angle_btn.clicked.connect(self.toggle_draw_mode)
        button_layout.addWidget(self.draw_angle_btn)

        self.calculate_angleA_btn = QPushButton('Calculate angle A')
        self.calculate_angleA_btn.clicked.connect(self.calculate_angleA)
        button_layout.addWidget(self.calculate_angleA_btn)

        self.calculate_angleC_btn = QPushButton('Calculate Angle C')
        self.calculate_angleC_btn.clicked.connect(self.toggle_angle_c_mode)
        button_layout.addWidget(self.calculate_angleC_btn)

        main_layout.addLayout(button_layout)

        # Rotation sliders
        rotation_layout = QHBoxLayout()
        
        self.rotation_slider1 = QSlider(Qt.Horizontal)
        self.rotation_slider1.setRange(0, 359)
        self.rotation_slider1.valueChanged.connect(lambda: self.rotate_image(1))
        rotation_layout.addWidget(QLabel("Rotate Image 1:"))
        rotation_layout.addWidget(self.rotation_slider1)

        self.rotation_slider2 = QSlider(Qt.Horizontal)
        self.rotation_slider2.setRange(0, 359)
        self.rotation_slider2.valueChanged.connect(lambda: self.rotate_image(2))
        rotation_layout.addWidget(QLabel("Rotate Image 2:"))
        rotation_layout.addWidget(self.rotation_slider2)

        main_layout.addLayout(rotation_layout)

        # Transparency sliders
        transparency_layout = QHBoxLayout()

        self.transparency_slider1 = QSlider(Qt.Horizontal)
        self.transparency_slider1.setRange(0, 100)
        self.transparency_slider1.setValue(100)
        self.transparency_slider1.valueChanged.connect(self.update_display)
        transparency_layout.addWidget(QLabel("Transparency Image 1:"))
        transparency_layout.addWidget(self.transparency_slider1)

        self.transparency_slider2 = QSlider(Qt.Horizontal)
        self.transparency_slider2.setRange(0, 100)
        self.transparency_slider2.setValue(50)
        self.transparency_slider2.valueChanged.connect(self.update_display)
        transparency_layout.addWidget(QLabel("Transparency Image 2:"))
        transparency_layout.addWidget(self.transparency_slider2)

        main_layout.addLayout(transparency_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initialize variables
        self.image1 = None
        self.image2 = None
        self.image1_rotation = 0
        self.image2_rotation = 0
        self.image1_offset = QPoint(0, 0)
        self.image2_offset = QPoint(0, 0)
        self.image1_scale = 1.0
        self.image2_scale = 1.0
        self.drawing = False
        self.panning = False
        self.panning_image = 0
        self.last_pos = None
        self.drawing_angle_c = False
        self.angle_c_lines = []
        self.preview_pixmap = None
        self.points = []

    def load_image(self, image_number):
        file_name, _ = QFileDialog.getOpenFileName(self, f"Open Image {image_number}", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            image = QImage(file_name)
            if image_number == 1:
                self.image1 = image
                self.image1_offset = QPoint(0, 0)
                self.image1_scale = 1.0
            else:
                self.image2 = image
                self.image2_offset = QPoint(0, 0)
                self.image2_scale = 1.0
            self.update_display()

    def scale_image(self, image_number, delta):
        scale_factor = 1.0 + (delta / 1200.0)  # Adjust sensitivity here
        if image_number == 1 and self.image1:
            self.image1_scale *= scale_factor
            # Limit scaling to reasonable ranges
            self.image1_scale = max(0.1, min(5.0, self.image1_scale))
        elif image_number == 2 and self.image2:
            self.image2_scale *= scale_factor
            # Limit scaling to reasonable ranges
            self.image2_scale = max(0.1, min(5.0, self.image2_scale))
        self.update_display()

    def rotate_image(self, image_number):
        if image_number == 1:
            self.image1_rotation = self.rotation_slider1.value()
        else:
            self.image2_rotation = self.rotation_slider2.value()
        self.update_display()

    def update_display(self):
        if self.image1:
            pixmap = QPixmap(self.image_label.size())
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            
            # Draw rotated, scaled, and panned image1
            painter.setOpacity(self.transparency_slider1.value() / 100)
            painter.translate(self.image_label.width() / 2 + self.image1_offset.x(), 
                            self.image_label.height() / 2 + self.image1_offset.y())
            painter.rotate(self.image1_rotation)
            painter.scale(self.image1_scale, self.image1_scale)
            painter.translate(-self.image1.width() / 2, -self.image1.height() / 2)
            painter.drawImage(0, 0, self.image1)
            painter.resetTransform()
            
            if self.image2:
                # Draw rotated, scaled, and panned image2 with transparency
                painter.setOpacity(self.transparency_slider2.value() / 100)
                painter.translate(self.image_label.width() / 2 + self.image2_offset.x(), 
                                self.image_label.height() / 2 + self.image2_offset.y())
                painter.rotate(self.image2_rotation)
                painter.scale(self.image2_scale, self.image2_scale)
                painter.translate(-self.image2.width() / 2, -self.image2.height() / 2)
                painter.drawImage(0, 0, self.image2)
            
            painter.end()
            self.image_label.setPixmap(pixmap)

            if self.drawing_angle_c:
                self.preview_pixmap = self.image_label.pixmap().copy()

    def toggle_draw_mode(self):
        self.drawing = not self.drawing
        if self.drawing:
            self.draw_angle_btn.setText('Measuring Angle')
            self.image_label.setCursor(Qt.CrossCursor)
        else:
            self.draw_angle_btn.setText('Draw Angle')
            self.image_label.setCursor(Qt.ArrowCursor)
            self.points = []

    def toggle_angle_c_mode(self):
        self.drawing_angle_c = not self.drawing_angle_c
        self.drawing = False  # Disable other drawing mode
        if self.drawing_angle_c:
            self.calculate_angleC_btn.setText('Drawing Angle C')
            self.image_label.setCursor(Qt.CrossCursor)
            self.angle_c_lines = []
        else:
            self.calculate_angleC_btn.setText('Calculate Angle C')
            self.image_label.setCursor(Qt.ArrowCursor)
            self.angle_c_lines = []
        self.update_display()

    def update_preview_line(self, start_pos, current_pos):
        if self.image1:
            # Create a copy of the current display
            if self.preview_pixmap is None:
                self.preview_pixmap = self.image_label.pixmap().copy()
            
            preview = self.preview_pixmap.copy()
            painter = QPainter(preview)
            
            # Draw existing lines
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            
            for line in self.angle_c_lines:
                painter.drawLine(line[0], line[1])
            
            # Draw preview line
            painter.drawLine(start_pos, current_pos)
            
            painter.end()
            self.image_label.setPixmap(preview)        

    def add_line_to_angle_c(self, start_pos, end_pos):
        if len(self.angle_c_lines) < 2:
            self.angle_c_lines.append((start_pos, end_pos))
            
            if len(self.angle_c_lines) == 2:
                self.calculate_angle_c()
            else:
                # Store the current display for future preview updates
                self.preview_pixmap = self.image_label.pixmap().copy()

    def get_point(self, event):
        if len(self.points) < 3:
            self.points.append(event.pos())
            if len(self.points) == 3:
                self.calculate_angle()

    def calculate_angle(self):
        p1, p2, p3 = self.points
        angle = math.degrees(math.atan2(p3.y() - p2.y(), p3.x() - p2.x()) - 
                           math.atan2(p1.y() - p2.y(), p1.x() - p2.x()))
        angle = abs(angle)
        if angle > 180:
            angle = 360 - angle
        
        pixmap = self.image_label.pixmap()
        painter = QPainter(pixmap)
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(p1, p2)
        painter.drawLine(p2, p3)
        painter.drawText(p2, f"{angle:.1f}°")
        painter.end()
        self.image_label.setPixmap(pixmap)
        self.points = []

    def calculate_angle_c(self):
        if len(self.angle_c_lines) == 2:
            # Calculate vectors for both lines
            line1_vector = (
                self.angle_c_lines[0][1].x() - self.angle_c_lines[0][0].x(),
                self.angle_c_lines[0][1].y() - self.angle_c_lines[0][0].y()
            )
            line2_vector = (
                self.angle_c_lines[1][1].x() - self.angle_c_lines[1][0].x(),
                self.angle_c_lines[1][1].y() - self.angle_c_lines[1][0].y()
            )
            
            # Calculate dot product and magnitudes
            dot_product = (line1_vector[0] * line2_vector[0] + 
                         line1_vector[1] * line2_vector[1])
            mag1 = math.sqrt(line1_vector[0]**2 + line1_vector[1]**2)
            mag2 = math.sqrt(line2_vector[0]**2 + line2_vector[1]**2)
            
            # Calculate angle
            angle = math.degrees(math.acos(dot_product / (mag1 * mag2)))
            
            # Ensure we're getting the angle on the right side
            cross_product = (line1_vector[0] * line2_vector[1] - 
                           line1_vector[1] * line2_vector[0])
            if cross_product < 0:
                angle = 360 - angle
                
            # Take the smaller angle
            if angle > 180:
                angle = 360 - angle
            
            # Draw the final result
            pixmap = self.image_label.pixmap()
            painter = QPainter(pixmap)
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            
            # Draw both lines
            for line in self.angle_c_lines:
                painter.drawLine(line[0], line[1])
            
            # Draw angle text at the intersection point
            midpoint = QPoint(
                (self.angle_c_lines[0][0].x() + self.angle_c_lines[1][0].x()) // 2,
                (self.angle_c_lines[0][0].y() + self.angle_c_lines[1][0].y()) // 2
            )
            painter.drawText(midpoint, f"{angle:.1f}°")
            
            painter.end()
            self.image_label.setPixmap(pixmap)
            
            # Reset for next measurement
            self.angle_c_lines = []
            self.drawing_angle_c = False
            self.calculate_angleC_btn.setText('Calculate Angle C')
            self.image_label.setCursor(Qt.ArrowCursor)
            self.preview_pixmap = None

    def calculate_angleA(self):
        if self.image1 and self.image2:
            angle_diff = abs(self.image1_rotation - self.image2_rotation)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            QMessageBox.information(self, "Angle A", f"The sagittal pelvic rotation is {angle_diff} degrees.")
        else:
            QMessageBox.warning(self, "Warning", "Please load both images to calculate angle A.")

    def start_pan(self, event):
        if event.button() == Qt.LeftButton:
            self.panning = True
            self.panning_image = 1
            self.last_pos = event.pos()
        elif event.button() == Qt.RightButton:
            self.panning = True
            self.panning_image = 2
            self.last_pos = event.pos()

    def stop_pan(self, event):
        self.panning = False

    def pan_image(self, event):
        if self.panning:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            if self.panning_image == 1:
                self.image1_offset += QPoint(dx, dy)
            else:
                self.image2_offset += QPoint(dx, dy)
            self.last_pos = event.pos()
            self.update_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageOverlayTool()
    ex.show()
    sys.exit(app.exec_())