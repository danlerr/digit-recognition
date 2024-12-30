const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const predictButton = document.getElementById('predictButton');
const resultText = document.getElementById('predictionResult');
const confidenceText = document.getElementById('confidenceResult');
const clearButton = document.getElementById('clearButton');

let isDrawing = false;

// Imposta colore, spessore e arrotondamento delle linee
ctx.lineWidth = 15;  // Imposta lo spessore delle linee
ctx.lineCap = 'round';  // Rende le linee arrotondate
ctx.strokeStyle = 'black';  // Colore della linea (nero)

// Inizia il disegno sul canvas
canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    ctx.moveTo(e.offsetX, e.offsetY);
});

// Disegna sul canvas mentre il mouse si muove
canvas.addEventListener('mousemove', (e) => {
    if (isDrawing) {
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
    }
});

// Interrompe il disegno quando il mouse viene rilasciato
canvas.addEventListener('mouseup', () => {
    isDrawing = false;
});

predictButton.addEventListener('click', () => {
    // Crea un canvas temporaneo di dimensioni 28x28
    const centeredCanvas = document.createElement('canvas');
    const centeredCtx = centeredCanvas.getContext('2d');
    centeredCanvas.width = 28;
    centeredCanvas.height = 28;

    // Ottieni i dati dell'immagine disegnata
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    
    // Trova i bordi dell'immagine disegnata (per determinare il rettangolo di contenuto)
    const data = imageData.data;
    let top = canvas.height, bottom = 0, left = canvas.width, right = 0;

    // Scorri i pixel per determinare i bordi (dove c'è del colore disegnato)
    for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
            const index = (y * canvas.width + x) * 4;
            const alpha = data[index + 3];
            if (alpha > 0) { // Se c'è un pixel disegnato
                if (y < top) top = y;
                if (y > bottom) bottom = y;
                if (x < left) left = x;
                if (x > right) right = x;
            }
        }
    }

    // Calcola la larghezza e l'altezza dell'immagine disegnata
    const width = right - left;
    const height = bottom - top;

    // Se l'immagine è troppo piccola o vuota, mostra un messaggio di errore
    if (width === 0 || height === 0) {
        resultText.textContent = 'Disegna qualcosa prima di fare una previsione.';
        confidenceText.textContent = '';
        return;
    }

    // Calcola il fattore di ridimensionamento per adattare l'immagine disegnata a 28x28
    const scale = Math.min(centeredCanvas.width / width, centeredCanvas.height / height);
    const scaledWidth = width * scale;
    const scaledHeight = height * scale;

    // Calcola la posizione per centrare l'immagine
    const offsetX = (centeredCanvas.width - scaledWidth) / 2;
    const offsetY = (centeredCanvas.height - scaledHeight) / 2;

    // Centra l'immagine disegnata all'interno del nuovo canvas 28x28
    centeredCtx.clearRect(0, 0, centeredCanvas.width, centeredCanvas.height);
    centeredCtx.drawImage(
        canvas,
        left, top, width, height, // Sorgente: la parte disegnata dell'immagine
        offsetX, offsetY,         // Destinazione: centrato nel nuovo canvas
        scaledWidth, scaledHeight // Nuove dimensioni dell'immagine ridimensionata
    );

    // Converte il canvas centrato in base64
    const centeredImageData = centeredCanvas.toDataURL();

    // Invia l'immagine centrata al server per la previsione
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: centeredImageData })
    })
    .then(response => response.json())
    .then(data => {
        // Mostra il risultato della previsione
        resultText.textContent = `Predizione: ${data.prediction}`;
        confidenceText.textContent = `Probabilità: ${(data.probability * 100).toFixed(2)}%`;
    })
    .catch(error => {
        console.error('Errore:', error);
        resultText.textContent = 'Errore nella previsione. Riprova.';
        confidenceText.textContent = '';
    });
});

// Funzione per pulire il canvas
clearButton.addEventListener('click', () => {
    // Pulisce completamente la canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Reset delle variabili di disegno
    isDrawing = false;

    // Reset dei testi della previsione e probabilità
    resultText.textContent = 'La previsione sarà mostrata qui.';
    confidenceText.textContent = '';

    // Rimuovi l'immagine di debug se presente
    const imgElements = document.querySelectorAll('img');
    imgElements.forEach(img => img.remove());

    // Aggiungi un piccolo ritardo prima di permettere un nuovo disegno
    setTimeout(() => {
        // Rendi sicuro che nessuna vecchia "traccia" del disegno sia presente
        ctx.beginPath();
    }, 10);
});