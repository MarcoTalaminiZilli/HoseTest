import cv2
import numpy as np
import math

# Read the original image
img_original = cv2.imread('hose.jpg')

# Convert the image from BGR to HSV color space
img_hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)

# Define the lower and upper bounds for the color of the hose (adjust as needed)
lower_hose = np.array([1, 100, 50])  # Example lower
upper_hose = np.array([25, 255, 255])  # Example upper

# Create a mask using the defined color range
mask = cv2.inRange(img_hsv, lower_hose, upper_hose)

# Apply morphological operations to clean up the mask
kernel = cv2.getStructuringElement(cv2.MORPH_RECT , (12, 12))
img_closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT , (5, 5))
img_opening = cv2.morphologyEx(img_closing, cv2.MORPH_OPEN , kernel)

# --------------------------- Calculate the angle of the hose -----------------------------
height, width = img_opening.shape
x1 = int(width / 4)
x2 = int(3 * width / 4)

# Function to calculate the average y-coordinate of the white pixels in a given column
def get_average_y(col_index, mask_img):
    coluna = mask_img[:, col_index]
    pixels_brancos = np.where(coluna == 255)[0]
    if len(pixels_brancos) > 0:
        return np.mean(pixels_brancos)
    return None

y1 = get_average_y(x1, img_opening)
y2 = get_average_y(x2, img_opening)

# Calculate the angle of the hose using the two points (x1, y1) and (x2, y2)
if y1 is not None and y2 is not None:
    delta_y = y2 - y1
    delta_x = x2 - x1
    
    # Angulo em radianos e depois para graus
    angulo_rad = math.atan2(delta_y, delta_x)
    angulo_graus = math.degrees(angulo_rad)
    
    # Inverter o sinal do ângulo se necessário (OpenCV tem Y crescendo para baixo)
    angulo_final = -angulo_graus 
    
    print(f"Ângulo de orientação: {angulo_final:.2f} graus")


# Display the original image and the processed masks, along with the orientation line
cv2.imshow('Original Image', img_original)
cv2.imshow('Hose Mask', mask)
cv2.imshow('Hose Mask (Closed)', img_closing)
cv2.imshow('Hose Mask (Opened)', img_opening)

# Draw a line on the original image to visualize the orientation of the hose
cv2.line(img_original, (x1, int(y1)), (x2, int(y2)), (255, 0, 0), 3)
cv2.imshow('Hose Orientation', img_original)

cv2.waitKey(0)
cv2.destroyAllWindows()