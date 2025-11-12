# 🚀 Como Abrir a Interface do SuperEzio

## ✅ MÉTODO RÁPIDO

### **Opção 1: Script Automático**
```bash
start_all.bat
```
Isso abre 3 janelas (Python, Express, Vite) e depois você acessa:
```
http://localhost:3000
```

### **Opção 2: NPM (Tudo Junto)**
```bash
npm run dev:all
```
Abre os 3 servidores em paralelo.

### **Opção 3: Manual (3 Terminais)**
```bash
# Terminal 1: Python
cd backend
venv\Scripts\activate
python api.py

# Terminal 2: Express
npm run serve

# Terminal 3: Vite
npm run dev
```

---

## 🌐 ACESSAR INTERFACE

Depois que os servidores estiverem rodando:
```
http://localhost:3000
```

---

## 📊 VERIFICAR STATUS

### **Verificar se estão rodando:**
```bash
netstat -ano | findstr ":8000"  # Python
netstat -ano | findstr ":8080"  # Express
netstat -ano | findstr ":3000"  # Vite
```

### **Ou usar o script:**
```bash
check_servers.bat
```

---

## ⚠️ SE NÃO ABRIR

1. Verificar se portas estão livres:
```bash
kill_ports.bat
```

2. Reiniciar servidores:
```bash
start_all.bat
```

3. Aguardar 10-15 segundos para servidores iniciarem

4. Acessar manualmente:
```
http://localhost:3000
```

---

**Status:** Interface deve abrir automaticamente após iniciar servidores

