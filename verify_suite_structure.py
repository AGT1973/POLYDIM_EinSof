import re

with open(r'E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26250\Auditoria_Externa\suite_consolidada_1571_teoremas.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'(@register_test\((\d+),\s*(r?"[^"]+"),\s*(\d+)\)\s*\ndef\s+(test_teorema_\d+)\(\):\s*\n\s*(r?"""[\s\S]*?"""))')
matches = pattern.findall(text)
print(f"Total matched functions with decorator and docstring: {len(matches)}")
if len(matches) > 0:
    first = matches[0]
    print(f"First match: ID={first[1]}, Topic={first[2]}, Cycle={first[3]}, Name={first[4]}")
    last = matches[-1]
    print(f"Last match: ID={last[1]}, Topic={last[2]}, Cycle={last[3]}, Name={last[4]}")
