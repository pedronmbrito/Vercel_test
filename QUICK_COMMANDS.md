# 🚀 Quick Commands - TeamPulse

## 📖 Ver Código

```bash
# Bot Slack principal
cat backend/app.py | less

# Scheduler (mensagens automáticas)
cat backend/scheduler.py | less

# Database operations
cat backend/database.py | less

# Stripe payments
cat backend/stripe_integration.py | less

# Landing page
cat frontend/index.html | less

# Database schema
cat database/schema.sql
```

## 🔍 Procurar no Código

```bash
# Procurar função específica
grep -n "def send_checkin" backend/app.py

# Ver todas as funções
grep "^def " backend/*.py

# Procurar por "mood" em todo o código
grep -r "mood" backend/

# Ver estrutura das tabelas
grep "CREATE TABLE" database/schema.sql
```

## 📊 Estatísticas do Código

```bash
# Contar linhas de código
wc -l backend/*.py frontend/*.html database/*.sql

# Ver tamanho dos ficheiros
ls -lh backend/ frontend/ database/

# Ver commits
git log --oneline

# Ver o que foi mudado
git diff HEAD~2 HEAD --stat
```

## 🌐 Ver Frontend no Browser

```bash
# Já está a correr em:
# http://localhost:8080/index.html
# http://localhost:8080/dashboard.html

# Se não estiver, iniciar servidor:
cd frontend
python3 -m http.server 8080
```

## 🐳 Testar Com Docker

```bash
# Iniciar tudo (backend + database + scheduler)
docker-compose up

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

## 📝 Editar Código

```bash
# Editar bot principal
nano backend/app.py
# ou
vim backend/app.py

# Editar landing page
nano frontend/index.html

# Editar database schema
nano database/schema.sql
```

## 🚀 Deploy

```bash
# Ler o guia completo
cat NEXT_STEPS.md

# Ou seguir README
cat README.md
```

## 💡 Dicas

- **Ver só as funções importantes**: `grep -A 10 "def send_checkin" backend/app.py`
- **Ver imports**: `head -20 backend/app.py`
- **Ver estrutura do projeto**: `tree -L 2` (se tiveres tree instalado)
- **Pesquisar texto**: `grep -r "texto_a_procurar" .`

## 🎯 Próximos Passos

1. **Ver o código**: ✅ (estás aqui!)
2. **Testar localmente**: Seguir `HOW_TO_TEST_LOCALLY.sh`
3. **Deploy**: Seguir `NEXT_STEPS.md`
4. **Lançar**: Semana 1-2 do plano
