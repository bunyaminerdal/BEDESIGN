import ast
import math
import os
import sys
import json
import numpy as np
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


def read_bedb(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = ast.literal_eval(f.read())
    return data


def section_props(sec):
    t = sec.get('type','rectangular')
    if t == 'rectangular':
        h = float(sec.get('h',1.0))
        b = float(sec.get('b',1.0))
        A = h * b
        I = b * h**3 / 12.0
        return A, I
    if t == 'rectangularbar':
        h = float(sec.get('h',1.0)); b = float(sec.get('b',1.0))
        A = h*b; I = b*h**3/12.0; return A,I
    if t == 'circular' or t=='circularbar':
        d = float(sec.get('d',1.0))
        tck = sec.get('thickness', None)
        if tck:
            t = float(tck)
            A = math.pi*(d**2 - (d-2*t)**2)/4.0
            I = math.pi*(d**4 - (d-2*t)**4)/64.0
        else:
            A = math.pi*d**2/4.0
            I = math.pi*d**4/64.0
        return A,I
    # rough approximations for other shapes
    h = float(sec.get('h',1.0))
    b = float(sec.get('b', sec.get('btop', sec.get('bbottom',1.0))))
    t = float(sec.get('bthickness', sec.get('bthickness',1.0) or 1.0))
    A = (h * t) + (b * t)
    I = b * h**3 / 12.0
    return A, I


def local_stiffness(E,A,I,L):
    # 2D frame local stiffness (6x6) for two-node element
    k = np.zeros((6,6))
    k[0,0] = A*E/L
    k[0,3] = -A*E/L
    k[3,0] = -A*E/L
    k[3,3] = A*E/L

    k[1,1] = 12*E*I/(L**3)
    k[1,2] = 6*E*I/(L**2)
    k[1,4] = -12*E*I/(L**3)
    k[1,5] = 6*E*I/(L**2)

    k[2,1] = 6*E*I/(L**2)
    k[2,2] = 4*E*I/L
    k[2,4] = -6*E*I/(L**2)
    k[2,5] = 2*E*I/L

    k[4,1] = -12*E*I/(L**3)
    k[4,2] = -6*E*I/(L**2)
    k[4,4] = 12*E*I/(L**3)
    k[4,5] = -6*E*I/(L**2)

    k[5,1] = 6*E*I/(L**2)
    k[5,2] = 2*E*I/L
    k[5,4] = -6*E*I/(L**2)
    k[5,5] = 4*E*I/L
    return k


def transform_matrix(c, s):
    # transform 6x6 for 2D frame (ux, uz, rot) per node
    T = np.zeros((6,6))
    R = np.array([[c, s, 0], [-s, c, 0], [0,0,1]])
    T[0:3,0:3] = R
    T[3:6,3:6] = R
    return T


def assemble(data):
    joints = [j for j in data['joints'] if not j.get('deleted', False)]
    joints_sorted = sorted(joints, key=lambda x: x['name'])
    nid_map = {j['name']: idx for idx,j in enumerate(joints_sorted)}
    nnode = len(joints_sorted)
    ndof = 3 * nnode

    elements = [f for f in data['frames'] if not f.get('deleted', False)]

    K = np.zeros((ndof, ndof))
    F = np.zeros(ndof)

    elem_info = []

    # prepare materials and sections
    mats = {m['index']: m for m in data.get('materials', [])}
    secs = {s['index']: s for s in data.get('sections', [])}

    for el in elements:
        n1 = nid_map[el['joint0']]
        n2 = nid_map[el['joint1']]
        x1,z1 = joints_sorted[n1]['coords'][0], joints_sorted[n1]['coords'][2]
        x2,z2 = joints_sorted[n2]['coords'][0], joints_sorted[n2]['coords'][2]
        dx = x2 - x1
        dz = z2 - z1
        L = math.hypot(dx, dz)
        if L <= 0:
            continue
        c = dx / L
        s = dz / L

        sec = secs.get(el.get('section', None)) or secs.get(data.get('sectionindex', None))
        if sec is None:
            A,I = 1.0, 1.0
            E = 1.0
        else:
            A,I = section_props(sec)
            matidx = sec.get('matindex', data.get('matindex',1))
            mat = mats.get(matidx, {})
            E = float(mat.get('E',1.0))

        k_loc = local_stiffness(E,A,I,L)
        T = transform_matrix(c,s)
        k_glob = T.T @ k_loc @ T

        dofs = [3*n1, 3*n1+1, 3*n1+2, 3*n2, 3*n2+1, 3*n2+2]
        for i in range(6):
            for j in range(6):
                K[dofs[i], dofs[j]] += k_glob[i,j]

        elem_info.append({'id': el['name'], 'n1':n1, 'n2':n2, 'L':L, 'c':c, 's':s, 'k_loc':k_loc, 'T':T, 'E':E, 'A':A, 'I':I})

    # loads: try loads.json in same folder
    loads_file = 'loads.json'
    if os.path.exists(loads_file):
        with open(loads_file,'r') as f:
            loads = json.load(f)
        for ld in loads.get('nodal',[]):
            nid = nid_map[ld['node']]
            idx = 3*nid
            F[idx + 0] += ld.get('Fx',0.0)
            F[idx + 1] += ld.get('Fz',0.0)
            F[idx + 2] += ld.get('Mz',0.0)

    # apply supports
    fixed = []
    for j in joints_sorted:
        idx = 3*nid_map[j['name']]
        res = j.get('restraints',[0,0,0,0,0,0])
        if res[0]: fixed.append(idx+0)
        if res[2]: fixed.append(idx+1)
        if res[4]: fixed.append(idx+2)

    free_dofs = [i for i in range(ndof) if i not in fixed]

    Kff = K[np.ix_(free_dofs, free_dofs)]
    Ff = F[free_dofs]

    # solve
    if Kff.size == 0:
        U = np.zeros(ndof)
    else:
        try:
            Uf = np.linalg.solve(Kff, Ff)
        except np.linalg.LinAlgError:
            Uf = np.linalg.lstsq(Kff, Ff, rcond=None)[0]
        U = np.zeros(ndof)
        for i, dof in enumerate(free_dofs):
            U[dof] = Uf[i]

    # reactions
    R = K @ U - F

    results = {'U':U.tolist(), 'R':R.tolist(), 'elem':[]}

    # element end forces (local)
    for e in elem_info:
        n1 = e['n1']; n2 = e['n2']
        dofs = [3*n1,3*n1+1,3*n1+2,3*n2,3*n2+1,3*n2+2]
        u_e_global = np.array([U[d] for d in dofs])
        u_e_local = e['T'] @ u_e_global
        f_local = e['k_loc'] @ u_e_local
        # axial N is f_local[0] (positive tension), shear V at node1 is f_local[1], moment M at node1 is f_local[2]
        results['elem'].append({'id': e['id'], 'n1': e['n1'], 'n2': e['n2'], 'L': e['L'], 'N1': float(f_local[0]), 'V1': float(f_local[1]), 'M1': float(f_local[2]), 'N2': float(f_local[3]), 'V2': float(f_local[4]), 'M2': float(f_local[5])})

        # save simple linear diagrams (end values) to files
        base = f"elem_{e['id']}"
        with open(base + '_N.txt','w') as f:
            f.write('x N\n')
            f.write(f"0 {f_local[0]}\n")
            f.write(f"{e['L']} {f_local[3]}\n")
        with open(base + '_V.txt','w') as f:
            f.write('x V\n')
            f.write(f"0 {f_local[1]}\n")
            f.write(f"{e['L']} {f_local[4]}\n")
        with open(base + '_M.txt','w') as f:
            f.write('x M\n')
            f.write(f"0 {f_local[2]}\n")
            f.write(f"{e['L']} {f_local[5]}\n")

    return results


def pretty_print(raw, results):
    print('--- Displacements (per node: ux, uz, rot) ---')
    joints = [j for j in raw['joints'] if not j.get('deleted', False)]
    joints_sorted = sorted(joints, key=lambda x: x['name'])
    U = np.array(results['U'])
    for i,j in enumerate(joints_sorted):
        ux, uz, rz = U[3*i], U[3*i+1], U[3*i+2]
        print(f"Node {j['name']}: ux={ux:.6g}, uz={uz:.6g}, rot={rz:.6g}")

    print('\n--- Reactions (global DOFs) ---')
    R = np.array(results['R'])
    for i,r in enumerate(R):
        if abs(r) > 1e-12:
            print(f"DOF {i}: R={r:.6g}")

    print('\n--- Element end forces (local) ---')
    for e in results['elem']:
        print(f"Elem {e['id']}: N1={e['N1']:.6g}, V1={e['V1']:.6g}, M1={e['M1']:.6g} | N2={e['N2']:.6g}, V2={e['V2']:.6g}, M2={e['M2']:.6g}")


def plot_results(raw, results):
    if plt is None:
        print('matplotlib not available; skipping plots')
        return
    joints = [j for j in raw['joints'] if not j.get('deleted', False)]
    joints_sorted = sorted(joints, key=lambda x: x['name'])
    U = np.array(results['U'])

    # Displacements plot
    idx = [j['name'] for j in joints_sorted]
    ux = [U[3*i] for i in range(len(joints_sorted))]
    uz = [U[3*i+1] for i in range(len(joints_sorted))]
    plt.figure(figsize=(8,4))
    plt.plot(idx, ux, marker='o', label='ux')
    plt.plot(idx, uz, marker='s', label='uz')
    plt.xlabel('Node')
    plt.ylabel('Displacement')
    plt.title('Nodal Displacements')
    plt.grid(True)
    plt.legend()
    plt.savefig('displacements.png', dpi=150)
    plt.close()

    # Element diagrams
    for e in results['elem']:
        base = f"elem_{e['id']}"
        L = float(e.get('L', 1.0))
        npts = 101
        xs = np.linspace(0.0, L, npts)
        # linear interpolation between end values (sufficient for unloaded element)
        Nvals = np.linspace(e['N1'], e['N2'], npts)
        Vvals = np.linspace(e['V1'], e['V2'], npts)
        Mvals = np.linspace(e['M1'], e['M2'], npts)

        plt.figure()
        plt.plot(xs, Nvals, marker=None)
        plt.title(f'Element {e["id"]} - Axial (N)')
        plt.xlabel('x (m)')
        plt.ylabel('Axial force')
        plt.grid(True)
        plt.savefig(base + '_N.png', dpi=150)
        plt.close()

        plt.figure()
        plt.plot(xs, Vvals, marker=None)
        plt.title(f'Element {e["id"]} - Shear (V)')
        plt.xlabel('x (m)')
        plt.ylabel('Shear force')
        plt.grid(True)
        plt.savefig(base + '_V.png', dpi=150)
        plt.close()

        plt.figure()
        plt.plot(xs, Mvals, marker=None)
        plt.title(f'Element {e["id"]} - Moment (M)')
        plt.xlabel('x (m)')
        plt.ylabel('Moment')
        plt.grid(True)
        plt.savefig(base + '_M.png', dpi=150)
        plt.close()

        # Deformed/undeformed shape along element
        # get node coordinates and displacements
        joints_map = {j['name']: j for j in joints_sorted}
        n1 = e['n1']; n2 = e['n2']
        # node names are indices in joints_sorted list
        j1 = joints_sorted[n1]
        j2 = joints_sorted[n2]
        x1, z1 = j1['coords'][0], j1['coords'][2]
        x2, z2 = j2['coords'][0], j2['coords'][2]
        dx = x2 - x1; dz = z2 - z1
        # nodal displacements
        ux1 = U[3*n1]; uz1 = U[3*n1+1]
        ux2 = U[3*n2]; uz2 = U[3*n2+1]

        X = x1 + (dx) * (xs / L)
        Z = z1 + (dz) * (xs / L)

        Ux_interp = ux1 + (ux2 - ux1) * (xs / L)
        Uz_interp = uz1 + (uz2 - uz1) * (xs / L)

        # scale deformation for visibility
        max_dim = max(abs(x2 - x1), abs(z2 - z1), 1.0)
        max_disp = max(np.max(np.abs(Ux_interp)), np.max(np.abs(Uz_interp)), 1e-9)
        scale = 0.1 * max_dim / max_disp

        Xd = X + Ux_interp * scale
        Zd = Z + Uz_interp * scale

        plt.figure()
        plt.plot([x1, x2], [z1, z2], 'k--', label='undeformed')
        plt.plot(Xd, Zd, 'r-', label=f'deformed x{scale:.1g}')
        plt.scatter([x1, x2], [z1, z2], c='k')
        plt.title(f'Element {e["id"]} - Shape (undeformed/deformed)')
        plt.xlabel('X')
        plt.ylabel('Z')
        plt.legend()
        plt.axis('equal')
        plt.grid(True)
        plt.savefig(base + '_shape.png', dpi=150)
        plt.close()

        # try opening PNGs
        try:
            if os.name == 'nt':
                os.startfile('displacements.png')
                os.startfile(base + '_N.png')
                os.startfile(base + '_V.png')
                os.startfile(base + '_M.png')
                os.startfile(base + '_shape.png')
        except Exception:
            pass


def main():
    bedb = sys.argv[1] if len(sys.argv) > 1 else '1.bedb'
    if not os.path.exists(bedb):
        print('BEDB file not found:', bedb); sys.exit(1)
    raw = read_bedb(bedb)
    res = assemble(raw)
    pretty_print(raw, res)
    # plot if matplotlib available
    if plt is not None:
        try:
            plot_results(raw, res)
        except Exception as e:
            print('Plotting failed:', e)
    print('\nDiagram files (N,V,M) saved as elem_<id>_*.txt in current directory.')


if __name__ == '__main__':
    main()
