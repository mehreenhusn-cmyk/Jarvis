"""Chalao: python backend/check_keys.py  - .env ki har key ko ek chhota sawal bhej ke check karta hai.
Key kabhi print nahi hoti, sirf OK / FAIL."""
import app

app.load_env()
for name, (base, key_env, model) in app.PROVIDERS.items():
    if not app.os.environ.get(key_env):
        print(f"- {name:10} key .env mein nahi hai (skip)")
        continue
    try:
        r = app.call(name, [{"role": "user", "content": "Ek shabd mein jawab do: OK"}])
        print(f"OK   {name:10} jawab: {r[:40]!r}")
    except RuntimeError as e:
        print(f"FAIL {name:10} {e}")
print("\nChalne wale providers ko PROVIDER=a,b,c order mein .env mein likho.")
