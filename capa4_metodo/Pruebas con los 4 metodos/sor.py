# Temperatura CPU/GPU - Método SOR (sobrerrelajación sucesiva)
# Balance de calor por componente:
#   (Ti - Tamb)/R_i + suma_j (Ti - Tj)/R_acople = P_i
# Esto da un sistema lineal; M es la matriz aumentada [A | b] (n x n+1)

T_AMBIENTE = 25.0   # °C
R_ACOPLE = 2.0      # °C/W  (resistencia térmica entre componentes)
TOL = 1e-6          # error porcentual para detenerse
OMEGA = 1.0075      # factor de relajación (1 = Gauss-Seidel, debe estar entre 0 y 2)
                    # óptimo para este caso 2x2: w = 2 / (1 + sqrt(1 - rho^2)),
                    # con rho = sqrt(a12*a21 / (a11*a22))

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


def sor(M, w, nombres):
    n = len(M)

    xo = [T_AMBIENTE] * n
    cumple = False
    iteracion = 0

    while cumple == False:
        iteracion += 1
        xn = [0] * n

        for i in range(n):
            suma = 0

            for j in range(n):
                if i != j:
                    if j < i:
                        suma += M[i][j] * xn[j]
                    elif j > i:
                        suma += M[i][j] * xo[j]

            gs = (M[i][n] - suma) / M[i][i]            # valor de Gauss-Seidel
            xn[i] = (1 - w) * xo[i] + w * gs           # relajación

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
        print("  Valores iniciales:", fmt(xo, nombres))
        print("  Valores finales  :", fmt(xn, nombres))
        print("  Error porcentual :", "  ".join(f"{nombres[i]}={errores[i]:.6f}%" for i in range(n)))

        if contador > 0:
            cumple = False

            for i in range(n):
                xo[i] = xn[i]

        else:
            cumple = True

    return xn, errores, iteracion


M = construir_matriz(COMPONENTES)
nombres = [c["corto"] for c in COMPONENTES]

print("=== METODO SOR ===")
print(f"Factor de relajacion w = {OMEGA}")
print("Matriz aumentada [A | b]:")
for fila in M:
    print("  ", [round(v, 4) for v in fila])
print()

xn, errores, iteraciones = sor(M, OMEGA, nombres)

print("\n=== RESULTADO FINAL ===")
for i in range(len(xn)):
    print(f"{COMPONENTES[i]['nombre']}: {xn[i]:.4f} Grados Centigrados")
print(f"Error final (max): {max(errores):.3e} %")
print(f"Iteraciones      : {iteraciones}")
