# 🎨 Assets - Tech Explanation Service

Questa cartella contiene le risorse grafiche del progetto.

---

## 🤖 Logo

### **File Disponibili:**

- `logo.svg` - Logo vettoriale 120×120 px (✅ Creato)
- `logo.png` - Logo raster 120×120 px (⏳ Da generare)
- `view_logo.html` - Preview interattiva con conversione SVG→PNG

---

## 📐 **Specifiche Logo**

| Proprietà | Valore |
|-----------|--------|
| **Dimensioni** | 120 × 120 pixels |
| **Formato principale** | SVG (Scalable Vector Graphics) |
| **Stile** | Robot stilizzato con gradient viola/blu |
| **Ispirazione** | Emoji 🤖 usata nel progetto |
| **Background** | Gradient (#667eea → #764ba2) |
| **Elementi** | Antenna, testa, corpo, braccia, gambe |

---

## 🖼️ **Come Visualizzare il Logo**

### **Metodo 1: Browser (Consigliato)**

```bash
# Da terminale, apri il file HTML
open assets/view_logo.html           # macOS
xdg-open assets/view_logo.html       # Linux
start assets/view_logo.html          # Windows
```

Oppure doppio-click su `view_logo.html` dal Finder/Explorer.

---

## 💾 **Come Ottenere la Versione PNG**

### **Metodo 1: Browser (Più Facile)**

1. Apri `assets/view_logo.html` nel browser
2. Clicca il pulsante **"🖼️ Convert to PNG"**
3. Il file `tech-explanation-logo.png` verrà scaricato automaticamente
4. Rinominalo in `logo.png` e spostalo in `assets/`

### **Metodo 2: Script Python**

```bash
# Installa dipendenze (solo la prima volta)
pip install cairosvg pillow

# Esegui lo script di conversione
python scripts/generate_logo_png.py
```

Il file `logo.png` verrà creato automaticamente in `assets/`.

### **Metodo 3: Convertitore Online**

1. Visita: https://cloudconvert.com/svg-to-png
2. Upload: `assets/logo.svg`
3. Imposta dimensioni: **120 × 120 px**
4. Download e salva come: `assets/logo.png`

### **Metodo 4: Inkscape (Se Installato)**

```bash
inkscape -w 120 -h 120 assets/logo.svg -o assets/logo.png
```

---

## 🎯 **Utilizzo del Logo**

### **README.md / Documentazione:**

```markdown
![Logo](assets/logo.png)
```

### **HTML:**

```html
<img src="assets/logo.svg" alt="Tech Explanation Service" width="120" height="120">
```

### **Gradio UI:**

```python
gr.Image("assets/logo.png", show_label=False, height=120)
```

### **FastAPI Login Page:**

```html
<img src="/assets/logo.svg" alt="Logo" style="width: 120px; height: 120px;">
```

---

## 🎨 **Palette Colori del Logo**

| Colore | Hex Code | Utilizzo |
|--------|----------|----------|
| **Viola Scuro** | `#667eea` | Background gradient (start) |
| **Viola Intenso** | `#764ba2` | Background gradient (end) |
| **Blu Chiaro** | `#e0e7ff` | Robot body (gradient start) |
| **Blu Medio** | `#c7d2fe` | Robot body (gradient end) |
| **Blu Accento** | `#3b82f6` | Eyes, details |
| **Indaco** | `#6366f1` | Chest panel, mouth |
| **Giallo** | `#fbbf24` | Antenna tip |

---

## 📁 **Struttura Assets**

```
assets/
├── README.md              # Questa documentazione
├── logo.svg              # ✅ Logo vettoriale (creato)
├── logo.png              # ⏳ Logo raster (da generare)
└── view_logo.html        # 🖼️ Preview e converter
```

---

## 🔄 **Rigenerare il Logo**

Se vuoi modificare il logo:

1. Edita `assets/logo.svg` con un editor SVG (Inkscape, Figma, etc.)
2. Oppure modifica il codice SVG direttamente (è XML)
3. Rigenera il PNG con uno dei metodi sopra

### **Elementi SVG da Modificare:**

- **Background**: `<rect width="120" height="120" rx="24" fill="url(#bg-gradient)"/>`
- **Robot Head**: `<rect x="40" y="30" width="40" height="35" rx="6" .../>`
- **Eyes**: `<circle cx="50" cy="45" r="5" .../>`
- **Antenna**: `<line x1="60" y1="20" x2="60" y2="30" .../>`

---

## ✅ **Checklist**

- [x] Logo SVG creato (120×120 px)
- [x] Design robot stilizzato con gradient
- [x] Preview HTML interattiva
- [x] Script di conversione Python
- [ ] Logo PNG generato (da fare)
- [ ] Logo usato in README.md principale
- [ ] Logo usato nella login page di FastAPI

---

## 📚 **Risorse**

- [SVG Tutorial](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial)
- [SVG to PNG Converter](https://cloudconvert.com/svg-to-png)
- [Inkscape](https://inkscape.org/) - Editor SVG gratuito
- [Figma](https://www.figma.com/) - Design tool online

