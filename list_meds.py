from app import load_medicamentos

meds = load_medicamentos()
print(f"Total de medicamentos: {len(meds)}")
for i, m in enumerate(meds, 1):
    print(f"{i:2d}. {m.get('nome')} (ID: {m.get('id')})")
