import os
import sys
from dotenv import load_dotenv
from supabase import create_client

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("❌ Erro: SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem estar configuradas no .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

# Lista padrão para criação/atualização de cargos
USERS_TO_SETUP = [
    {
        "email": os.getenv("ADMIN_EMAIL", "admin@example.com"),
        "password": os.getenv("ADMIN_INITIAL_PASSWORD", "Admin@123456!"),
        "role": "admin"
    }
]

print("\n" + "=" * 65)
print("🚀 Configurando Cargos (Admin, Pro, Basic) no Supabase Auth")
print("=" * 65 + "\n")

try:
    existing_users_res = supabase.auth.admin.list_users()
    existing_users = getattr(existing_users_res, 'users', existing_users_res)
    users_by_email = {u.email.lower(): u for u in existing_users if getattr(u, 'email', None)}
except Exception as e:
    print(f"⚠️ Erro ao listar usuários via admin API: {e}")
    users_by_email = {}

for u_data in USERS_TO_SETUP:
    email = u_data["email"].lower()
    role = u_data["role"]
    pwd = u_data["password"]

    if email in users_by_email:
        user_obj = users_by_email[email]
        print(f"🔄 Atualizando cargo do usuário existente: {email} -> {role.upper()}")
        try:
            supabase.auth.admin.update_user_by_id(
                user_obj.id,
                {
                    "app_metadata": {"role": role},
                    "user_metadata": {"role": role}
                }
            )
            print(f"   ✅ {email} atualizado com sucesso para {role.upper()}!")
        except Exception as err:
            print(f"   ❌ Falha ao atualizar {email}: {err}")
    else:
        print(f"➕ Criando novo usuário: {email} ({role.upper()}) com senha...")
        try:
            new_user = supabase.auth.admin.create_user({
                "email": email,
                "password": pwd,
                "email_confirm": True,
                "app_metadata": {"role": role},
                "user_metadata": {"role": role}
            })
            print(f"   ✅ {email} criado com sucesso com role {role.upper()}! Senha: {pwd}")
        except Exception as err:
            print(f"   ❌ Falha ao criar {email}: {err}")

print("\n" + "=" * 65)
print("✨ Configuração de usuários e cargos concluída com sucesso!")
print("=" * 65 + "\n")
