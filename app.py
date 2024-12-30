from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__, template_folder='templates')

# Carica il modello
model = load_model('model/digit_recognition_model.h5')

@app.route('/')
def index():
    return render_template('index.html')  # Servi il template HTML

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_data = data['image']
    
    # Stampa i primi 100 caratteri dei dati base64 per il debug
    #print(f"Immagine base64 ricevuta (primi 100 caratteri): {image_data[:100]}")

    # Decodifica l'immagine base64
    image_data = image_data.split(",")[1]  # Rimuovi il prefisso "data:image/png;base64,"
    
    try:
        # Decodifica l'immagine
        decoded_image = base64.b64decode(image_data)
        #print("Immagine decodificata correttamente! Lunghezza dei dati:", len(decoded_image))

        # Apri l'immagine da byte
        image = Image.open(io.BytesIO(decoded_image))
        #print("Immagine caricata correttamente!")
        #print(f"Dimensioni dell'immagine dopo la decodifica: {image.size}")

    except Exception as e:
        return jsonify({'error': 'Errore nel caricare l\'immagine', 'message': str(e)})

    # Rimuovere la trasparenza (se presente) e impostare lo sfondo bianco
    if image.mode == 'RGBA':
        # Crea una nuova immagine bianca con lo stesso dimensione
        background = Image.new('RGB', image.size, (255, 255, 255))  # Impostiamo lo sfondo bianco
        # Incolla l'immagine originale sopra il nuovo sfondo bianco
        background.paste(image, (0, 0), image)
        image = background
        #print("Trasparenza rimossa, immagine convertita in RGB con sfondo bianco")

    # Mostra l'immagine per il debug (prima della normalizzazione)
    image.show()

    # Ridimensiona l'immagine a 28x28 (formato richiesto dal modello)
    image = image.resize((28, 28))
    #print("Immagine ridimensionata a 28x28.")
    
    # Salva l'immagine ridimensionata per il debug
    #image.save("resized_image.png")
    #print("Immagine ridimensionata salvata come 'resized_image.png' per il debug")

    # Converti in scala di grigi (il modello si aspetta immagini in scala di grigi)
    image = image.convert('L')  # Converte in scala di grigi
    #print("Immagine convertita in scala di grigi")
    # Mostra l'immagine in scala di grigi per il debug
    image.show()

    # **Debug**: Salva l'immagine prima della normalizzazione
    #image.save("grayscale_image.png")
    #print("Immagine in scala di grigi salvata come 'grayscale_image.png'")

    # Controlliamo i valori dei pixel prima della normalizzazione
    image_array = np.array(image)  # Otteniamo l'array dei pixel
    #print(f"Array dei pixel prima della normalizzazione:\n{image_array}")
    image_array = 255 - image_array
    # Verifica dei valori dei pixel
    #min_pixel_value = np.min(image_array)
    #max_pixel_value = np.max(image_array)
    #print(f"Valori minimi e massimi dei pixel (prima della normalizzazione): {min_pixel_value}, {max_pixel_value}")

    # Normalizzazione
    image_array = image_array / 255.0  # Normalizzazione dei pixel (tra 0 e 1)
    #print(f"Array dei pixel dopo la normalizzazione:\n{image_array}")

    # Verifica dei valori dei pixel dopo la normalizzazione
    #min_pixel_value = np.min(image_array)
    #max_pixel_value = np.max(image_array)
    #print(f"Valori minimi e massimi dei pixel (dopo la normalizzazione): {min_pixel_value}, {max_pixel_value}")

    # Ridimensiona per adattarlo al modello
    image_array = image_array.reshape(1, 28, 28, 1)  # Reshaping per il modello (aggiungi la dimensione del batch)

    # Stampa la forma dell'array dell'immagine
    #print(f"Array immagine preprocessata: {image_array.shape}")

    # Fai la previsione
    prediction = model.predict(image_array)
    
    # Stampa le probabilità per ciascuna cifra (0-9)
    print(f"Probabilità per ciascuna cifra: {prediction}")
    
    # Ottieni la previsione finale (cifra da 0 a 9) e la probabilità associata
    predicted_digit = np.argmax(prediction)  # Cifra predetta
    predicted_probability = prediction[0][predicted_digit]  # Probabilità associata

    # Restituisci la previsione e la probabilità come risposta JSON
    return jsonify({
        'prediction': int(predicted_digit),
        'probability': float(predicted_probability)
    })

if __name__ == '__main__':
    app.run(debug=True)