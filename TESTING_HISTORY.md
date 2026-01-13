# Testing History Persistence

## 🧪 Come Testare la Persistenza della History

### Test Locale (prima del deploy su HF Spaces)

1. **Avvia l'app localmente**:
   ```bash
   conda activate tech-explain
   python spaces_app.py
   ```

2. **Fai una nuova domanda**:
   - Inserisci un topic (es. "Docker")
   - Attendi la risposta completa
   - Guarda i log nel terminale per conferma salvataggio

3. **Verifica il dropdown**:
   - Il dropdown "Previous chats" dovrebbe aggiornarsi
   - Il nuovo topic dovrebbe apparire nella lista

4. **Reload della pagina (F5)**:
   - La history dovrebbe essere ancora visibile
   - Il dropdown dovrebbe mostrare tutti i topic precedenti

5. **Carica una chat precedente**:
   - Seleziona un topic dal dropdown
   - Dovrebbe apparire la spiegazione completa (non solo una frase)

### Debug Logs da Verificare

Durante l'uso, nel terminale dovresti vedere:

```
🚀 Nuova richiesta: 'Docker'
   History corrente: 2 items
   ✅ Generazione completata: 1234 chars
✅ History salvata su HF Hub (3 items)
   📚 History aggiornata: 3 items (era 2)
   🔄 Dropdown aggiornato con 3 topics
```

Quando selezioni una chat precedente:

```
🔍 Ricerca chat per topic: 'Docker'
   History ha 3 items
   ✅ Trovata! Explanation: 1234 chars
```

### Problemi Comuni

#### ❌ "History si azzera dopo reload"

**Causa**: Cache HF Hub non invalidata
**Soluzione**: Già fixato con `force_download=True`

#### ❌ "Chat precedente mostra solo una frase"

**Causa**: Explanation troncata o non caricata
**Debug**: 
- Guarda i logs: "✅ Trovata! Explanation: X chars"
- Se X è piccolo (< 100), il problema è nel salvataggio
- Se X è grande ma l'output è breve, problema di visualizzazione

#### ❌ "Nuove chat non appaiono nel dropdown"

**Causa**: Dropdown non aggiornato dinamicamente
**Debug**:
- Verifica log: "🔄 Dropdown aggiornato con X topics"
- Se appare ma dropdown non cambia, è un bug Gradio

### Test su HF Spaces

**IMPORTANTE**: Quando l'app gira su HF Spaces, il file `history.json` 
deve essere creato manualmente nello Space prima del primo avvio.

1. Vai su HF Space → Files
2. Crea `history.json` con:
   ```json
   []
   ```
3. Riavvia lo Space
4. Ora la history dovrebbe persistere

---

## 🔧 Configurazione HF Hub

### Variabili d'ambiente richieste:

```python
HF_USERNAME = "gianmarioiamoni67"
HF_REPO = "tech-explanation-service"
HISTORY_FILE = "history.json"
```

### Token (opzionale):

Se l'upload fallisce, setta `HF_TOKEN` come secret nello Space:

```
Settings → Repository secrets → New secret
Name: HF_TOKEN
Value: hf_xxxxxxxxxxxxx
```

---

## 📊 Verifica Manuale della History

```bash
python -c "
from app.services.tech_explanation_service import TechExplanationService
service = TechExplanationService()
history = service.load_history()
for topic, explanation in history:
    print(f'{topic}: {len(explanation)} chars')
"
```

