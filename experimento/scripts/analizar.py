"""Calcula mediana y p95 de segundos por corrida. Uso: python analizar.py resultados/corrida.csv"""
import csv, sys, statistics as st
t = sorted(float(r[1]) for r in csv.reader(open(sys.argv[1])) if r[1])
p95 = t[min(len(t)-1, int(0.95*len(t)))]
print(f"n={len(t)} mediana={st.median(t):.2f}s p95={p95:.2f}s")
