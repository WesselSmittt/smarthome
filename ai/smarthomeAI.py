import random
import matplotlib.pyplot as plt

# -----------------------------
# 1. Dataset maken
# -----------------------------
random.seed(42)
n = 50

temperatuur = [random.uniform(10, 35) for _ in range(n)]
zonuren = [random.uniform(0, 12) for _ in range(n)]

ijsjes = [2.5 * t + 1.5 * z + random.uniform(-15, 15)
          for t, z in zip(temperatuur, zonuren)]

# -----------------------------
# 2. Statistische functies
# -----------------------------
def mean(values):
    return sum(values) / len(values)

def variance(values):
    m = mean(values)
    return sum((v - m)**2 for v in values) / len(values)

def covariance(x, y):
    mx, my = mean(x), mean(y)
    return sum((xi - mx)*(yi - my) for xi, yi in zip(x, y)) / len(x)

def pearson(x, y):
    return covariance(x, y) / ((variance(x)**0.5) * (variance(y)**0.5))

# Correlaties berekenen
print("Correlatie temperatuur vs ijsjes:", round(pearson(temperatuur, ijsjes), 3))
print("Correlatie zonuren vs ijsjes:", round(pearson(zonuren, ijsjes), 3))

# -----------------------------
# 3. Visualisaties verkennende analyse
# -----------------------------
# Grafiek 1: Temperatuur vs ijsjesverkoop
plt.scatter(temperatuur, ijsjes, color="blue")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Aantal ijsjes verkocht")
plt.title("Temperatuur vs ijsjesverkoop")
plt.show()

# Grafiek 2: Zonuren vs ijsjesverkoop
plt.scatter(zonuren, ijsjes, color="green")
plt.xlabel("Zonuren")
plt.ylabel("Aantal ijsjes verkocht")
plt.title("Zonuren vs ijsjesverkoop")
plt.show()

# -----------------------------
# 4. Lineaire regressie (gradient descent)
# -----------------------------
def gradient_descent(X, Y, lr=0.001, epochs=3000):
    m, b = 0, 0
    n = len(X)

    for _ in range(epochs):
        y_pred = [m*x + b for x in X]
        dm = (-2/n) * sum(x*(y - y_hat) for x, y, y_hat in zip(X, Y, y_pred))
        db = (-2/n) * sum(y - y_hat for y, y_hat in zip(Y, y_pred))
        m -= lr * dm
        b -= lr * db

    return m, b

# Model trainen op temperatuur
m, b = gradient_descent(temperatuur, ijsjes)
print("Voorspellingsformule: y = {:.2f}x + {:.2f}".format(m, b))

# -----------------------------
# 5. Visualisatie regressielijn
# -----------------------------
# Grafiek 3: Regressielijn over temperatuur
temp_sorted = sorted(temperatuur)
pred_line = [m*t + b for t in temp_sorted]

plt.scatter(temperatuur, ijsjes, color="blue", label="Data")
plt.plot(temp_sorted, pred_line, color="red", label="Regressielijn")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Aantal ijsjes verkocht")
plt.title("Lineaire regressie: temperatuur vs ijsjesverkoop")
plt.legend()
plt.show()
