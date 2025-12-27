use pyo3::prelude::*;
use pyo3::{Bound, types::PyModule};
use ascent::ascent;


fn same_orientation(l1: Vec<(i64, i64, String)>, l2: Vec<(i64, i64, String)>) -> bool {
    let edge_length = |p: (i64, i64, String), q: (i64, i64, String)| (q.0 - p.0) * (q.1 + p.1);

    let mut area1 = 0;
    for i in 0..l1.len() {
        area1 += edge_length(l1[i].clone(), l1[(i + 1) % l1.len()].clone());
    }

    let mut area2 = 0;
    for i in 0..l2.len() {
        area2 += edge_length(l2[i].clone(), l2[(i + 1) % l2.len()].clone());
    }

    return (area1 * area2) > 0;
}

#[pyclass]
struct DeductiveDatabase {
    // Input facts
    points: Vec<(i64, i64, String)>,
    col_facts: Vec<(String, String, String)>,
    para_facts: Vec<(String, String, String, String)>,
    perp_facts: Vec<(String, String, String, String)>,
    cong_facts: Vec<(String, String, String, String)>,
    eqangle_facts: Vec<(String, String, String, String, String, String)>,
    cyclic_facts: Vec<(String, String, String, String)>,
    sameclock_facts: Vec<(String, String, String, String, String, String)>,
    midp_facts: Vec<(String, String, String)>,
    contri1_facts: Vec<(String, String, String, String, String, String)>,
    contri2_facts: Vec<(String, String, String, String, String, String)>,
    simtri1_facts: Vec<(String, String, String, String, String, String)>,
    simtri2_facts: Vec<(String, String, String, String, String, String)>,
    eqratio_facts: Vec<(String, String, String, String, String, String, String, String)>,
    aconst_facts: Vec<(String, String, String, i32, i32)>,

    // Derived results
    derived_col: Vec<(String, String, String)>,
    derived_para: Vec<(String, String, String, String)>,
    derived_perp: Vec<(String, String, String, String)>,
    derived_cong: Vec<(String, String, String, String)>,
    derived_eqangle: Vec<(String, String, String, String, String, String)>,
    derived_cyclic: Vec<(String, String, String, String)>,
    derived_sameclock: Vec<(String, String, String, String, String, String)>,
    derived_midp: Vec<(String, String, String)>,
    derived_contri1: Vec<(String, String, String, String, String, String)>,
    derived_contri2: Vec<(String, String, String, String, String, String)>,
    derived_simtri1: Vec<(String, String, String, String, String, String)>,
    derived_simtri2: Vec<(String, String, String, String, String, String)>,
    derived_eqratio: Vec<(String, String, String, String, String, String, String, String)>,
    derived_aconst: Vec<(String, String, String, i32, i32)>,
}

#[pymethods]
impl DeductiveDatabase {
    #[new]
    fn new() -> Self {
        DeductiveDatabase {
            points: Vec::new(),
            col_facts: Vec::new(),
            para_facts: Vec::new(),
            perp_facts: Vec::new(),
            cong_facts: Vec::new(),
            eqangle_facts: Vec::new(),
            cyclic_facts: Vec::new(),
            sameclock_facts: Vec::new(),
            midp_facts: Vec::new(),
            contri1_facts: Vec::new(),
            contri2_facts: Vec::new(),
            simtri1_facts: Vec::new(),
            simtri2_facts: Vec::new(),
            eqratio_facts: Vec::new(),
            aconst_facts: Vec::new(),

            derived_col: Vec::new(),
            derived_para: Vec::new(),
            derived_perp: Vec::new(),
            derived_cong: Vec::new(),
            derived_eqangle: Vec::new(),
            derived_cyclic: Vec::new(),
            derived_sameclock: Vec::new(),
            derived_midp: Vec::new(),
            derived_contri1: Vec::new(),
            derived_contri2: Vec::new(),
            derived_simtri1: Vec::new(),
            derived_simtri2: Vec::new(),
            derived_eqratio: Vec::new(),
            derived_aconst: Vec::new(),
        }
    }

    fn add_point(&mut self, x: i64, y: i64, name: String) {
        if self.points.iter().any(|(_, _, n)| n == &name) {
            return;
        }
        self.points.push((x, y, name.clone()));
    }

    fn add_col(&mut self, a: String, b: String, c: String) {
        self.col_facts.push((a, b, c));
    }

    fn add_para(&mut self, a: String, b: String, c: String, d: String) {
        self.para_facts.push((a, b, c, d));
    }

    fn add_perp(&mut self, a: String, b: String, c: String, d: String) {
        self.perp_facts.push((a, b, c, d));
    }

    fn add_cong(&mut self, a: String, b: String, c: String, d: String) {
        self.cong_facts.push((a, b, c, d));
    }

    fn add_eqangle(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.eqangle_facts.push((a, b, c, d, e, f));
    }

    fn add_cyclic(&mut self, a: String, b: String, c: String, d: String) {
        self.cyclic_facts.push((a, b, c, d));
    }

    fn add_sameclock(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.sameclock_facts.push((a, b, c, d, e, f));
    }

    fn add_midp(&mut self, a: String, b: String, c: String) {
        self.midp_facts.push((a, b, c));
    }

    fn add_contri1(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.contri1_facts.push((a, b, c, d, e, f));
    }

    fn add_contri2(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.contri2_facts.push((a, b, c, d, e, f));
    }

    fn add_simtri1(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.simtri1_facts.push((a, b, c, d, e, f));
    }

    fn add_simtri2(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.simtri2_facts.push((a, b, c, d, e, f));
    }

    fn add_eqratio(&mut self, a: String, b: String, c: String, d: String, e: String, f: String, g: String, h: String) {
        self.eqratio_facts.push((a, b, c, d, e, f, g, h));
    }

    fn add_aconst(&mut self, a: String, b: String, c: String, m: i32, n: i32) {
        self.aconst_facts.push((a, b, c, m, n));
    }

    fn run(&mut self) {
        let points = self.points.clone();

        let col_facts = self.col_facts.clone();
        let para_facts = self.para_facts.clone();
        let perp_facts = self.perp_facts.clone();
        let cong_facts = self.cong_facts.clone();
        let eqangle_facts = self.eqangle_facts.clone();
        let cyclic_facts = self.cyclic_facts.clone();
        let sameclock_facts = self.sameclock_facts.clone();
        let midp_facts = self.midp_facts.clone();
        let contri1_facts = self.contri1_facts.clone();
        let contri2_facts = self.contri2_facts.clone();
        let simtri1_facts = self.simtri1_facts.clone();
        let simtri2_facts = self.simtri2_facts.clone();
        let eqratio_facts = self.eqratio_facts.clone();
        let aconst_facts = self.aconst_facts.clone();

        ascent! {
            struct AscentProgram;

            relation point(i64, i64, String);
            relation col(String, String, String);
            relation para(String, String, String, String);
            relation perp(String, String, String, String);
            relation cong(String, String, String, String);
            relation eqangle(String, String, String, String, String, String);
            relation cyclic(String, String, String, String);
            relation sameclock(String, String, String, String, String, String);
            relation eqratio(String, String, String, String, String, String, String, String);
            relation midp(String, String, String);
            relation contri1(String, String, String, String, String, String);
            relation contri2(String, String, String, String, String, String);
            relation simtri1(String, String, String, String, String, String);
            relation simtri2(String, String, String, String, String, String);
            relation aconst(String, String, String, i32, i32);

            // ----------------------------------------------------------------
            // Relation Properties (Symmetries)
            // ----------------------------------------------------------------

            col(c, b, a) <-- col(a, b, c);
            col(a, c, b) <-- col(a, b, c);

            para(c, d, a, b) <-- para(a, b, c, d);
            para(b, a, c, d) <-- para(a, b, c, d);
            para(a, b, d, c) <-- para(a, b, c, d);

            perp(c, d, a, b) <-- perp(a, b, c, d);
            perp(b, a, c, d) <-- perp(a, b, c, d);
            perp(a, b, d, c) <-- perp(a, b, c, d);

            cong(c, d, a, b) <-- cong(a, b, c, d);
            cong(b, a, c, d) <-- cong(a, b, c, d);
            cong(a, b, d, c) <-- cong(a, b, c, d);

            eqangle(d, e, f, a, b, c) <-- eqangle(a, b, c, d, e, f);
            eqangle(c, b, a, f, e, d) <-- eqangle(a, b, c, d, e, f);

            cyclic(b, c, d, a) <-- cyclic(a, b, c, d);
            cyclic(a, c, b, d) <-- cyclic(a, b, c, d);

            sameclock(d, e, f, a, b, c) <-- sameclock(a, b, c, d, e, f);
            sameclock(a, b, c, f, d, e) <-- sameclock(a, b, c, d, e, f);
            sameclock(c, b, a, f, e, d) <-- sameclock(a, b, c, d, e, f);

            eqratio(e, f, g, h, a, b, c, d) <-- eqratio(a, b, c, d, e, f, g, h);
            eqratio(c, d, a, b, g, h, e, f) <-- eqratio(a, b, c, d, e, f, g, h);
            eqratio(a, b, e, f, c, d, g, h) <-- eqratio(a, b, c, d, e, f, g, h);

            // ----------------------------------------------------------------
            // Trivial Statements
            // ----------------------------------------------------------------

            cong(a, b, a, b) <--
                point(_, _, a), point(_, _, b),
                if a != b;

            para(a, b, a, b) <--
                point(_, _, a), point(_, _, b),
                if a != b;

            eqangle(a, b, c, a, b, c) <--
                point(_, _, a), point(_, _, b), point(_, _, c), !col(a, b, c),
                if a != b && a != c && b != c;

            // ----------------------------------------------------------------
            // Deductive Rules
            // ----------------------------------------------------------------

            // AA Similarity
            simtri1(a, b, c, d, e, f) <-- 
                eqangle(b, a, c, e, d, f), 
                eqangle(b, c, a, e, f, d),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*dx, *dy, d.clone()), (*ex, *ey, e.clone()), (*fx, *fy, f.clone())]
                );
            simtri2(a, b, c, d, e, f) <-- 
                eqangle(b, a, c, f, d, e), 
                eqangle(b, c, a, d, f, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*fx, *fy, f.clone()), (*ex, *ey, e.clone()), (*dx, *dy, d.clone())]
                );

            // ASA Congruence
            contri1(a, b, c, d, e, f) <-- eqangle(b, a, c, e, d, f), eqangle(c, b, a, f, e, d), cong(a, b, d, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*dx, *dy, d.clone()), (*ex, *ey, e.clone()), (*fx, *fy, f.clone())]
                );
            contri2(a, b, c, d, e, f) <-- eqangle(b, a, c, f, d, e), eqangle(c, b, a, d, e, f), cong(a, b, d, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*fx, *fy, f.clone()), (*ex, *ey, e.clone()), (*dx, *dy, d.clone())]
                );

            // SAS Congruence
            contri1(a, b, c, d, e, f) <-- eqangle(b, a, c, e, d, f), cong(a, c, d, f), cong(a, b, d, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*dx, *dy, d.clone()), (*ex, *ey, e.clone()), (*fx, *fy, f.clone())]
                );
            contri2(a, b, c, d, e, f) <-- eqangle(b, a, c, f, d, e), cong(a, c, d, f), cong(a, b, d, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*fx, *fy, f.clone()), (*ex, *ey, e.clone()), (*dx, *dy, d.clone())]
                );

            // SSS Congruence
            contri1(a, b, c, d, e, f) <-- cong(a, c, d, f), cong(a, b, d, e), cong(c, b, f, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*dx, *dy, d.clone()), (*ex, *ey, e.clone()), (*fx, *fy, f.clone())]
                );
            contri2(a, b, c, d, e, f) <-- cong(a, c, d, f), cong(a, b, d, e), cong(c, b, f, e),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*fx, *fy, f.clone()), (*ex, *ey, e.clone()), (*dx, *dy, d.clone())]
                );

            // Right SSA
            contri1(a, b, c, d, e, f) <-- perp(a, b, a_prime, c), perp(d, e, d_prime, f), cong(a, b, d, e), cong(b, c, e, f),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*dx, *dy, d.clone()), (*ex, *ey, e.clone()), (*fx, *fy, f.clone())]
                );

            contri2(a, b, c, d, e, f) <-- perp(a, b, a_prime, c), perp(d, e, d_prime, f), cong(a, b, d, e), cong(b, c, e, f),
                point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
                point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
                if same_orientation(
                    vec![(*ax, *ay, a.clone()), (*bx, *by, b.clone()), (*cx, *cy, c.clone())],
                    vec![(*fx, *fy, f.clone()), (*ex, *ey, e.clone()), (*dx, *dy, d.clone())]
                );

            // Inscribed Angle Theorem
            eqangle(a, b, c, c, b, d) <-- cong(o, a, o_prime, b), cong(o, c, o_prime, b), cong(o, c, o_prime, a), perp(o, b, b_prime, d), eqangle(a, o, c, c_prime, o, b),
                if o == o_prime && b == b_prime && c == c_prime &&
                   a != b && a != c && a != d &&
                   b != c && b != d &&
                   c != d;

            // Diameter Right Angle
            perp(b, r, r, d) <-- cyclic(b, r, y, d), cong(b, o, r, o_prime), cong(r, o, d, o_prime), col(b, o, d)
                if o == o_prime &&
                   b != r && b != y && b != d &&
                   r != y && r != d &&
                   y != d;
        }

        let mut prog = AscentProgram::default();

        // Initialize input relations
        prog.point = points;
        prog.col = col_facts;
        prog.para = para_facts;
        prog.perp = perp_facts;
        prog.cong = cong_facts;
        prog.eqangle = eqangle_facts;
        prog.cyclic = cyclic_facts;
        prog.sameclock = sameclock_facts;
        prog.midp = midp_facts;
        prog.contri1 = contri1_facts;
        prog.contri2 = contri2_facts;
        prog.simtri1 = simtri1_facts;
        prog.simtri2 = simtri2_facts;
        prog.eqratio = eqratio_facts;
        prog.aconst = aconst_facts;

        prog.run();

        // Extract derived results
        self.derived_col = prog.col;
        self.derived_para = prog.para;
        self.derived_perp = prog.perp;
        self.derived_cong = prog.cong;
        self.derived_eqangle = prog.eqangle;
        self.derived_cyclic = prog.cyclic;
        self.derived_sameclock = prog.sameclock;
        self.derived_midp = prog.midp;
        self.derived_contri1 = prog.contri1;
        self.derived_contri2 = prog.contri2;
        self.derived_simtri1 = prog.simtri1;
        self.derived_simtri2 = prog.simtri2;
        self.derived_eqratio = prog.eqratio;
        self.derived_aconst = prog.aconst;
    }

    // Output methods
    fn get_points(&self) -> Vec<(i64, i64, String)> {
        self.points.clone()
    }

    fn get_col(&self) -> Vec<(String, String, String)> {
        self.derived_col.clone()
    }

    fn get_para(&self) -> Vec<(String, String, String, String)> {
        self.derived_para.clone()
    }

    fn get_perp(&self) -> Vec<(String, String, String, String)> {
        self.derived_perp.clone()
    }

    fn get_cong(&self) -> Vec<(String, String, String, String)> {
        self.derived_cong.clone()
    }

    fn get_eqangle(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_eqangle.clone()
    }

    fn get_cyclic(&self) -> Vec<(String, String, String, String)> {
        self.derived_cyclic.clone()
    }

    fn get_sameclock(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_sameclock.clone()
    }

    fn get_midp(&self) -> Vec<(String, String, String)> {
        self.derived_midp.clone()
    }

    fn get_contri1(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_contri1.clone()
    }

    fn get_contri2(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_contri2.clone()
    }

    fn get_simtri1(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_simtri1.clone()
    }

    fn get_simtri2(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_simtri2.clone()
    }

    fn get_eqratio(&self) -> Vec<(String, String, String, String, String, String, String, String)> {
        self.derived_eqratio.clone()
    }

    fn get_aconst(&self) -> Vec<(String, String, String, i32, i32)> {
        self.derived_aconst.clone()
    }
}

#[pymodule]
fn ascent_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DeductiveDatabase>()?;
    Ok(())
}
