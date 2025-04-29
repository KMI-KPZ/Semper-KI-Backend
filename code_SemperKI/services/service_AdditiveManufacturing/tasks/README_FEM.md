# Semper-KI FEM Simulation

Authors: **Alexander Peetz** & **Silvio Weging**  
Year: **2025**

---

### Overview

The platform contains a finite element simulation tool designed for 3D mechanical testing of arbitrary geometries described via STL files. It simulates simple compression or tension tests by automatically meshing the geometry and solving a linear elasticity problem.

The tool supports:

- Automatic tetrahedral meshing using pytetwild
- Material modeling based on experimental data
- Application of loads in all three directions (x, y, z)
- Stress and displacement calculation
- Statistical evaluation over multiple simulations
- PID-controlled adjustment of the mesh density in relation to the volume

### Purpose and Motivation

The goal of this project was to develop a fast, automated, and simple-to-use FEM simulation pipeline that could predict plastic deformation, verifying whether certain materials are suitable for a given use case.

As part of Alexander's Bachelor Thesis in Physics, this framework serves as a foundation for further research.

### Key Features:

- Automatic tetrahedral mesh generation with optimized mesh density via PID control
- Elastic linear stress-strain analysis
- Plasticity estimation based on yield stress and elongation at break
- Multipoint loading: compression/tension along x, y, z axes
- Statistical result averaging over multiple solutions
- Clear output metrics

### Libraries Used

- [`scikit-fem`](https://github.com/kinnala/scikit-fem) (Finite Element Solver)
- [`pytetwild`](https://github.com/wildmeshing/pytetwild) (Mesh Tetrahedralization)
- [`meshio`](https://github.com/nschloe/meshio) (Mesh I/O)
- `numpy` (Numerical Computation)

### Installation and Requirements

Make sure you have **Python ≥ 3.11** installed.

Install required libraries:

```bash
pip install numpy meshio scikit-fem pytetwild
```

Note: Installing pytetwild may require a C++ compiler and additional system dependencies.

### How to Use

1. Provide an STL file.
2. Define material properties (or use one of the built-in mock materials).
3. Call:

```python
run_FEM_test(material, pressure, stl_file, stl_fileName, test_type, resultQueue)
```

- `material`: Dictionary with material properties (Young's modulus, Poisson's ratio, etc.)
- `pressure`: Load in Pascals
- `stl_file`: Byte array of your STL file
- `stl_fileName`: Name of your STL file (used temporarily)
- `test_type`: `compression` or `tension`
- `resultQueue`: A multiprocessing queue to retrieve the results

### Results Interpretation

Each simulation outputs JSON:

- Did the material yield plastically [boolean]
- Statistical evaluation [float]:
    - Number of failed elements
    - Maximum stress ratio
    - Maximum elongation

### Known Issues and Limitations

#### Mesh Generation Instability

- The current pipeline uses pytetwild for tetrahedralization, but this library can sometimes crash, hang, or produce invalid meshes depending on the input STL.
- The PID controller for adjusting mesh density improves stability but cannot fully guarantee successful mesh generation for extremely complex or poor-quality STL files.

#### Simplified Material Model

- The simulation uses linear elasticity only.
- No true plastic deformation modeling (only yielding detection based on stress thresholds).

#### Boundary Conditions Are Idealized

- The load application assumes perfectly clamped faces and perfect pressure application, which might not fully represent real-world boundary effects.
- The allocation of the edges is done by defining the nodes at the borders of the bounding box, which is inconsistent under rotation.

#### Limited Geometry Preprocessing

- Bad or non-manifold STL files might cause errors without detailed feedback.

#### Errors Due to pytetwild

- In the current pipeline, errors caused by the pytetwild library may occur.

### Future Work

- Improve mesh robustness using additional preprocessing (e.g., smoothing, remeshing).
- Add full plasticity models (nonlinear FEM, plastic deformation tracking).
- Implement adaptive meshing at corners and edges.
- Determine specific boundary conditions for every use case via text prompt.

### Final Thoughts

This project provides a simple and extensible basis for automated FEM simulation on 3D geometries.

While it does not yet replace professional tools (e.g., ANSYS, Abaqus), it offers value for research and prototyping.




