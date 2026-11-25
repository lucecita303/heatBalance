"""
CAPA 4 - LÓGICA MATEMÁTICA PURA
================================
Cálculo de temperatura CPU/GPU resolviendo A·T = b con métodos iterativos.

Reglas de esta capa:
  - Solo cálculos numéricos: sin print(), sin input(), sin archivos, sin interfaz.
  - Recibe la matriz aumentada M = [A | b] (n filas x n+1 columnas) y devuelve
    datos (diccionarios y listas). Las capas superiores deciden cómo mostrarlos.
  - No sabe nada del hardware: quién arma M a partir de los componentes es otra capa.

Método elegido: GAUSS-SEIDEL (ver JUSTIFICACION_METODO y seleccionar_metodo()).
"""

# ----------------------------------------------------------------------------
# CONSTANTES Y JUSTIFICACIÓN
# ----------------------------------------------------------------------------
METODO_ELEGIDO = "gauss_seidel"

TOL_POR_DEFECTO = 1e-6        # error porcentual para detener
MAX_ITER_POR_DEFECTO = 1000
OMEGA_POR_DEFECTO = 1.0       # 1.0 equivale a Gauss-Seidel

# Criterios con los que se escogió el método (identificación explícita).
JUSTIFICACION_METODO = {
    "metodo": "Gauss-Seidel",
    "criterios": [
        "Convergencia garantizada: la matriz del balance térmico es "
        "diagonalmente dominante (la diagonal suma la resistencia al ambiente "
        "más los acoples).",
        "Eficiencia: usa los valores nuevos apenas se calculan, por lo que "
        "converge en menos iteraciones que Jacobi.",
        "Robustez: no requiere parámetro externo (ω). El sistema cambia según "
        "el hardware detectado y un ω mal elegido hace más lentos o divergir "
        "a SOR y SSOR.",
        "Costo por iteración: 1 barrido, frente a 2 de SSOR.",
        "Simplicidad: fácil de implementar, explicar y depurar.",
    ],
    "cuando_cambiar": "SOR sería preferible si el modelo creciera a una malla "
                      "con muchos nodos y se pudiera calcular un ω óptimo.",
}


# ----------------------------------------------------------------------------
# UTILIDADES NUMÉRICAS
# ----------------------------------------------------------------------------
def validar_matriz(M):
    """Verifica que M sea n x (n+1) y sin ceros en la diagonal.
    Lanza ValueError si no es válida."""
    n = len(M)
    if n == 0:
        raise ValueError("La matriz está vacía.")
    for i in range(n):
        if len(M[i]) != n + 1:
            raise ValueError("La matriz aumentada debe ser n x (n+1).")
        if M[i][i] == 0:
            raise ValueError(f"Cero en la diagonal (fila {i}).")


def error_porcentual(xn, xo):
    """Error porcentual por variable: |(xn - xo) / xn| * 100."""
    errores = []
    for i in range(len(xn)):
        if xn[i] == 0:
            errores.append(0.0 if xo[i] == 0 else float("inf"))
        else:
            errores.append(abs((xn[i] - xo[i]) / xn[i]) * 100)
    return errores


def es_diagonalmente_dominante(M):
    """True si |a_ii| >= suma |a_ij| (j != i) en todas las filas
    y es estricta en al menos una."""
    n = len(M)
    estricta = False
    for i in range(n):
        resto = sum(abs(M[i][j]) for j in range(n) if j != i)
        if abs(M[i][i]) < resto:
            return False
        if abs(M[i][i]) > resto:
            estricta = True
    return estricta


def omega_optimo(M):
    """ω óptimo para SOR. Fórmula cerrada solo para sistemas 2x2:
        rho = sqrt(a12*a21 / (a11*a22)),  ω = 2 / (1 + sqrt(1 - rho^2)).
    Para n != 2 devuelve 1.0 (equivale a Gauss-Seidel)."""
    if len(M) != 2:
        return OMEGA_POR_DEFECTO
    rho2 = (M[0][1] * M[1][0]) / (M[0][0] * M[1][1])
    if rho2 < 0 or rho2 >= 1:
        return OMEGA_POR_DEFECTO
    return 2.0 / (1.0 + (1.0 - rho2) ** 0.5)


def residuo(M, x):
    """Norma infinito de (b - A·x). Mide qué tan bien cumple el sistema."""
    n = len(M)
    mayor = 0.0
    for i in range(n):
        r = M[i][n] - sum(M[i][j] * x[j] for j in range(n))
        mayor = max(mayor, abs(r))
    return mayor


def _resultado(nombre, x, historial, iteraciones, barridos, convergio):
    errores = historial[-1]["errores"] if historial else []
    return {
        "metodo": nombre,
        "solucion": x,
        "iteraciones": iteraciones,
        "barridos": barridos,
        "error_final": max(errores) if errores else None,
        "convergio": convergio,
        "historial": historial,   # lista de {iteracion, x_inicial, x_final, errores}
    }


# ----------------------------------------------------------------------------
# MÉTODOS ITERATIVOS
# ----------------------------------------------------------------------------
def jacobi(M, x0=None, tol=TOL_POR_DEFECTO, max_iter=MAX_ITER_POR_DEFECTO):
    """Jacobi: cada incógnita usa SOLO valores de la iteración anterior."""
    validar_matriz(M)
    n = len(M)
    xo = list(x0) if x0 is not None else [0.0] * n
    historial = []

    for k in range(1, max_iter + 1):
        xn = [0.0] * n
        for i in range(n):
            suma = 0.0
            for j in range(n):
                if i != j:
                    suma += M[i][j] * xo[j]
            xn[i] = (M[i][n] - suma) / M[i][i]

        errores = error_porcentual(xn, xo)
        historial.append({"iteracion": k, "x_inicial": xo[:], "x_final": xn[:],
                          "errores": errores})
        if max(errores) <= tol:
            return _resultado("jacobi", xn, historial, k, k, True)
        xo = xn

    return _resultado("jacobi", xo, historial, max_iter, max_iter, False)


def gauss_seidel(M, x0=None, tol=TOL_POR_DEFECTO, max_iter=MAX_ITER_POR_DEFECTO):
    """Gauss-Seidel: usa valores NUEVOS (j < i) y viejos (j > i)."""
    validar_matriz(M)
    n = len(M)
    xo = list(x0) if x0 is not None else [0.0] * n
    historial = []

    for k in range(1, max_iter + 1):
        xn = [0.0] * n
        for i in range(n):
            suma = 0.0
            for j in range(n):
                if i != j:
                    if j < i:
                        suma += M[i][j] * xn[j]
                    else:
                        suma += M[i][j] * xo[j]
            xn[i] = (M[i][n] - suma) / M[i][i]

        errores = error_porcentual(xn, xo)
        historial.append({"iteracion": k, "x_inicial": xo[:], "x_final": xn[:],
                          "errores": errores})
        if max(errores) <= tol:
            return _resultado("gauss_seidel", xn, historial, k, k, True)
        xo = xn

    return _resultado("gauss_seidel", xo, historial, max_iter, max_iter, False)


def sor(M, omega=None, x0=None, tol=TOL_POR_DEFECTO, max_iter=MAX_ITER_POR_DEFECTO):
    """SOR: Gauss-Seidel con relajación  x_i = (1-ω)·x_i_viejo + ω·x_i_GS."""
    validar_matriz(M)
    n = len(M)
    w = omega if omega is not None else omega_optimo(M)
    if not 0 < w < 2:
        raise ValueError("ω debe estar entre 0 y 2.")
    xo = list(x0) if x0 is not None else [0.0] * n
    historial = []

    for k in range(1, max_iter + 1):
        xn = [0.0] * n
        for i in range(n):
            suma = 0.0
            for j in range(n):
                if i != j:
                    if j < i:
                        suma += M[i][j] * xn[j]
                    else:
                        suma += M[i][j] * xo[j]
            gs = (M[i][n] - suma) / M[i][i]
            xn[i] = (1 - w) * xo[i] + w * gs

        errores = error_porcentual(xn, xo)
        historial.append({"iteracion": k, "x_inicial": xo[:], "x_final": xn[:],
                          "errores": errores, "omega": w})
        if max(errores) <= tol:
            return _resultado("sor", xn, historial, k, k, True)
        xo = xn

    return _resultado("sor", xo, historial, max_iter, max_iter, False)


def _barrido_sor(M, x, w, orden):
    """Un barrido SOR sobre la lista x (se modifica en el lugar)."""
    n = len(M)
    for i in orden:
        suma = 0.0
        for j in range(n):
            if i != j:
                suma += M[i][j] * x[j]
        gs = (M[i][n] - suma) / M[i][i]
        x[i] = (1 - w) * x[i] + w * gs


def ssor(M, omega=None, x0=None, tol=TOL_POR_DEFECTO, max_iter=MAX_ITER_POR_DEFECTO):
    """SSOR: por iteración, un barrido SOR hacia adelante y otro hacia atrás."""
    validar_matriz(M)
    n = len(M)
    w = omega if omega is not None else omega_optimo(M)
    if not 0 < w < 2:
        raise ValueError("ω debe estar entre 0 y 2.")
    xo = list(x0) if x0 is not None else [0.0] * n
    historial = []

    for k in range(1, max_iter + 1):
        xm = xo[:]
        _barrido_sor(M, xm, w, range(n))                  # adelante
        xn = xm[:]
        _barrido_sor(M, xn, w, range(n - 1, -1, -1))      # atrás

        errores = error_porcentual(xn, xo)
        historial.append({"iteracion": k, "x_inicial": xo[:], "x_medio": xm[:],
                          "x_final": xn[:], "errores": errores, "omega": w})
        if max(errores) <= tol:
            return _resultado("ssor", xn, historial, k, 2 * k, True)
        xo = xn

    return _resultado("ssor", xo, historial, max_iter, 2 * max_iter, False)


# ----------------------------------------------------------------------------
# SELECCIÓN DEL MÉTODO (identificación explícita del porqué)
# ----------------------------------------------------------------------------
METODOS = {
    "jacobi": jacobi,
    "gauss_seidel": gauss_seidel,
    "sor": sor,
    "ssor": ssor,
}
METODOS_CON_PARAMETRO = {"sor", "ssor"}


def comparar_metodos(M, x0=None, tol=TOL_POR_DEFECTO, max_iter=MAX_ITER_POR_DEFECTO):
    """Ejecuta los 4 métodos sobre el mismo sistema y devuelve
    {nombre: resultado}. Sirve de base para el cuadro comparativo."""
    return {nombre: f(M, x0=x0, tol=tol, max_iter=max_iter)
            for nombre, f in METODOS.items()}


def seleccionar_metodo(M, x0=None, tol=TOL_POR_DEFECTO):
    """Elige el método para el sistema M y devuelve la decisión con su motivo.

    Criterios, en orden:
      1. Que converja.
      2. Que NO dependa de un parámetro externo (ω), por robustez.
      3. Entre los que quedan, el de menor número de barridos (costo real).
    """
    validar_matriz(M)
    resultados = comparar_metodos(M, x0=x0, tol=tol)

    candidatos = [r for nombre, r in resultados.items()
                  if r["convergio"] and nombre not in METODOS_CON_PARAMETRO]
    if not candidatos:       # plan B: cualquiera que converja
        candidatos = [r for r in resultados.values() if r["convergio"]]
    if not candidatos:
        raise ValueError("Ningún método convergió con esta matriz.")

    elegido = min(candidatos, key=lambda r: r["barridos"])
    otros = {n: r["barridos"] for n, r in resultados.items()}

    return {
        "metodo": elegido["metodo"],
        "diagonalmente_dominante": es_diagonalmente_dominante(M),
        "barridos_por_metodo": otros,
        "criterios": JUSTIFICACION_METODO["criterios"],
        "motivo": (f"Se eligió {elegido['metodo']} porque converge, no depende "
                   f"de un parámetro externo y necesitó {elegido['barridos']} "
                   f"barridos (todos: {otros})."),
    }


# ----------------------------------------------------------------------------
# PUNTO DE ENTRADA DE LA CAPA
# ----------------------------------------------------------------------------
def resolver(M, metodo=METODO_ELEGIDO, x0=None, tol=TOL_POR_DEFECTO,
             max_iter=MAX_ITER_POR_DEFECTO, **kwargs):
    """Resuelve M con el método indicado (por defecto, el elegido).
    kwargs permite pasar omega a sor/ssor."""
    if metodo not in METODOS:
        raise ValueError(f"Método desconocido: {metodo}")
    return METODOS[metodo](M, x0=x0, tol=tol, max_iter=max_iter, **kwargs)
