import random
import matplotlib.pyplot as plt
# -----------------------------
# 1. dataset genereren
# -----------------------------
random.seed(42)
X = [i for i in range(1, 21)]  # aantal actieve apparaten
Y = [2.5 * x + random.uniform(-5, 5) for x in X]  # energieverbruik met ruis

# -----------------------------
# 2. Eigen functies voor correlatie
# -----------------------------
def mean(values):
    return sum(values) / len(values)

def covariance(x, y):
    x_mean, y_mean = mean(x), mean(y)
    return sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y)) / len(x)

def variance(values):
    mean_val = mean(values)
    return sum((v - mean_val) ** 2 for v in values) / len(values)

def pearson_correlation(x, y):
    return covariance(x, y) / (variance(x)**0.5 * variance(y)**0.5)

print("Covariance:", covariance(X, Y))
print("Pearson correlation:", pearson_correlation(X, Y))

# -----------------------------
# 3. Lineaire regressie met Gradient Descent
# -----------------------------
def gradient_descent(X, Y, lr=0.01, epochs=2000):
    m, b = 0, 0  # startwaarden
    n = len(X)

    for _ in range(epochs):
        y_pred = [m * x + b for x in X]
        # Gradients berekenen
        dm = (-2/n) * sum(x * (y - y_hat) for x, y, y_hat in zip(X, Y, y_pred))
        db = (-2/n) * sum(y - y_hat for y, y_hat in zip(Y, y_pred))
        # Update
        m -= lr * dm
        b -= lr * db
    return m, b

m, b = gradient_descent(X, Y, lr=0.01, epochs=2000)
print("Slope (m):", m)
print("Intercept (b):", b)

# -----------------------------
# 4. Visualisatie
# -----------------------------
plt.scatter(X, Y, color="blue", label="Data punten")
plt.plot(X, [m*x + b for x in X], color="red", label="Regressielijn")
plt.xlabel("Aantal actieve apparaten")
plt.ylabel("Energieverbruik (kWh)")
plt.title("Lineaire regressie SmartHome Dummy Data")
plt.legend()
plt.show()
