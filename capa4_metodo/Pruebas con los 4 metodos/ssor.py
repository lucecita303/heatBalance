# Temperatura CPU/GPU - Método SSOR (SOR simétrico)
# Cada iteración = un barrido SOR hacia adelante + uno hacia atrás
# (por eso una iteración SSOR cuesta 2 barridos).
# Balance de calor por componente:
#   (Ti - Tamb)/R_i + suma_j (Ti - Tj)/R_acople = P_i
# Esto da un sistema lineal; M es la matriz aumentada [A | b] (n x n+1)

T_AMBIENTE = 25.0   # °C
R_ACOPLE = 2.0      # °C/W  (resistencia térmica entre componentes)
TOL = 1e-6          # error porcentual para detenerse
OMEGA = 1.0075      # factor de relajación (entre 0 y 2)

COMPONENTES = [
    {"nombre": "CPU Intel Core i5 13a gen", "corto": "CPU", "potencia": 65.0, "R": 0.50},
    {"nombre": "GPU NVIDIA RTX 4060 8GB", "corto": "GPU", "potencia": 115.0, "R": 0.35},
]


def construir_matriz(componentes):
    n = len(componentes)
    M = [[0.0] * (n + 1) for _ in range(n)]
    for i in range(n):
        c = componentes[i]
        M[i][i] += 1 / c["R"]
        M[i][n] = c["potencia"] + T_AMBIENTE / c["R"]
        for j in range(n):
            if j != i:
                M[i][i] += 1 / R_ACOPLE
                M[i][j] -= 1 / R_ACOPLE
    return M


def fmt(v, nombres):
    return "  ".join(f"{nombres[i]}={v[i]:.6f}" for i in range(len(v)))


def barrido(M, x, w, orden):
    # Un barrido SOR sobre la lista x (se actualiza en el lugar)
    n = len(M)
    for i in orden:
        suma = 0

        for j in range(n):
            if i != j:
                suma += M[i][j] * x[j]

        gs = (M[i][n] - suma) / M[i][i]
        x[i] = (1 - w) * x[i] + w * gs


def ssor(M, w, nombres):
    n = len(M)

    xo = [T_AMBIENTE] * n
    cumple = False
    iteracion = 0

    while cumple == False:
        iteracion += 1

        xm = xo[:]                                    # copia para el barrido adelante
        barrido(M, xm, w, range(n))                   # adelante: 0 .. n-1

        xn = xm[:]
        barrido(M, xn, w, range(n - 1, -1, -1))       # atrás: n-1 .. 0

        contador = 0
        errores = [0] * n

        for i in range(n):
            if xn[i] == 0:
                error = 0 if xo[i] == 0 else float('inf')
            else:
                error = abs((xn[i] - xo[i]) / xn[i]) * 100

            errores[i] = error
            if error > TOL:
                contador += 1

        print(f"Iteracion {iteracion}")
        print("  Valores iniciales :", fmt(xo, nombres))
        print("  Tras barrido adel.:", fmt(xm, nombres))
        print("  Valores finales   :", fmt(xn, nombres))
        print("  Error porcentual  :", "  ".join(f"{nombres[i]}={errores[i]:.6f}%" for i in range(n)))

        if contador > 0:
            cumple = False

            for i in range(n):
                xo[i] = xn[i]

        else:
            cumple = True

    return xn, errores, iteracion


M = construir_matriz(COMPONENTES)
nombres = [c["corto"] for c in COMPONENTES]

print("=== METODO SSOR ===")
print(f"Factor de relajacion w = {OMEGA}")
print("Matriz aumentada [A | b]:")
for fila in M:
    print("  ", [round(v, 4) for v in fila])
print()

xn, errores, iteraciones = ssor(M, OMEGA, nombres)

print("\n=== RESULTADO FINAL ===")
for i in range(len(xn)):
    print(f"{COMPONENTES[i]['nombre']}: {xn[i]:.4f} Grados Centigrados")
print(f"Error final (max): {max(errores):.3e} %")
print(f"Iteraciones      : {iteraciones}  ({2 * iteraciones} barridos)")
