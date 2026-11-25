def construir_sistema(temperatura_ambiente, uso_cpu, uso_gpu):
    b1 = temperatura_ambiente * 0.92 + 0.45 * uso_cpu
    b2 = temperatura_ambiente * 0.90 + 0.50 * uso_gpu

    return {
        "matriz_aumentada": [
            [1.00, -0.08, b1],
            [-0.10,  1.00, b2],
        ],
        "variables": ["T_CPU", "T_GPU"],
        "n": 2,
        "temperatura_ambiente": temperatura_ambiente,
        "uso_cpu": uso_cpu,
        "uso_gpu": uso_gpu,
    }


def es_diagonalmente_dominante(matriz_aumentada):
    n = len(matriz_aumentada)
    for i in range(n):
        diagonal = abs(matriz_aumentada[i][i])
        suma_otros = sum(abs(matriz_aumentada[i][j]) for j in range(n) if j != i)
        if diagonal <= suma_otros:
            return False
    return True


def reordenar_para_dominancia(matriz_aumentada):
    from itertools import permutations
    n = len(matriz_aumentada)
    for orden in permutations(range(n)):
        nueva_matriz = [matriz_aumentada[i] for i in orden]
        if es_diagonalmente_dominante(nueva_matriz):
            return nueva_matriz
    return None


def preparar_datos(temperatura_ambiente, uso_cpu, uso_gpu):
    sistema = construir_sistema(temperatura_ambiente, uso_cpu, uso_gpu)
    matriz = sistema["matriz_aumentada"]
    advertencia = ""

    if es_diagonalmente_dominante(matriz):
        dominante = True
    else:
        matriz_reordenada = reordenar_para_dominancia(matriz)
        if matriz_reordenada is not None:
            matriz = matriz_reordenada
            dominante = True
            advertencia = "Filas reordenadas para lograr dominancia diagonal."
        else:
            dominante = False
            advertencia = "ADVERTENCIA: La matriz no es diagonalmente dominante. Gauss-Seidel puede no converger."

    return {
        "matriz_aumentada": matriz,
        "variables": sistema["variables"],
        "n": sistema["n"],
        "dominante": dominante,
        "advertencia": advertencia,
        "temperatura_ambiente": temperatura_ambiente,
        "uso_cpu": uso_cpu,
        "uso_gpu": uso_gpu,
    }


def reconstruir_resultado(solucion, variables, temperatura_ambiente, uso_cpu, uso_gpu):
    return {
        "T_CPU": round(solucion[0], 6),
        "T_GPU": round(solucion[1], 6),
        "variables": variables,
        "temperatura_ambiente": temperatura_ambiente,
        "uso_cpu": uso_cpu,
        "uso_gpu": uso_gpu,
        "alerta_cpu": solucion[0] > 85,
        "alerta_gpu": solucion[1] > 90,
        "mensaje_cpu": "TEMPERATURA CRÍTICA EN CPU" if solucion[0] > 85 else "CPU en rango normal",
        "mensaje_gpu": "TEMPERATURA CRÍTICA EN GPU" if solucion[1] > 90 else "GPU en rango normal",
    }


if __name__ == "__main__":
    resultado = preparar_datos(25.0, 70.0, 90.0)

    print("=" * 55)
    print("PRUEBA DE CAPA 3 — TRADUCCIÓN")
    print("=" * 55)

    for i, fila in enumerate(resultado["matriz_aumentada"]):
        nombre = resultado["variables"][i]
        coefs = "  ".join(f"{v:8.4f}" for v in fila)
        print(f"  Fila {i} ({nombre}): [ {coefs} ]")

    print(f"\nDiagonalmente dominante : {resultado['dominante']}")

    if resultado["advertencia"]:
        print(f"Advertencia             : {resultado['advertencia']}")

    print("\nPrueba de conversión inversa:")
    solucion_simulada = [60.383063, 73.538306]
    reconstruido = reconstruir_resultado(
        solucion_simulada,
        resultado["variables"],
        25.0, 70.0, 90.0
    )
    for clave, valor in reconstruido.items():
        print(f"  {clave}: {valor}")