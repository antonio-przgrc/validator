import cv2
import pyautogui
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import numpy as np
import pytesseract

def capturar_pantalla(zona, guardar=True, nombre_archivo="pictures/captura.png"):
    # Captura la pantalla completa
    #screenshot = pyautogui.screenshot(region=(110,465,1725,262))
    screenshot = pyautogui.screenshot(region=zona)
    #screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    imagen_gris = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)  # Convertir a escala de grises
    
    imagen_gris = preprocesar_imagen(imagen_gris)

    if guardar:
        cv2.imwrite(nombre_archivo, imagen_gris)  # Guardar la imagen

    return imagen_gris

def normalizar_texto(texto):
    # Convertir a mayúsculas para evitar diferencias de minúsculas/mayúsculas
    texto = texto.upper()
    # Reemplazar caracteres ambiguos
    texto = texto.replace('O', '0')  # Letra 'O' por número '0'
    texto = texto.replace('I', '1')  # Letra 'I' por número '1'
    texto = texto.replace('L', '1')  # Letra 'L' por número '1' (opcional)
    texto = texto.replace('S', '5')  # Letra 'S' por número '5' (opcional)
    return texto

def preprocesar_imagen(imagen):
    _, imagen_binaria = cv2.threshold(imagen, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    imagen_procesada = cv2.medianBlur(imagen_binaria, 3)
    return imagen_procesada

def detectar_texto(palabra_clave, zona, guardar_imagen=True):
    imagen = capturar_pantalla(zona, guardar=guardar_imagen, nombre_archivo="captura.png")
    
    # Usar OCR para extraer el texto y sus coordenadas
    resultados = pytesseract.image_to_data(imagen, output_type=pytesseract.Output.DICT)

    for i, texto in enumerate(resultados["text"]):
        texto_normalizado = normalizar_texto(texto)
        palabra_clave_normalizada = normalizar_texto(palabra_clave)

        if palabra_clave_normalizada.lower() in texto_normalizado.lower():
            x = resultados["left"][i]
            y = resultados["top"][i]
            ancho = resultados["width"][i]
            alto = resultados["height"][i]
            
            # Calcular el centro de la palabra detectada
            centro_x = x + ancho // 2
            centro_y = y + alto // 2
            
            print(f"Texto encontrado: '{texto}' en ({centro_x}, {centro_y})")
            
            return (zona[0]+centro_x, zona[1]+centro_y)

    print("Texto no encontrado")
    return False



class validator():
    def ubicacion_texto(self, zona):
        # Confirmamos que la aplicación está iniciada
        res = detectar_texto("SGA", zona)
        if res != False:
            # Comprobamos en qué apartado estamos
            res = detectar_texto("Entrega", zona)
            if res != False:
                pyautogui.click(res)
                time.sleep(0.5)
                return True
            else:
                check = False
                for i in ["Llegada", "Consultar","Generar"]:
                    res = detectar_texto(i,zona)
                    if res != False:
                        res = pyautogui.locateCenterOnScreen('pictures/menusalidas.png')
                        if res != False:
                            pyautogui.click(res)
                            time.sleep(0.5)
                            check = True
                            break

                if check == False:
                    return False
                else:
                    res = detectar_texto("Entrega", zona)
                    if res != False:
                        pyautogui.click(res)
                        time.sleep(0.5)
                        return True
        else:
            res = detectar_texto("Seleccionar", zona)
            if res != False:
                return True
            else:
                print("Ni idea de donde estoy primo")
                return False
        
    def __init__(self):
        # almacén
        self.almacen = '1'

        # posición en la aplicacion
        self.estado = ''

        # conexión a base de datos
        self.DB_SERVER = '212.81.135.183'
        self.DB_DATABASE = 'BD_SIERRASUR'
        self.DB_USER = 'SierraSur_Consulta'
        self.DB_PASSWORD = 'SierraSur2025@#'
        self.connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={self.DB_SERVER};DATABASE={self.DB_DATABASE};UID={self.DB_USER};PWD={self.DB_PASSWORD}"
        self.connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": self.connection_string})
        self.engine = create_engine(self.connection_url)

        # imágenes para búsqueda
        self.skritsga = 'pictures/skritsga.png'
        self.albarancliente = 'pictures/albarancliente.png'
        self.menualbarancliente = 'pictures/menualbarancliente.png'
        self.salidas = 'pictures/salidas.png'
        self.menusalidas = 'pictures/menusalidas.png'
        self.cli = 'pictures/cli.png'

        # zona de trabajo
        self.x = 110
        self.y = 110
        self.ancho = 1730
        self.alto = 860

        self.zona = (self.x, self.y, self.ancho, self.alto)

    def run(self):
        # Comprobar localización en la aplicación y abrir albaranes de cliente
        self.ubicacion_texto(self.zona)
        
        # Consulta SQL de albaranes pendientes de validar
        query1 = f'''
        SELECT acc.ACC_Codigo FROM AlbaranCliente_Cabecera acc
        WHERE acc.ACC_ValidadoSGA = 0 AND acc.ACC_Almacen = '{self.almacen}' AND acc.ACC_Abono = 0  AND acc.ACC_PedidoCliente IS NULL
        '''
        df = pd.read_sql(query1, self.engine)

        # Buscar albaranes de la lista en pantalla
        for i in df.iterrows():
            albaran = i[1].values[0]
            res = detectar_texto(albaran, self.zona)
            if res != False:
                # Comprobar si hay líneas validables
                query2 = f'''
                SELECT acl.ACL_Referencia, acl.ACL_Cantidad, acl.ACL_CantidadValidadaSGA FROM AlbaranCliente_Linea acl
                JOIN AlbaranCliente_Cabecera acc ON acc.ACC_Codigo = acl.ACL_Albaran
                WHERE acc.ACC_Codigo = '{albaran}' AND acl.ACL_Almacen = '{self.almacen}';
                '''
                referencias = pd.read_sql(query2, self.engine)
                pyautogui.click(res)


        

        # referencias = pd.read_sql(query, self.engine)

        # # Se comprueba que haya referencias validables y se decide cuál van a ser las ubicaciones donde extraerlas
        # df_obj = pd.DataFrame()
        # for ref in referencias.iterrows():
        #     if ref[1].ACL_Cantidad > ref[1].ACL_CantidadValidadaSGA:
        #         query = f'''
        #             SELECT au.ArU_Articulo, au.ArU_Ubicacion, au.ArU_Stock FROM Articulo_Ubicacion au 
        #             WHERE au.ArU_Articulo = '{ref[1].ACL_Referencia}' AND au.ArU_Almacen  = '{self.almacen}';
        #             '''
        #         df_ubi = pd.read_sql(query,self.engine)
                
        #         if (len(df_ubi) == 1) and (float(ref[1].ACL_Cantidad - ref[1].ACL_CantidadValidadaSGA) <= float(df_ubi['ArU_Stock'][0])):
        #             refe = ref[1].ACL_Referencia
        #             ubic = df_ubi['ArU_Ubicacion'][0]
        #             cant = ref[1].ACL_Cantidad - ref[1].ACL_CantidadValidadaSGA
        #             df_obj = pd.concat([df_obj, pd.DataFrame([[refe,ubic,cant]], columns=["Referencia","Ubicacion","Cantidad"])])
        #             df_obj = df_obj.reset_index(drop=True)
        # print(df_obj)
        # pyautogui.click(pos)
        # pyautogui.moveTo(10,10)
        # time.sleep(2)

        # pos = detectar_texto(df_obj['Referencia'][0], self.zona)
        # pyautogui.click(pos)

app = validator()
app.run()