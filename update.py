# -*- coding: utf-8 -*-

import sys
import time
import os
import requests
import zipfile
import subprocess

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QProcess
from PyQt5 import uic
from PyQt5.QtGui import QPixmap

from src.pipelinepro.settings import DEBUG

class Progreso_Update(QThread):
    def __init__(self, ventana):
        self.ventana = ventana
        super().__init__()

    actualizar_progreso = pyqtSignal(int)

    def run(self):
        time.sleep(1)
        self.ventana.kraken_off()
        self.actualizar_progreso.emit(20)
        time.sleep(1)

        self.ventana.download_code()
        self.actualizar_progreso.emit(40)
        # time.sleep(1)

        self.ventana.unZip_kraken()
        self.actualizar_progreso.emit(60)
        time.sleep(1)

        self.ventana.launch_kraken()
        self.actualizar_progreso.emit(80)
        time.sleep(1)

        self.ventana.off_update()
        self.actualizar_progreso.emit(100)
        time.sleep(1)


class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        root = os.getcwd()
        path_to_ui = os.path.join(f'{root}', 'src', 'ui', 'update_ui.ui').replace('\\', '/')
        uic.loadUi(path_to_ui, self)

        self.path_to_image = os.path.join('src', 'ui', 'images', 'Kraken_icon.ico')
        self.pixmap = QPixmap(self.path_to_image)
        self.logo_kraken.setPixmap(self.pixmap)
        self.logo_kraken.setScaledContents(True)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Los demás widgets se manejan de la misma manera
        self.copiar_archivos()


    def copiar_archivos(self):
        self.progreso_thread = Progreso_Update(self)
        self.progreso_thread.actualizar_progreso.connect(self.actualizar_progreso)
        self.progreso_thread.start()

    def actualizar_progreso(self, valor):
        self.barra_progreso.setValue(valor)
        if valor == 100:
            self.close_app()

    def iniciar_kraken(self):
        command = f'{self.exe}'
        # QProcess().startDetached(command)
        pass

    # ============= PHASES ============
    def kraken_off(self):
        phase = 'Asegurar que Kraken está cerrado'
        print(phase)

    def download_code(self):
        phase = 'Descargar código nuevo'
        print(phase)
        descargar_kraken_zip()

    def unZip_kraken(self):
        phase = 'Descomprimir'
        print(phase)

    def launch_kraken(self):
        phase = 'Encender Kraken nuevo (Quitar)'
        print(phase)

    def off_update(self):
        phase = 'Apagar Instalador (Quitar)'
        print(phase)

    def close_app(self):
        # Iniciar hilo independiente
        pwd = os.getcwd().replace('\\', '/')
        try:
            root = os.getcwd()
            update_dependencies = os.path.join(f'{root}', 'update_dependences.bat')
            os.startfile(update_dependencies)
            print('Actualizando dependencias')
        except:
            print('Error al intentar actualizar dependencias')
            pass
        command = os.path.join(f'{os.path.dirname(pwd)}', 'Run_Kraken.lnk')
        os.startfile(command)
        command = os.path.join(f'{os.path.dirname(pwd)}', 'Kraken_Manager.lnk')
        os.startfile(command)

        # Cerrar aplicación
        self.close()


def descargar_kraken_zip():
    if DEBUG:
        url = 'https://github.com/michelcub/staging/raw/main/kraken_win_64.zip'
    else:
        url = 'https://unlogic.io/static/kraken/kraken_win_64.zip'

    installation_path = os.path.dirname(os.getcwd()).replace('\\', '/')
    nombre_temporal = installation_path + '/kraken_update.zip'
    # Descargar el archivo ZIP desde la URL
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        # Guardar el contenido descargado en un archivo temporal
        with open(nombre_temporal, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        # Descomprimir el archivo ZIP en la carpeta de destino
        with zipfile.ZipFile(nombre_temporal, "r") as zip_ref:
            zip_ref.extractall(installation_path)
        os.remove(nombre_temporal)
    else:
        print("  Failed to download the ZIP file. Status code")


def main():
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.move(app.primaryScreen().geometry().center() - ventana.rect().center())

    ventana.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
