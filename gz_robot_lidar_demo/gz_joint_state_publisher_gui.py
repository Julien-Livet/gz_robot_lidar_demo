import sys
import subprocess
import textwrap
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSlider, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
import math


class RobotSliderGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Robot Joint Control via gz topic")
        self.joint_labels = ['joint_1_s', 'joint_2_l', 'joint_3_u', 'joint_4_r', 'joint_5_b', 'joint_6_t']
        self.values = [0.0] * 6  # En radians
        self.slider_min = -180  # -180° pour le slider
        self.slider_max = 180   # 180° pour le slider

        self.layout = QVBoxLayout()
        self.sliders = []
        self.labels = []
        self.lineedits = []

        for i, joint_name in enumerate(self.joint_labels):
            joint_layout = QHBoxLayout()

            label = QLabel(f"{joint_name}: 0.00°")
            label.setFixedWidth(100)
            self.labels.append(label)
            joint_layout.addWidget(label)

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(self.slider_min)
            slider.setMaximum(self.slider_max)
            slider.setValue(0)
            slider.setSingleStep(1)
            slider.valueChanged.connect(lambda value, i=i: self.slider_changed(i, value))
            slider.setFixedWidth(250)
            joint_layout.addWidget(slider)
            self.sliders.append(slider)

            lineedit = QLineEdit("0.00")
            lineedit.setFixedWidth(60)
            lineedit.editingFinished.connect(lambda i=i: self.lineedit_changed(i))
            self.lineedits.append(lineedit)
            joint_layout.addWidget(lineedit)

            self.layout.addLayout(joint_layout)

        # Add buttons
        btn_layout = QHBoxLayout()
        center_btn = QPushButton("Center Joints")
        center_btn.clicked.connect(self.center_joints)
        btn_layout.addWidget(center_btn)

        random_btn = QPushButton("Randomize")
        random_btn.clicked.connect(self.randomize_joints)
        btn_layout.addWidget(random_btn)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

        # Timer for continuous publishing
        self.timer = QTimer()
        self.timer.timeout.connect(self.publish_command)
        self.timer.start(200)  # 5 Hz

    def degrees_to_radians(self, degrees):
        return degrees * (math.pi / 180)

    def radians_to_degrees(self, radians):
        return radians * (180 / math.pi)

    def slider_changed(self, index, value):
        # Conversion en degrés
        angle_deg = value
        # Conversion en radians pour Gazebo
        angle_rad = self.degrees_to_radians(angle_deg)
        self.values[index] = angle_rad
        self.labels[index].setText(f"{self.joint_labels[index]}: {angle_deg:.2f}°")
        self.lineedits[index].setText(f"{angle_deg:.2f}")

    def lineedit_changed(self, index):
        try:
            # Convertir l'input en degrés
            value = float(self.lineedits[index].text())
            if -180 <= value <= 180:
                # Convertir en radians pour Gazebo
                angle_rad = self.degrees_to_radians(value)
                self.values[index] = angle_rad
                self.sliders[index].setValue(int(value))
                self.labels[index].setText(f"{self.joint_labels[index]}: {value:.2f}°")
            else:
                self.lineedits[index].setText(f"{self.radians_to_degrees(self.values[index]):.2f}")  # Reset to previous
        except ValueError:
            self.lineedits[index].setText(f"{self.radians_to_degrees(self.values[index]):.2f}")  # Invalid input, reset

    def center_joints(self):
        for i in range(6):
            self.sliders[i].setValue(0)  # Will trigger slider_changed

    def randomize_joints(self):
        for i in range(6):
            rand_val = random.uniform(-180, 180)  # Aléatoire en degrés
            self.sliders[i].setValue(int(rand_val))  # Will trigger slider_changed

    def publish_command(self):
        # Convertir les valeurs de chaque joint en radians
        position_lines = "\n".join([f"      positions: {v}" for v in self.values])
        joint_lines = "\n".join([f"  joint_names: \"{name}\"" for name in self.joint_labels])
        cmd = textwrap.dedent(f"""
            gz topic -t "/model/gz_ma2010/joint_trajectory" -m gz.msgs.JointTrajectory -p '
            {joint_lines}
            points {{
        {position_lines}
              time_from_start {{
                sec: 1
                nsec: 0
              }}
            }}'
        """)
        subprocess.run(cmd, shell=True, executable='/bin/bash')


def main():
    app = QApplication(sys.argv)
    gui = RobotSliderGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
