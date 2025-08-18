import cv2
import numpy as np

# Create a black image
width, height = 640, 480
image = np.zeros((height, width, 3), dtype=np.uint8)

# Save the image
cv2.imwrite("dummy_frame.jpg", image)
print("Dummy image created.")
