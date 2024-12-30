import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.datasets import mnist
from PIL import Image
import matplotlib.pyplot as plt

# Carica il modello
model = load_model('model/digit_recognition_model.h5')

# Carica il dataset MNIST
(_, _), (x_test, y_test) = mnist.load_data()

# Preprocessa un'immagine di test
test_image = x_test[34].reshape(1, 28, 28, 1) / 255.0

# Fai la previsione
prediction = model.predict(test_image)
predicted_digit = np.argmax(prediction)

# Visualizza l'immagine e la previsione
plt.imshow(x_test[34], cmap='gray')
plt.title(f'Predizione: {predicted_digit}')
plt.show()
