# 20 küsimuse mäng

**20 küsimuse mäng** on veebipõhine mäng, kus kasutaja mõtleb ühele sõnale ning süsteem püüab selle ära arvata, esitades kuni 20 küsimust. Mäng kasutab taustal loogikat ja keeleressursse, et teha täpseid pakkumisi.

See repositoorium koosneb kolmest kaustast:  
- `preparation` – andmete eeltöötlus ja ettevalmistus  
- `backend` – mängu loogika ja API  
- `frontend` – kasutajaliides  

#### Mängu saab mängida otse veebis: **[kysimustemang.pythonanywhere.com](https://kysimustemang.pythonanywhere.com)**  

Või seadistada lokaalselt oma arvutis. See eeldab nende olemasolu: Git (https://git-scm.com/downloads), Python (https://www.python.org/downloads/) ja Node.js (https://nodejs.org/)

## Lokaalne seadistamine

### 1. Repositooriumi kloonimine
Klooni repositoorium oma arvutisse:
```
git clone https://github.com/vanessaphtn/20KysimuseMang.git
cd 20KysimuseMang
```

### 2. Backendi seadistamine
Liigu backend kausta ja installi vajalikud Python'i teegid:
 ```
cd backend
python -m venv venv  # Loo virtuaalkeskkond, kui python ei tööta proovi py või python3
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python3 server.py    
```

### 3. Frontendi käivitamine
Eraldi terminaliaknas liigu frontend kausta ja installi vajalikud paketid:
```
cd ../frontend/frontend  # Linux/Mac
cd .\frontend\frontend # Windows
npm install
npm run dev
```
Mine lehele: http://localhost:5173/
