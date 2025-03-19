import pyodbc
import cv2
import pyautogui
import time
# Consulta básica a la base de datos (modificar más tarde)
# def consulta():
#     try:
#         with pyodbc.connect(conn_str) as conn:
#             cursor = conn.cursor()
#             cursor.execute(consulta)  # Modifica la consulta según necesites
#             datos = cursor.fetchall()
#             for linea in datos:
#                 linea[1] = linea[1].replace(microsecond=0)
#         return datos
#     except Exception as e:
#         return [], []

class validator():
    def ubicacion_app(self):
        try:
            pyautogui.locateOnScreen(self.skritsga, confidence=0.8)
            try:
                pyautogui.locateOnScreen(self.salidas, confidence=0.8)
                self.posicion = 'inicio_salidas'
            except:
                pos = pyautogui.locateCenterOnScreen(self.menusalidas,confidence=0.8)
                pyautogui.click(pos)
                time.sleep(1)
                try:
                    pyautogui.locateOnScreen(self.salidas, confidence=0.8)
                    self.posicion = 'inicio_salidas'
                except:
                    print('No responde la pantalla')
                    exit
            print('Aplicación en menú inicio')
        except:
            try:
                pyautogui.locateOnScreen(self.albarancliente, confidence=0.8)
                print('Aplicación en menú albaranes')
                self.posicion = 'menu_albaran'
            except:
                print('No se encuentra aplicación')
                exit

    def __init__(self):
        # almacén
        self.almacen = '1'

        # posición en la aplicacion
        self.posicion = ''

        # conexión a base de datos
        self.DB_SERVER = '212.81.135.183'
        self.DB_DATABASE = 'BD_SIERRASUR'
        self.DB_USER = 'SierraSur_Consulta'
        self.DB_PASSWORD = 'SierraSur2025@#'
        self.conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.DB_SERVER};DATABASE={self.DB_DATABASE};UID={self.DB_USER};PWD={self.DB_PASSWORD}'
        
        # imágenes para búsqueda
        self.skritsga = 'pictures/skritsga.png'
        self.albarancliente = 'pictures/albarancliente.png'
        self.menualbarancliente = 'pictures/menualbarancliente.png'
        self.salidas = 'pictures/salidas.png'
        self.menusalidas = 'pictures/menusalidas.png'

        # Comprobar localización en la aplicación
        self.ubicacion_app()



app = validator()