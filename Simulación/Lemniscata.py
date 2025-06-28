from robodk.robolink import *    # API para comunicarte con RoboDK
from robodk.robomath import *    # Funciones matemáticas
import math

#------------------------------------------------
# 1) Conexión a RoboDK e inicialización
#------------------------------------------------
RDK = Robolink()

# Elegir un robot (si hay varios, aparece un popup)
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No se ha seleccionado un robot válido.")

# Conectar al robot físico
##if not robot.Connect():
##    raise Exception("No se pudo conectar al robot. Verifica que esté en modo remoto y que la configuración sea correcta.")

# Confirmar conexión
##if not robot.ConnectedState():
##    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

##print("Robot conectado correctamente.")

#------------------------------------------------
# 2) Cargar el Frame (ya existente) donde quieres dibujar
#    Ajusta el nombre si tu Frame se llama diferente
#------------------------------------------------
frame_name = "Frame_from_Target1"
frame = RDK.Item(frame_name, ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception(f'No se encontró el Frame "{frame_name}" en la estación.')

# Asignamos este frame al robot
robot.setPoseFrame(frame)
# Usamos la herramienta activa
robot.setPoseTool(robot.PoseTool())

# Ajustes de velocidad y blending
robot.setSpeed(300)   # mm/s - Ajusta según necesites
robot.setRounding(5)  # blending (radio de curvatura)

#------------------------------------------------
# 3) Parámetros de la figura (rosa polar)
#------------------------------------------------
num_points = 720       # Cuántos puntos muestreamos (mayor = más suave)
A = 150               # Amplitud (300 mm = radio máximo)
k = 5                  # Parámetro de la rosa (pétalos). Si es impar, habrá k pétalos; si es par, 2k
z_surface = 0          # Z=0 en el plano del frame
z_safe = 50            # Altura segura para aproximarse y salir

#------------------------------------------------
# 4) Movimiento al centro en altura segura
#------------------------------------------------
# Guardamos la pose segura "home relativa al frame"
home_pose = robot.Pose()

# El centro de la rosa (r=0) corresponde a x=0, y=0
robot.MoveJ(transl(0, 0, z_surface + z_safe))

# Bajamos a la "superficie" (Z=0)
robot.MoveL(transl(0, 0, z_surface))

#------------------------------------------------
# 5) Dibujar la rosa polar
#    r = A * sin(k*theta)
#    x = r*cos(theta), y = r*sin(theta)
#------------------------------------------------
# Recorremos theta de 0 a 2*pi (una vuelta completa)
##full_turn = 2*math.pi

##for i in range(num_points+1):
    # Fracción entre 0 y 1
##    t = i / num_points
    # Ángulo actual
##    theta = full_turn * t

    # Calculamos r
##    r = A * math.sin(k * theta)

    # Convertimos a coordenadas Cartesianas X, Y
##    x = r * math.cos(theta)
##    y = r * math.sin(theta)

    # Movemos linealmente (MoveL) en el plano del Frame
##    robot.MoveL(transl(x, y, z_surface))

#------------------------------------------------
# 5) Dibujar la lemniscata: r^2 = A^2 * sin(2θ)
#------------------------------------------------
full_turn = 2 * math.pi

for i in range(num_points+1):
    t = i / num_points
    theta = full_turn * t

    sin_2theta = math.sin(2 * theta)
    if sin_2theta < 0:
        continue  # Saltar puntos donde r^2 sería negativo

    r = A * math.sqrt(sin_2theta)

    x = r * math.cos(theta)
    y = r * math.sin(theta)

    robot.MoveL(transl(x, y, z_surface))

# Al terminar, subimos de nuevo para no chocar
robot.MoveL(transl(x, y, z_surface + z_safe))

# --------------------------------------------
# FUNCIONES PARA ESCRIBIR LETRAS LINEALES
# --------------------------------------------
def draw_letter(letter, offset_x=0, offset_y=0, scale=10):
    path = {
        'A': [(0,0),(0,1),(0.5,2),(1,1),(1,0),(0,1)],
        'N': [(0,0),(0,2),(1,0),(1,2)],
        'D': [(0,0),(0,2),(0.5,2),(1,1.5),(1,0.5),(0.5,0),(0,0)],
        'R': [(0,0),(0,2),(0.5,2),(1,1.5),(0.5,1),(1,0)],
        'E': [(1,2),(0,2),(0,1),(0.7,1),(0,1),(0,0),(1,0)],
        'S': [(1,2),(0,2),(0,1.5),(1,1.5),(1,1),(0,1),(0,0),(1,0)],
        'J': [(1,2),(1,0.2),(0.7,0),(0.3,0),(0,0.2)],
        'U': [(0,2),(0,0.3),(0.3,0),(0.7,0),(1,0.3),(1,2)]
    }

    pts = path.get(letter.upper())
    if not pts:
        return  # Letra no disponible

    # Mover a posición inicial
    robot.MoveJ(transl(offset_x + pts[0][0]*scale, offset_y + pts[0][1]*scale, z_surface + z_safe))
    robot.MoveL(transl(offset_x + pts[0][0]*scale, offset_y + pts[0][1]*scale, z_surface))

    for px, py in pts[1:]:
        x = offset_x + px * scale
        y = offset_y + py * scale
        robot.MoveL(transl(x, y, z_surface))

    robot.MoveL(transl(x, y, z_surface + z_safe))


def write_text(text, start_x, start_y, spacing=15):
    x = start_x
    for letter in text:
        if letter != ' ':
            draw_letter(letter, offset_x=x, offset_y=start_y)
        x += spacing

# --------------------------------------------
# ESCRIBIR "ANDRES" ARRIBA Y "JUAN" A LA DERECHA
# --------------------------------------------
write_text("ANDRES", start_x=-80, start_y=80)
write_text("JUAN", start_x=100, start_y=10)

robot.MoveJ(home_pose)

print(f"¡Lemniscata y nombres completados en el frame '{frame_name}'!")
