import os
import sys
from dotenv import load_dotenv
from supabase import create_client

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tqyhsxgsauwdzkepfqnr.supabase.co")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

users_res = supabase.auth.admin.list_users()
users = getattr(users_res, 'users', users_res)

# Pega termos de exemplo de uma conta existente
existing_cfg = supabase.from_('configuracoes_scraper').select('*').limit(1).execute()
default_terms = ["topo de bolo biscuit", "vela personalizada biscuit", "lembrancinha biscuit"]
default_blacklist = ["molde", "silicone", "esteca", "papel"]

if existing_cfg.data and len(existing_cfg.data) > 0:
    default_terms = existing_cfg.data[0].get("termos_busca") or default_terms
    default_blacklist = existing_cfg.data[0].get("blacklist") or default_blacklist

for u in users:
    if not u.email:
        continue
    email = u.email.lower()
    user_id = u.id
    
    # Verifica se já tem config
    chk = supabase.from_('configuracoes_scraper').select('id').eq('user_id', user_id).limit(1).execute()
    if not chk.data or len(chk.data) == 0:
        print(f"📦 Criando configuracoes_scraper inicial para {email}...")
        supabase.from_('configuracoes_scraper').insert({
            "user_id": user_id,
            "termos_busca": default_terms,
            "blacklist": default_blacklist,
            "status_scraper": "🟢 Conta inicializada e pronta para monitoramento."
        }).execute()
        print(f"   ✅ Configuração criada para {email}!")
    else:
        print(f"   ✓ {email} já possui configuracoes_scraper.")

print("✨ Finalizado!")
