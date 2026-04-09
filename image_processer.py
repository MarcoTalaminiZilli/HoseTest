import cv2
import numpy as np

class ImageProcesser:
    def __init__(self):
        pass

    def main(self):
        pass


    def pipeline(self, img, lower_hsv, upper_hsv, kernel_size):
        hsv = self.hsv_conversion(img)
        mascara = self.mask(hsv, lower_hsv, upper_hsv)
        mascara_limpa = self.closing(mascara, kernel_size)
        mascara_limpa = self.opening(mascara_limpa, kernel_size)
        p1, p2 = self.pointsFinder(mascara_limpa)

        # Só tenta desenhar a linha se os pontos foram encontrados
        if p1 is not None and p2 is not None:
            img_final = self.lineDrawer(img.copy(), p1, p2)
        else:
            img_final = img.copy() # Retorna a imagem sem a linha
        return img_final, mascara_limpa

    # Método pra ler a imagem original
    def leitura(self, filepath):
        img = cv2.imread(filepath)
        if img is None:
            raise FileNotFoundError(f"Não foi possível ler a imagem em: {filepath}")
        return img

    # Método para converter a imagem de BGR para HSV
    def hsv_conversion(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Método para aplicar a máscara HSV
    def mask(self, hsv_img, lower_limit, upper_limit):
        return cv2.inRange(hsv_img, lower_limit, upper_limit)

    # Método para aplicar a operação de abertura
    def opening(self, bin_img, kernel_size):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel)

    # Método para aplicar a operação de fechamento
    def closing(self, bin_img, kernel_size):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)

    # Função auxiliar para calcular a média dos y-coordinates dos pixels brancos em uma coluna
    def get_average_y(self, col_index, mask_img):
        coluna = mask_img[:, col_index]
        pixels_brancos = np.where(coluna == 255)[0]
        if len(pixels_brancos) > 0:
            return np.mean(pixels_brancos)
        return None

    # Método para encontrar os pontos de orientação da mangueira
    def pointsFinder(self, bin_img):
        height, width = bin_img.shape
        x1 = int(width / 4)
        x2 = int(3 * width / 4)
        y1_raw = self.get_average_y(x1, bin_img)
        y2_raw = self.get_average_y(x2, bin_img)

        # Verificamos se AMBOS encontraram a cor laranja
        if y1_raw is not None and y2_raw is not None:
            p1 = (x1, int(y1_raw)) # Agora é seguro usar int()
            p2 = (x2, int(y2_raw))
            return p1, p2
        else:
            # Se não achou a cor em uma das colunas, retornamos None
            return None, None

    # Método para desenhar a linha de orientação na imagem original
    def lineDrawer(self, img, p1, p2):
        cv2.line(img, p1, p2, (255, 0, 0), 3)
        return img