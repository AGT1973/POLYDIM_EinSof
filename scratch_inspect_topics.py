import re

with open(r'E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26250\Auditoria_Externa\suite_consolidada_1571_teoremas.py', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'@register_test\((\d+),\s*r?"([^"]+)"', text)
hyp_matches = [(num, topic) for num, topic in matches if any(k in topic.lower() for k in ['hiperb', 'lorentz', 'poincar'])]
print(f"Topics matching hyperbolic/lorentz: {len(hyp_matches)}")
for num, t in hyp_matches:
    print(f"  Th {num}: {t}")
