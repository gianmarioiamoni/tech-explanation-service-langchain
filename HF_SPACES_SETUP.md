# 🚀 Configurazione Hugging Face Spaces

## ⚠️ Setup Iniziale per History Persistence

Per far funzionare la persistenza della history su HF Spaces, segui questi passaggi:

### 📋 Step 1: Verifica lo Space su Hugging Face

1. Vai su: https://huggingface.co/spaces/gianmarioiamoni67/tech-explanation-service
2. Verifica che lo Space esista e sia accessibile
3. Se non esiste, crealo:
   - Vai su https://huggingface.co/new-space
   - Name: `tech-explanation-service`
   - SDK: `Gradio`
   - Python version: `3.11`

---

### 🔑 Step 2: Configura il Token HF (CRUCIALE)

Il token HF è necessario per scrivere file nello Space.

#### Opzione A: Token come Secret (RACCOMANDATO per HF Spaces)

1. Vai nelle **Settings** dello Space
2. Sezione **Repository secrets**
3. Clicca su **New secret**
4. Nome: `HF_TOKEN`
5. Valore: Il tuo token HF (crea uno su https://huggingface.co/settings/tokens)
   - Tipo token: **Write** (non Read-only!)
6. Salva

#### Opzione B: Token nel .env (solo per sviluppo locale)

```bash
# .env (NON committare questo file!)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

**⚠️ IMPORTANTE**: Il token deve avere permessi di **WRITE** per permettere upload di file.

---

### 📁 Step 3: Assicurati che history.json esista nello Space

Il file `history.json` deve esistere nel repository dello Space.

#### Metodo 1: Commit dal tuo repository locale

```bash
# Aggiungi history.json al repository
git add history.json
git commit -m "Add empty history.json for persistence"
git push origin main
```

#### Metodo 2: Crealo direttamente su HF (interfaccia web)

1. Vai allo Space: https://huggingface.co/spaces/gianmarioiamoni67/tech-explanation-service
2. Tab **Files and versions**
3. Clicca su **Add file** → **Create a new file**
4. Nome file: `history.json`
5. Contenuto: `[]`
6. Commit message: `Initialize history.json`
7. **Commit new file**

---

### 🧪 Step 4: Verifica che Funzioni

Dopo aver completato gli step sopra:

1. **Riavvia lo Space** (Settings → Factory reboot)
2. Apri l'app: https://huggingface.co/spaces/gianmarioiamoni67/tech-explanation-service
3. Chiedi una spiegazione (es. "Explain Docker")
4. Controlla i logs:
   - ✅ `History salvata su HF Hub (1 items)` → **FUNZIONA!**
   - ❌ `Errore salvataggio su HF Hub` → Vedi troubleshooting sotto

---

### 🔍 Troubleshooting

#### Errore: "401 Client Error"
```
❌ Errore salvataggio su HF Hub: 401 Client Error
Invalid username or password
```

**Causa**: Token HF non configurato o non valido

**Soluzione**:
1. Verifica che il secret `HF_TOKEN` esista nelle Settings dello Space
2. Verifica che il token sia di tipo **Write** (non Read)
3. Rigenera il token se necessario: https://huggingface.co/settings/tokens
4. Riavvia lo Space dopo aver aggiunto/modificato il secret

---

#### Errore: "404 Client Error - Entry Not Found"
```
⚠️ Impossibile caricare history da HF Hub: 404 Client Error
Entry Not Found for url: .../history.json
```

**Causa**: Il file `history.json` non esiste nello Space

**Soluzione**:
1. Crea il file `history.json` con contenuto `[]` (vedi Step 3)
2. Committa e pusha sul repository
3. Riavvia lo Space

---

#### Errore: "Repository Not Found"
```
Repository Not Found for url: https://huggingface.co/api/spaces/...
```

**Causa**: Nome dello Space errato nel codice o Space non esiste

**Soluzione**:
1. Verifica che lo Space esista: https://huggingface.co/spaces/gianmarioiamoni67/tech-explanation-service
2. Se il nome è diverso, aggiorna `app/services/tech_explanation_service.py`:
   ```python
   HF_USERNAME = "gianmarioiamoni67"
   HF_REPO = "tech-explanation-service"  # ← Verifica questo nome
   ```

---

#### History non persiste dopo reload

**Causa**: Token non configurato o file history.json in sola lettura

**Soluzione**:
1. Verifica che TUTTI gli step sopra siano completati
2. Controlla i logs dello Space per errori specifici
3. Assicurati che il token abbia permessi di Write
4. Prova a eliminare e ricreare il file `history.json`

---

### ✅ Checklist Completa

Prima di considerare il setup completo, verifica:

- [ ] Space esiste su HF: `https://huggingface.co/spaces/gianmarioiamoni67/tech-explanation-service`
- [ ] Token HF con permessi **Write** creato
- [ ] Secret `HF_TOKEN` configurato nelle Settings dello Space
- [ ] File `history.json` con contenuto `[]` esiste nel repository
- [ ] Space riavviato dopo configurazione
- [ ] Test: Creata una chat e verificato log `✅ History salvata su HF Hub`
- [ ] Test: Ricaricata pagina e verificato che la chat persista

---

### 📊 Verifica Status History

Puoi verificare lo stato della history nei logs dello Space:

```
# ✅ Tutto OK:
📚 History caricata da HF Hub (N items)
✅ History salvata su HF Hub (N items)

# ❌ Problemi:
⚠️ Impossibile caricare history da HF Hub: 404 Client Error
❌ Errore salvataggio su HF Hub: 401 Client Error
```

---

### 🆘 Support

Se dopo aver seguito tutti gli step il problema persiste:

1. **Controlla i logs** dello Space per errori specifici
2. **Verifica i permessi** del token HF
3. **Prova a ricreare** il file `history.json`
4. **Contatta il supporto** HF se necessario

---

## 📝 Note Aggiuntive

### Permessi Token HF

Il token deve avere questi permessi:
- ✅ **Write access to contents of all repos under your personal namespace**
- ✅ **Write access to datasets**

### Struttura File history.json

```json
[
  [
    "Topic 1",
    "Explanation 1...",
    "2026-01-13T10:30:00.123456"
  ],
  [
    "Topic 2",
    "Explanation 2...",
    "2026-01-13T11:45:00.654321"
  ]
]
```

Ogni entry è una tupla: `[topic, explanation, timestamp]`

---

## 🎉 Una Volta Configurato...

La history sarà **persistente** tra:
- ✅ Reload della pagina
- ✅ Riavvii dello Space
- ✅ Sessioni diverse
- ✅ Utenti diversi (shared history)

---

**Data ultimo aggiornamento**: 13 Gennaio 2026

