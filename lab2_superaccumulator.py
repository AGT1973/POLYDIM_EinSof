#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO 2: SUPERACUMULADOR KULISCH Y PREVENCIÓN DE CANCELACIÓN
Cátedra POLYDIM — UTN-FRBA
"""

import struct
import math

class KulischSuperacc4352:
    """
    Simulador de Referencia C07: Registro de Punto Fijo de 4.352 bits.
    136 palabras de 32 bits (Radix 2^32). Rango: [2^-2148, 2^+2048].
    """
    def __init__(self):
        self.words = [0] * 136

    def accumulate_product(self, a: float, b: float):
        # 1. Descomponer flotantes IEEE-754 en signo, exponente y mantisa entera
        bits_a = struct.unpack('!Q', struct.pack('!d', a))[0]
        bits_b = struct.unpack('!Q', struct.pack('!d', b))[0]

        exp_a, mant_a = (bits_a >> 52) & 0x7FF, bits_a & 0xFFFFFFFFFFFFF
        exp_b, mant_b = (bits_b >> 52) & 0x7FF, bits_b & 0xFFFFFFFFFFFFF

        # Exponentes y mantisas según tipo de número (normal vs subnormal)
        scale_a = -1074 if exp_a == 0 else (exp_a - 1075)
        int_m_a = mant_a if exp_a == 0 else (mant_a | (1 << 52))

        scale_b = -1074 if exp_b == 0 else (exp_b - 1075)
        int_m_b = mant_b if exp_b == 0 else (mant_b | (1 << 52))

        # Producto entero exacto (hasta 106 bits de precisión)
        prod_int = int_m_a * int_m_b
        total_exp = scale_a + scale_b

        # Desplazamiento respecto al bit 0 del acumulador (quantum 2^-2148)
        bit_pos = total_exp + 2148
        
        # Desplazar y sumar a las palabras radix 2^32
        shifted = prod_int << bit_pos
        bits_totales = prod_int.bit_length()
        
        idx = 0
        temp = shifted
        while temp > 0 and idx < 136:
            self.words[idx] += (temp & 0xFFFFFFFF)
            temp >>= 32
            idx += 1

        return {
            "prod_int": prod_int,
            "bits_totales": bits_totales,
            "bit_pos": bit_pos,
            "word_index": bit_pos // 32
        }

def run_lab2():
    print("=" * 70)
    print("LABORATORIO 2: AUDITORÍA DE CANCELACIÓN CATASTRÓFICA Y SUBNORMALES")
    print("=" * 70)

    # CASO 1: Subnormal Underflow Catastrófico
    a = 1.0e-315
    b = 1.0e-315
    prod_hardware = a * b

    print(f"\n[EXPERIMENTO 1: PRODUCTO SUBNORMAL a={a}, b={b}]")
    print(f"  • Hardware FPU estándar a * b : {prod_hardware}")
    print(f"  • ¿Hubo Underflow a Cero?     : {prod_hardware == 0.0} (INFORMACIÓN DESTRUIDA)")

    acc = KulischSuperacc4352()
    res = acc.accumulate_product(a, b)

    print(f"  • En Superacumulador Kulisch  : PRESERVADO EXACTO")
    print(f"  • Bits exactos activos        : {res['bits_totales']} bits")
    print(f"  • Posición de bit en registro : Bit {res['bit_pos']} (Palabra {res['word_index']})")
    print(f"  • Valor entero en registro    : {res['prod_int']}")

    # CASO 2: Cancelación Catastrófica en Sumas
    print(f"\n[EXPERIMENTO 2: CANCELACIÓN CATASTRÓFICA (1e8 + 1e-8) - 1e8]")
    suma_ingenua = (1.0e8 + 1.0e-8) - 1.0e8
    error_relativo_ingenuo = abs(suma_ingenua - 1.0e-8) / 1.0e-8

    print(f"  • Suma ingenua en Python/C++  : {suma_ingenua:.16e}")
    print(f"  • Valor analítico exacto      : 1.0000000000000000e-08")
    print(f"  • Error relativo de la FPU    : {error_relativo_ingenuo:.2%} (ERROR GRAVE)")

    # Acumulación compensada de Neumaier
    def neumaier(vals):
        s, c = 0.0, 0.0
        for v in vals:
            t = s + v
            if abs(s) >= abs(v):
                c += (s - t) + v
            else:
                c += (v - t) + s
            s = t
        return s + c

    suma_neumaier = neumaier([1.0e8, 1.0e-8, -1.0e8])
    error_neumaier = abs(suma_neumaier - 1.0e-8) / 1.0e-8
    print(f"  • Suma compensada Neumaier     : {suma_neumaier:.16e}")
    print(f"  • Error relativo Neumaier     : {error_neumaier:.2e} (PRECISIÓN TOTAL)")
    print("=" * 70)

if __name__ == "__main__":
    run_lab2()
