import cv2
from PIL import Image, ImageEnhance, ImageDraw
import matplotlib.pyplot as plt

from pdf2image import convert_from_path
import pytesseract

import glob
import numpy as np
import pandas as pd


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r'D:\Users\chelsy.mena\Downloads\poppler-22.04.0\Library\bin'

informes = glob.glob(r'D:\Users\chelsy.mena\OneDrive - Centro de Servicios Mundial SAS\Documentos\Proyectos\HSE\Residuos\Remisiones Julio\*')

def delinear_pdf(archivo):

    # Cargar un PDF
    paginas = convert_from_path(pdf_path=archivo, poppler_path=poppler_path)

    # Convertir pagina a blanco y negro
    img = paginas[0].convert('L')

    # Encontrar las lineas
    ## Pasar a array de numpy
    img = np.array(img)

    ## Quitar fondo e invertir colores
    th, threshed = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)

    ## (5) Encontrar los bordes superiores e inferiores de las lineas
    hist = cv2.reduce(threshed,1, cv2.REDUCE_AVG).reshape(-1)

    th = 2
    H, W = img.shape[:2]
    uppers = [y for y in range(H-1) if hist[y]<=th and hist[y+1]>th]
    lowers = [y for y in range(H-1) if hist[y]>th and hist[y+1]<=th]

    return img, uppers, lowers

def replicar_tabla(img, uppers, lowers):

    # crear Tabla para guardar ahi
    tabla = pd.DataFrame({'RESIDUO': [], 'ESTADO FÍSICO': [], 'EMBALAJE': [], 'RECOGIDO':[], 'UNIDADES':[], 'TIPOLOGÍA':[]})
    
    # Cortar por linea
    for i in range(11, len(uppers)):
        area = (0, uppers[i]-5, 1600, lowers[i]+5)
        cropped = Image.fromarray(np.uint8(img)).crop(area)
        text = pytesseract.image_to_string(cropped)

        # parar cuando termina la tabla de residuos
        if 'CONSTANCIA' in text:
                break
        else:
            # Partir verticalmente
            limites = [0, 392, 590, 785, 915, 1055, 1600]

            linea = []
            for i in range(1, len(limites)):
                area = (limites[i-1], 0, limites[i], cropped.size[1])
                cropped_celda = Image.fromarray(np.uint8(cropped)).crop(area)

                text = pytesseract.image_to_string(cropped)
                linea.append(text.replace("\n", ""))
            
            tabla.loc[tabla.shape[0]+1]= linea

    return tabla

archivo = informes[0]
img, lims_sup, lims_inf = delinear_pdf(archivo)
guia = replicar_tabla(img, lims_sup, lims_inf)

guia.to_clipboard()