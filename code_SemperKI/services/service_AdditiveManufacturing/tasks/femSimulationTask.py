"""
Part of Semper-KI software

Alexander Peetz 2025
Silvio Weging 2025

Contains: FEM simulation
"""

import sys, time, io, pytetwild, meshio, tempfile
import numpy as np

from skfem import *
from skfem.models.elasticity import linear_elasticity, lame_parameters, linear_stress
from skfem.helpers import sym_grad

##################################################
####
# 3D FEM Simulation mit Skfem
# Variablen: "material", "pressure", "stl_file", "test_type"
#       material: JSON-String mit Materialdaten
#       pressure: Druckkraft in Pascal
#       stl_file: Pfad zur STL-Datei
#       test_type: Art des Tests ("compression" oder "tension")

# Rückgabe: Statistische Auswertung der Simulation

##################################################
mockMaterials = {
    "PLA": {"Youngs Modulus": 2636e6, "Poisson Ratio": 0.327, "Yielding Stress": 54.4e6, "Elon_at_break": 0.051},
    "PLA_Chacon": {"Youngs Modulus": 3587e6, "Poisson Ratio": 0.35, "Yielding Stress": 54.65e6, "Elon_at_break": 0.05}, #Werte Entnommen aus Chacon et al. 2017
    "PA12": {"Youngs Modulus": 2022e6, "Poisson Ratio": 0.4, "Yielding Stress": 50e6, "Elon_at_break": 0.042},
    "PLA_Claudio": {"Youngs Modulus": 2798e6, "Poisson Ratio": 0.327, "Yielding Stress": 64.083e6, "Elon_at_break": 0.04},
}

##################################################
def calculate_surface_area(mesh_data):
    """
    Berechnet die Gesamtoberfläche einer STL-Datei durch Summierung der Dreiecksflächen.
    """
    
    vertices = mesh_data.points
    triangles = mesh_data.cells_dict["triangle"]
    
    total_area = 0.0
    for triangle in triangles:
        # Hole die drei Punkte des Dreiecks
        v1 = vertices[triangle[0]]
        v2 = vertices[triangle[1]]
        v3 = vertices[triangle[2]]
        
        # Berechne zwei Vektoren des Dreiecks
        vector1 = v2 - v1
        vector2 = v3 - v1
        
        # Berechne die Fläche mit dem Kreuzprodukt
        cross_product = np.cross(vector1, vector2)
        area = 0.5 * np.linalg.norm(cross_product)
        
        total_area += area
    
    return total_area

##################################################
def calculate_bbox_volume_ratio(mesh_data):
    """
    Berechnet das Verhältnis von Oberfläche zu Bounding-Box-Volumen.
    """
    
    vertices = mesh_data.points
    
    # Berechne Bounding Box
    bbox_min = np.min(vertices, axis=0)
    bbox_max = np.max(vertices, axis=0)
    bbox_dims = bbox_max - bbox_min
    bbox_volume = np.prod(bbox_dims)  # Länge * Breite * Höhe
    
    # Berechne Oberfläche
    surface_area = calculate_surface_area(mesh_data)
    
    # Berechne Verhältnis
    ratio = surface_area / bbox_volume if bbox_volume > 0 else 0
    return ratio

##################################################
def calculate_bounding_box(mesh):
    bbox_min = np.min(mesh.p, axis=1)
    bbox_max = np.max(mesh.p, axis=1)
    bbox_dims = bbox_max - bbox_min
    bbox_length = {'x': bbox_dims[0], 'y': bbox_dims[1], 'z': bbox_dims[2]}
    return bbox_length

##################################################
def pid_controller(setpoint, current_value, prev_error, integral, Kp, Ki, Kd, dt):
    #Regelungstechnik zur Bestimmung der richtigen Mesh Dichte.
    #ist nach dem 
    error = setpoint - current_value
    integral += error * dt
    derivative = (error - prev_error) / dt
    output = -(Kp * error + Ki * integral + Kd * derivative)  # Invertiert für korrekte Anpassung
    return output, error, integral

##################################################
def determine_opt_amount_Tets(mesh_data):
    #ein einfacher Dreisatz zur Bestimmung des richtigen Tetraeder Verhältnisses
    # für unser Simulationsobjekt
     ratio = calculate_bbox_volume_ratio(mesh_data)
     calc_ratio_TOSV = 0.190595 #for 10000 Tets
     result = (ratio * 10000) / calc_ratio_TOSV
     return result, ratio

##################################################
def determine_ELF(mesh_data):
    #Bestimmung des Parameters edge_length_fac (Netzdichte)für das Simulationsobjekt
    #Ziel ist nicht zu viele und nicht zu wenige Tetraeder zu generieren, da sonst
    #Simulationsfehler auftreten können
    Setpoint_value, ratio = determine_opt_amount_Tets(mesh_data)
    
    SETPOINT = Setpoint_value
    Kp = 0.0002
    Ki = 0.00002
    Kd = 0.0001
    edge_length_fac = 0.1
    prev_error = 0
    integral = 0
    dt = 1.0
    
    min_correction = 0.0002
    max_correction = 0.02
    correction_scale = 0.7
    
    min_elements = float('inf')
    max_elements = 0
    
    
    successful_runs = []
    best_run = None
    best_difference = float('inf')
    
    tolerance = 0.10
    min_iterations = 3
    
    for iteration in range(20):
        try:
            vertices, tetrahedras = pytetwild.tetrahedralize(
                mesh_data.points, 
                mesh_data.cells_dict["triangle"], 
                optimize=True, 
                edge_length_fac=edge_length_fac
            )
            num_elements = len(tetrahedras)
            min_elements = min(min_elements, num_elements)
            max_elements = max(max_elements, num_elements)
            successful_runs.append((edge_length_fac, num_elements))          
            relative_error = abs(SETPOINT - num_elements) / SETPOINT
            if iteration >= min_iterations and relative_error <= tolerance:
                # print(f"\nZielwert erreicht mit {num_elements:,} Tetraedern!", flush=True)
                # print(f"Relative Abweichung: {relative_error*100:.1f}% (Toleranz: {tolerance*100:.1f}%)")
                # print(f"Abbruch nach {iteration + 1} Iterationen")
                return edge_length_fac
            
            current_difference = abs(SETPOINT - num_elements)
            if current_difference < best_difference:
                best_difference = current_difference
                best_run = (edge_length_fac, num_elements)
            
            correction, prev_error, integral = pid_controller(
                SETPOINT, num_elements, prev_error, integral, Kp, Ki, Kd, dt
            )
            
            correction_factor = min(0.7, relative_error * correction_scale)
            
            if num_elements < SETPOINT * 0.2:
                correction *= 1.5
            elif num_elements > SETPOINT * 1.5:
                correction *= 0.7
            
            max_adjust = max_correction * correction_factor
            correction = np.clip(correction, -max_adjust, max_adjust)
            
            if relative_error < 0.3:
                correction *= 0.5
            elif relative_error < 0.5:
                correction *= 0.7
            
            if abs(correction) < min_correction and relative_error > 0.1:
                correction = np.sign(correction) * min_correction
            
            new_edge_length_fac = edge_length_fac + correction
            edge_length_fac = np.clip(new_edge_length_fac, 0.01, 0.95)

            if abs(SETPOINT - num_elements) < SETPOINT * 0.05:
                break
                
        except Exception as e:

            if successful_runs:
                edge_length_fac = successful_runs[-1][0] * 0.8
            else:
                edge_length_fac = max(0.01, edge_length_fac * 0.8)
        
        sys.stdout.flush()
        time.sleep(0.5)
    
 
    #for idx, (elf, num) in enumerate(successful_runs, 1):
        #print(f"Durchlauf {idx}: ELF={elf:.4f}, Tetraeder={num:,}", flush=True)
    
    if best_run:
        #print(f"\nBester Durchlauf: ELF={best_run[0]:.4f} mit {best_run[1]:,} Tetraedern")
        #print(f"Abweichung vom Zielwert: {abs(SETPOINT-best_run[1]):,} ({abs(SETPOINT-best_run[1])/SETPOINT*100:.1f}%)")
        return best_run[0]
    return 0.01

##################################################
def read_and_tetrahedralize(mesh_data, elf):
    #tetrahedralisierung der STL_FILE mit edge_length_fac

    vertices, tetrahedras = pytetwild.tetrahedralize(mesh_data.points, mesh_data.cells_dict["triangle"], optimize=True, edge_length_fac=elf)
    p, t = np.array(vertices.T, dtype=np.float64), np.array(tetrahedras, dtype=np.float64).T
    return MeshTet(p, t)

##################################################
def define_dofs(ib):
    #definiere Degrees Of Freedom mit dem einfachen Fall,
    #dass wir die Ränder der BBox erfasst werden
    return {
        'links': ib.get_dofs(lambda x: np.isclose(x[0], x[0].min())),
        'rechts': ib.get_dofs(lambda x: np.isclose(x[0], x[0].max())),
        'oben': ib.get_dofs(lambda x: np.isclose(x[1], x[1].max())),
        'unten': ib.get_dofs(lambda x: np.isclose(x[1], x[1].min())),
        'vorne': ib.get_dofs(lambda x: np.isclose(x[2], x[2].max())),
        'hinten': ib.get_dofs(lambda x: np.isclose(x[2], x[2].min()))
    }

##################################################
def define_displacements(pressure, test_type):
    #Bsp.: Auf die linke Seite des Objektes wirkt gewünschter Druck, 
    #rechte Seite wird fixiert und ein Druck, oder Streckversuch wird simuliert
    return {
        'links': ('rechts', 'u^1', pressure if test_type == 'compression' else -pressure, 'x'),
        'rechts': ('links', 'u^1', -pressure if test_type == 'compression' else pressure, 'x'),
        'oben': ('unten', 'u^2', -pressure if test_type == 'compression' else pressure, 'y'),
        'unten': ('oben', 'u^2', pressure if test_type == 'compression' else -pressure, 'y'),
        'vorne': ('hinten', 'u^3', -pressure if test_type == 'compression' else pressure, 'z'),
        'hinten': ('vorne', 'u^3', pressure if test_type == 'compression' else -pressure, 'z')
    }

##################################################
def yield_stress(array, threshold):
    # überprüft, ob Von Mises Spannung allen Tetraedern überschritten wurde
    " threshold: yielding stress of material"
    " array: von-mises-stress of all elements"
    max_stress = np.max(array)
    stress_percentage = (max_stress / threshold) * 100
    plastic_elements = [i for i in range(len(array)) if array[i] > threshold]
    return {'stress percentage': stress_percentage, 'plastic': plastic_elements}

##################################################
def calculate_displacements_and_stresses(mesh, lame_params, poisson_ratio, ib, K, dofs, displacements, bbox_length, material):
    # 
    results = {}
    for direction, (opposite, component, press_value, bbox_side) in displacements.items():
        u, F = ib.zeros(), np.zeros(ib.zeros().shape)
        direction_dofs = dofs[direction].nodal[component].astype(int).flatten()
        F[direction_dofs] = press_value
        fixed_dofs = np.hstack([dofs[opposite].all()])
        u[fixed_dofs] = 0
        free_dofs = np.setdiff1d(np.arange(K.shape[0]), fixed_dofs)
        u[free_dofs] = solve(K[free_dofs][:, free_dofs], F[free_dofs])
        initial_shift = u[direction_dofs]
        u = solve(*condense(K, x=u, I=ib.complement_dofs(np.concatenate([dofs[direction], dofs[opposite]]))))
        sf = 1
        m_shifted = mesh.translated(sf * u[ib.nodal_dofs])
        
        ## calculate total Nodal displacement
        abs_value_Nodal_shift = np.sqrt(u[ib.nodal_dofs][0]**2 + u[ib.nodal_dofs][1]**2 + u[ib.nodal_dofs][2]**2)
        elongation = [abs_value_Nodal_shift[i] / bbox_length[bbox_side] for i in range(len(abs_value_Nodal_shift))]
        broke_at_elongation = [elongation[i] > material["Elon_at_break"] for i in range(len(elongation))]
        num_plastic_points = sum(broke_at_elongation)
        
        s, dgb = {}, ib.with_element(ElementTetP0())
        up = ib.interpolate(u) 
        C = linear_stress(*lame_params)
        for i in [0, 1]:
            for j in [0, 1]:
                s[i, j] = dgb.project(C(sym_grad(up))[i, j])
        s[2, 2] = poisson_ratio * (s[0, 0] + s[1, 1])
        vonmises = np.sqrt(.5 * ((s[0, 0] - s[1, 1]) ** 2 + (s[1, 1] - s[2, 2]) ** 2 + (s[2, 2] - s[0, 0]) ** 2 + 6. * s[0, 1] ** 2))
        yield_results = yield_stress(vonmises, material['Yielding Stress'])
        result_info = {
            'Anz. zerstörter Elemente': len(yield_results['plastic']),
            'max. Spannungsverhältnis': f"{yield_results['stress percentage']:.4f}%",
            'Anz. überdehnter Knoten': num_plastic_points,
            'max. Dehnung': f"{np.max(elongation):.4f}",
        }
        results[direction] = result_info
    return results

##################################################
def calculate_average_results(results_list):
    """Berechnet Mittelwerte der Simulationsergebnisse"""
    avg_results = {}
    for direction in results_list[0].keys():
        avg_results[direction] = {
            'Anz. zerstörter Elemente': np.mean([res[direction]['Anz. zerstörter Elemente'] for res in results_list]),
            'max. Spannungsverhältnis': f"{np.mean([float(res[direction]['max. Spannungsverhältnis'].strip('%')) for res in results_list]):.4f}%",
            'Anz. überdehnter Knoten': np.mean([res[direction]['Anz. überdehnter Knoten'] for res in results_list]),
            'max. Dehnung': f"{np.mean([float(res[direction]['max. Dehnung']) for res in results_list]):.4f}",
            'Standardabweichungen': {
                'zerstörte Elemente': np.std([res[direction]['Anz. zerstörter Elemente'] for res in results_list]),
                'Spannungsverhältnis': np.std([float(res[direction]['max. Spannungsverhältnis'].strip('%')) for res in results_list]),
                'überdehnte Knoten': np.std([res[direction]['Anz. überdehnter Knoten'] for res in results_list]),
                'Dehnung': np.std([float(res[direction]['max. Dehnung']) for res in results_list])
            }
        }
    return avg_results

##################################################
def run_FEM_test(material, pressure, stl_file, stl_fileName, test_type, resultQueue):
    try:# print("\nStarte FEM-Simulationen mit Mittelwertberechnung...")
        output_data = {}
        with tempfile.TemporaryDirectory() as tempDir: # because meshio.read does not accept BytesIO, we have to use this bs
            temporaryFileName = tempDir+"\\"+stl_fileName
            temporaryFile = open(temporaryFileName, 'wb')
            temporaryFile.write(stl_file)
            temporaryFile.close()

            mesh_data = meshio.read(temporaryFileName, file_format="stl")

            elf = round(determine_ELF(mesh_data), 4)    
            #print(f"edge_length_factor: {elf}")
            num_simulations = 5
            all_results = []
            
            for i in range(num_simulations):
                #print(f"\nSimulation {i+1}/{num_simulations}")
                try:
                    mesh = read_and_tetrahedralize(mesh_data, elf)
                    bbox_length = calculate_bounding_box(mesh)
                    e1, e = ElementTetP1(), ElementVector(ElementTetP1())
                    ib = Basis(mesh, e, MappingIsoparametric(mesh, e1), 3)
                    young_modulus, poisson_ratio = material["Youngs Modulus"], material["Poisson Ratio"]
                    lame_params = lame_parameters(young_modulus, poisson_ratio)
                    K = asm(linear_elasticity(*lame_params), ib)
                    dofs = define_dofs(ib)
                    displacements = define_displacements(pressure, test_type)
                    results = calculate_displacements_and_stresses(mesh, lame_params, poisson_ratio, ib, K, dofs, displacements, bbox_length, material)
                    all_results.append(results)
                    #print(f"Simulation {i+1} erfolgreich")
                except Exception as e:
                    #print(f"Fehler in Simulation {i+1}: {e}")
                    continue
            
            if not all_results:
                raise RuntimeError("Keine erfolgreichen Simulationen durchgeführt")
            
        
            #print("\nBerechne Mittelwerte und Standardabweichungen...")
            avg_results = calculate_average_results(all_results)
            result_simulation = any(avg_results[direction]['Anz. zerstörter Elemente'] > 0 for direction in avg_results)
            
            # Ausgabe der Statistiken
            #print("\nStatistische Auswertung:")
            output_data = {
                "Plastische Verschiebung?": result_simulation,
                "Statistische Auswertung": {}
            }
            
            for direction in avg_results:
                output_data["Statistische Auswertung"][direction] = {
                    "Mittlere Anzahl zerstörter Elemente": f"{avg_results[direction]['Anz. zerstörter Elemente']:.2f} ± {avg_results[direction]['Standardabweichungen']['zerstörte Elemente']:.2f}",
                    "Mittleres Spannungsverhältnis": f"{avg_results[direction]['max. Spannungsverhältnis']} ± {avg_results[direction]['Standardabweichungen']['Spannungsverhältnis']:.2f}%",
                    # "Mittlere Anzahl überdehnter Knoten": f"{avg_results[direction]['Anz. überdehnter Knoten']:.2f} ± {avg_results[direction]['Standardabweichungen']['überdehnte Knoten']:.2f}",
                    "Mittlere maximale Dehnung": f"{avg_results[direction]['max. Dehnung']} ± {avg_results[direction]['Standardabweichungen']['Dehnung']:.4f}"
                }

        resultQueue.put(output_data)
    except Exception as e:
        print(f"Error in FEM-Simulation: {e}")
        resultQueue.put({"Error": str(e)})

##################################################
# When used as a script
# def __main__(args):
#     material = str(args)
#     pressure = float(args[1])    
#     stl_file = str(args[2])
#     test_type = str(args[3])
#     result = run_FEM_test( material,pressure, stl_file, test_type)
#     return result

# __main__(sys.argv[1:])


    
