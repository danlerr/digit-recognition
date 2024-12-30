import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

# 1. Caricare il dataset MNIST
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# 2. Preprocessare i dati
x_train = x_train.reshape(-1, 28, 28, 1) / 255.0
x_test = x_test.reshape(-1, 28, 28, 1) / 255.0
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)

# 3. Creare il modello
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')  # 10 classi (cifre da 0 a 9)
])

# 4. Compilare il modello
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 5. Addestrare il modello
model.fit(x_train, y_train, epochs=5, validation_data=(x_test, y_test))

# 6. Valutare il modello
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Accuratezza sul test: {test_acc:.2f}")

# 7. Visualizzare alcune predizioni
predictions = model.predict(x_test[:5])
for i, pred in enumerate(predictions):
    plt.imshow(x_test[i].reshape(28, 28), cmap='gray')
    plt.title(f"Predizione: {pred.argmax()}")
    plt.show()

model.save('model/digit_recognition_model.h5')