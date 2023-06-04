# Autores: Camilo Henrique Martins dos Santos (202004940027)
#          Eude Monteiro da Hora (202004940004)


#Imports
from grid import Grid
import numpy as np
import math

# Inicializa a grid
grid = Grid(extent=10, size=500)


def render_cells(selected_cells, rendered_cells, parameters):
    for cell in selected_cells:
        grid.render_cell(cell)


def translate(selected_cells, rendered_cells, parameters):
    
    x_offset = int(parameters['X'])  
    y_offset = int(parameters['Y'])  

    grid._clear_all()

    # Renderiza as novas células decorrentes da translação
    for cell in rendered_cells:
        new_cell = (cell[0] + x_offset, cell[1] + y_offset)
        grid.render_cell(new_cell)


   
def bresenham(selected_cells, rendered_cells=None, parameters=None):
    if len(selected_cells) != 2:
        print("O algoritmo requer exatamente duas células selecionadas.")
        return
    
    cell1, cell2 = selected_cells[0], selected_cells[1]
    
    x1, y1 = cell1
    x2, y2 = cell2
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    err = dx - dy
    
    line_coordinates = []
    
    while True:
        line_coordinates.append((x1, y1))
        
        if x1 == x2 and y1 == y2:
            break
        
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    for cell in line_coordinates:
        grid.render_cell(cell)

    grid.vertices = selected_cells



def draw_circle(selected_cells, rendered_cells, parameters):
    radius = int(parameters['Raio'])     
    if len(selected_cells) != 0:
        center_x,center_y = selected_cells[0][0], selected_cells[0][1]
    else:
        center_x = int(parameters['X do centro'])  
        center_y = int(parameters['Y do centro'])  

    x = radius
    y = 0
    decision = 1 - radius
    grid._clear_all()
    
    def plot_circle(center_x, center_y, x, y):
        """
        Realiza o plot do círculo utilizando as 
        coordenadas do centro e coordenadas relativas
        """

        # Reflexão de pontos em octantes (simetria)
        points = [(x, y), (-x, y), (x, -y), (-x, -y), (y, x), (-y, x), (y, -x), (-y, -x)]
        for point in points:
            grid.render_cell((center_x + point[0], center_y + point[1]))

    while x >= y:
        plot_circle(center_x, center_y, x, y)

        y += 1
        if decision <= 0:
            decision += 2 * y + 1
        else:
            x -= 1
            decision += 2 * (y - x) + 1
    
    # Redesenha a grid após renderização
    grid._redraw()



def recursive_fill(selected_cells, rendered_cells, parameters):
    
    filled_cells = []

    def flood_fill(x, y, edge_pixels, rendered_pixels):
        point = (x,y)

        if ((abs(x) > 10 or abs(y) > 10) or
           (point in edge_pixels) or 
           (point in rendered_pixels)):
            return 
        
        rendered_pixels.append(point)

        flood_fill(x+1, y, edge_pixels, rendered_pixels)
        flood_fill(x-1, y, edge_pixels, rendered_pixels)
        flood_fill(x, y+1, edge_pixels, rendered_pixels)
        flood_fill(x, y-1, edge_pixels, rendered_pixels)

        return rendered_pixels
    
    result = flood_fill(selected_cells[0][0], 
                        selected_cells[0][1],
                        rendered_cells, 
                        filled_cells)
    
    for point in result:        
        grid.raster.fill_cell((point))


def scanline_fill(selected_cells, rendered_cells, parameters):
    # Altura máxima e mínima da varredura
    min_y = min(point[1] for point in rendered_cells)
    max_y = max(point[1] for point in rendered_cells)

    # Varredura vertical
    for y in range(min_y, max_y + 1):
        # Intersecção entre as células coloridas
        # e arestas do polígono

        intersections = []
        for i, cell in enumerate(rendered_cells):
            x1, y1 = cell
            x2, y2 = rendered_cells[(i+1) % len(rendered_cells)]

            if (y1 <= y < y2) or (y2 <= y < y1):
                # Cálculo das intersecções
                x_intersect = int(x1 + (float(y - y1) / (y2 - y1)) * (x2 - x1))
                intersections.append(x_intersect)

        # Ordenação crescente  das coordenadas x
        intersections.sort()

        # Preenchimento dos pixels entre intersecções subsequentes
        for i in range(0, len(intersections), 2):
            x_start = intersections[i]
            x_end = intersections[i+1] if i+1 < len(intersections) else x_start

            # Preenchimento dos pixels entre os pontos de intersecção
            for x in range(x_start, x_end + 1):
                grid.raster.fill_cell((x, y))


def polyline(selected_cells, rendered_cells, parameters):
    
    if len(selected_cells) == 2:
        bresenham(selected_cells)
        return
    
    elif len(selected_cells) > 2:
        selected = selected_cells.copy()
    
    else:
        return
    
    length = len(selected)

    for i in range(length):
        if i+1 < length:
            draw = (selected[i],selected[i+1])
        else:
            draw = (selected[0],selected[i])

        bresenham(draw)
        grid.vertices = selected_cells



def scale(selected_cells, rendered_cells, parameters):
    
    x_factor = int(parameters['X'])
    y_factor = int(parameters['Y'])
    fixed_point = (int(parameters['FX']), int(parameters['FY']))
    
    points = grid.vertices.copy()
    new_points = []
    
    for i in range(len(points)):
        point = points[i]
        x = fixed_point[0] + (point[0] - fixed_point[0]) * x_factor
        y = fixed_point[1] + (point[1] - fixed_point[1]) * y_factor
        
        new_points.append((x,y))
        
    grid._clear_all()
    polyline(new_points,rendered_cells,parameters)



def cut(selected_cells, rendered_cells, parameters):
    
    x_list = [selected_cells[0][0],selected_cells[1][0]]
    y_list = [selected_cells[0][1],selected_cells[1][1]]
    x_max = max(x_list)
    x_min = min(x_list)
    y_max = max(y_list)
    y_min = min(y_list)
    for cell in rendered_cells:
        if ((x_min <= cell[0]) and (cell[0] <= x_max)) and ((y_min <= cell[1]) and (cell[1] <= y_max)):
            continue
        grid.clear_cell(cell)
      


def bezier_curve(selected_cells, rendered_cells, parameters):
    # Calcula o grau da curva
    degree = len(selected_cells) - 1

    # Verifica se há pontos de controle suficientes
    if degree + 1 < 3:
        return

    # Número de pontos a gerar na curva
    num_points = 100

    # Gera valores de t de 0 a 1
    t_values = [t / num_points for t in range(num_points + 1)]

    # Calcula os pontos na curva de Bezier
    for t in t_values:
        x = y = 0

        # Calcula as coordenadas x e y para o valor de t atual
        for i in range(degree + 1):
            coefficient = math.comb(degree, i)
            b = coefficient * (1 - t) ** (degree - i) * t ** i
            x += selected_cells[i][0] * b
            y += selected_cells[i][1] * b

        point = (int(x), int(y))
       
        rendered_cells.append(point)
        bresenham(rendered_cells[-2:], rendered_cells, parameters)



def rotation(selected_cells, rendered_cells, parameters):
    grid._clear_all()

    ang = np.deg2rad(float(parameters['Ângulo']))  
    x_pivot = int(parameters['X do pivô'])
    y_pivot = int(parameters['Y do pivô'])

    cells = rendered_cells.copy()

    for i in range(len(cells)):
        x = cells[i][0] - x_pivot
        y = cells[i][1] - y_pivot

        x_rot = int(round(x*np.cos(ang) - y * np.sin(ang)))
        y_rot = int(round(x*np.sin(ang)+y*np.cos(ang)))
        
        x_rot += x_pivot
        y_rot += y_pivot

        cells[i] = (x_rot,y_rot)
        
    for cell in cells:
        grid.render_cell(cell)


#Adição dos algoritmos à grid
grid.add_algorithm(name='Renderizar', parameters=None, algorithm=render_cells)

grid.add_algorithm(name='Bresenham', parameters=None, algorithm=bresenham)

grid.add_algorithm(name='Translação', parameters=['X', 'Y'], algorithm=translate)

grid.add_algorithm(name='Rotação', parameters=['Ângulo', 'X do pivô', 'Y do pivô'], algorithm=rotation)

grid.add_algorithm(name='Escala', parameters=['X','Y','FX','FY'], algorithm=scale)

grid.add_algorithm(name='Polilinha', parameters=None, algorithm=polyline)

grid.add_algorithm(name='Círculo', parameters=['Raio', 'X do centro', 'Y do centro'], algorithm=draw_circle)

grid.add_algorithm(name='Preenchimento (Recursivo)', parameters=None, algorithm=recursive_fill)

grid.add_algorithm(name='Preenchimento (Varredura)', parameters=None, algorithm=scanline_fill)

grid.add_algorithm(name='Curva de Bezier', parameters=None, algorithm=bezier_curve)

grid.add_algorithm(name='Recorte', parameters=None, algorithm=cut)

grid.show()