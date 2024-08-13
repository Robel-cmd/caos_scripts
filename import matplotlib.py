import matplotlib.pyplot as plt
import numpy as np

# Definir los valores de x
x = np.linspace(-2, 10, 400)
# Definir la línea de frontera
y = (2/3)*x - 4

# Crear la figura y los ejes
fig, ax = plt.subplots()

# Dibujar la línea de frontera
ax.plot(x, y, 'r', label='-2x + 3y = -12')

# Rellenar la región que satisface la desigualdad
x_fill = np.linspace(-2, 10, 400)
y_fill = (2/3)*x_fill - 4
ax.fill_between(x_fill, y_fill, -15, where=(y_fill > -15), interpolate=True, color='red', alpha=0.3)

# Etiquetas y título
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Gráfico de la desigualdad -2x + 3y < -12')

# Ajustar límites
ax.set_xlim(-2, 10)
ax.set_ylim(-15, 5)

# Mostrar la leyenda
ax.legend()

# Mostrar el gráfico
plt.grid(True)
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)
plt.show()
