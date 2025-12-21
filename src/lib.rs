use pyo3::prelude::*;
use pyo3::{Bound, types::PyModule};
use ascent::ascent;


#[pyclass]
struct GeometryProgram {
    // Input facts
    points: Vec<(String, f64, f64)>,
    collinear_facts: Vec<(String, String, String)>,
    parallel_facts: Vec<(String, String, String, String)>,
    perpendicular_facts: Vec<(String, String, String, String)>,
    congruent_facts: Vec<(String, String, String, String)>,
    equal_angle_facts: Vec<(String, String, String, String, String, String)>,
    cyclic_facts: Vec<(String, String, String, String)>,
    sameclock_facts: Vec<(String, String, String, String, String, String)>,
    midpoint_facts: Vec<(String, String, String)>,
    contri1_facts: Vec<(String, String, String, String, String, String)>,
    contri2_facts: Vec<(String, String, String, String, String, String)>,
    simtri1_facts: Vec<(String, String, String, String, String, String)>,
    simtri2_facts: Vec<(String, String, String, String, String, String)>,

    // Derived results
    derived_collinear: Vec<(String, String, String)>,
    derived_parallel: Vec<(String, String, String, String)>,
    derived_perpendicular: Vec<(String, String, String, String)>,
    derived_congruent: Vec<(String, String, String, String)>,
    derived_equal_angles: Vec<(String, String, String, String, String, String)>,
    derived_cyclic: Vec<(String, String, String, String)>,
    derived_sameclock: Vec<(String, String, String, String, String, String)>,
    derived_midpoint: Vec<(String, String, String)>,
    derived_contri1: Vec<(String, String, String, String, String, String)>,
    derived_contri2: Vec<(String, String, String, String, String, String)>,
    derived_simtri1: Vec<(String, String, String, String, String, String)>,
    derived_simtri2: Vec<(String, String, String, String, String, String)>,
    derived_equal_ratios: Vec<(String, String, String, String, String, String, String, String)>,
}

#[pymethods]
impl GeometryProgram {
    #[new]
    fn new() -> Self {
        GeometryProgram {
            points: Vec::new(),
            collinear_facts: Vec::new(),
            parallel_facts: Vec::new(),
            perpendicular_facts: Vec::new(),
            congruent_facts: Vec::new(),
            equal_angle_facts: Vec::new(),
            cyclic_facts: Vec::new(),
            sameclock_facts: Vec::new(),
            midpoint_facts: Vec::new(),
            contri1_facts: Vec::new(),
            contri2_facts: Vec::new(),
            simtri1_facts: Vec::new(),
            simtri2_facts: Vec::new(),

            derived_collinear: Vec::new(),
            derived_parallel: Vec::new(),
            derived_perpendicular: Vec::new(),
            derived_congruent: Vec::new(),
            derived_equal_angles: Vec::new(),
            derived_cyclic: Vec::new(),
            derived_sameclock: Vec::new(),
            derived_midpoint: Vec::new(),
            derived_contri1: Vec::new(),
            derived_contri2: Vec::new(),
            derived_simtri1: Vec::new(),
            derived_simtri2: Vec::new(),
            derived_equal_ratios: Vec::new(),
        }
    }

    fn add_point(&mut self, name: String, x: f64, y: f64) {
        if self.points.iter().any(|(n, _, _)| n == &name) {
            return;
        }
        self.points.push((name.clone(), x, y));
    }

    fn add_collinear(&mut self, a: String, b: String, c: String) {
        self.collinear_facts.push((a, b, c));
    }

    fn add_parallel(&mut self, a: String, b: String, c: String, d: String) {
        self.parallel_facts.push((a, b, c, d));
    }

    fn add_perpendicular(&mut self, a: String, b: String, c: String, d: String) {
        self.perpendicular_facts.push((a, b, c, d));
    }

    fn add_congruent(&mut self, a: String, b: String, c: String, d: String) {
        self.congruent_facts.push((a, b, c, d));
    }

    fn add_equal_angle(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.equal_angle_facts.push((a, b, c, d, e, f));
    }

    fn add_cyclic(&mut self, a: String, b: String, c: String, d: String) {
        self.cyclic_facts.push((a, b, c, d));
    }

    fn add_sameclock(&mut self, a: String, b: String, c: String, d: String, e: String, f: String) {
        self.sameclock_facts.push((a, b, c, d, e, f));
    }

    fn add_midpoint(&mut self, a: String, b: String, c: String) {
        self.midpoint_facts.push((a, b, c));
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

    fn run(&mut self) {
        let points: Vec<String> = self.points.iter()
            .map(|(name, _, _)| name.clone())
            .collect();

        let col_facts = self.collinear_facts.clone();
        let para_facts = self.parallel_facts.clone();
        let perp_facts = self.perpendicular_facts.clone();
        let cong_facts = self.congruent_facts.clone();
        let eqangle_facts = self.equal_angle_facts.clone();
        let cyclic_facts = self.cyclic_facts.clone();
        let sameclock_facts = self.sameclock_facts.clone();
        let midp_facts = self.midpoint_facts.clone();
        let contri1_facts = self.contri1_facts.clone();
        let contri2_facts = self.contri2_facts.clone();
        let simtri1_facts = self.simtri1_facts.clone();
        let simtri2_facts = self.simtri2_facts.clone();

        ascent! {
            struct AscentProgram;

            relation point(String);
            relation collinear(String, String, String);
            relation parallel(String, String, String, String);
            relation perpendicular(String, String, String, String);
            relation congruent(String, String, String, String);
            relation equal_angle(String, String, String, String, String, String);
            relation cyclic(String, String, String, String);
            relation sameclock(String, String, String, String, String, String);
            relation eq_ratio(String, String, String, String, String, String, String, String);
            relation midpoint(String, String, String);
            relation contri1(String, String, String, String, String, String);
            relation contri2(String, String, String, String, String, String);
            relation simtri1(String, String, String, String, String, String);
            relation simtri2(String, String, String, String, String, String);

            // ----------------------------------------------------------------
            // Relation Properties (Symmetries)
            // ----------------------------------------------------------------

            collinear(c, b, a) <-- collinear(a, b, c);
            collinear(a, c, b) <-- collinear(a, b, c);

            parallel(c, d, a, b) <-- parallel(a, b, c, d);
            parallel(b, a, c, d) <-- parallel(a, b, c, d);
            parallel(a, b, d, c) <-- parallel(a, b, c, d);

            perpendicular(c, d, a, b) <-- perpendicular(a, b, c, d);
            perpendicular(b, a, c, d) <-- perpendicular(a, b, c, d);
            perpendicular(a, b, d, c) <-- perpendicular(a, b, c, d);

            congruent(c, d, a, b) <-- congruent(a, b, c, d);
            congruent(b, a, c, d) <-- congruent(a, b, c, d);
            congruent(a, b, d, c) <-- congruent(a, b, c, d);

            equal_angle(d, e, f, a, b, c) <-- equal_angle(a, b, c, d, e, f);
            equal_angle(c, b, a, f, e, d) <-- equal_angle(a, b, c, d, e, f);

            cyclic(b, c, d, a) <-- cyclic(a, b, c, d);
            cyclic(a, c, b, d) <-- cyclic(a, b, c, d);

            sameclock(d, e, f, a, b, c) <-- sameclock(a, b, c, d, e, f);
            sameclock(c, b, a, f, e, d) <-- sameclock(a, b, c, d, e, f);

            eq_ratio(e, f, g, h, a, b, c, d) <-- eq_ratio(a, b, c, d, e, f, g, h);
            eq_ratio(c, d, a, b, g, h, e, f) <-- eq_ratio(a, b, c, d, e, f, g, h);
            eq_ratio(a, b, e, f, c, d, g, h) <-- eq_ratio(a, b, c, d, e, f, g, h);

            // ----------------------------------------------------------------
            // Relation Data
            // ----------------------------------------------------------------

            // Col implies parallel
            parallel(a, b, a, c) <-- collinear(a, b, c),
                if a != b && a != c && b != c;

            // Cyclic Quadrilateral Properties
            equal_angle(a, d, b, a, c, b) <-- cyclic(a, b, c, d);
            equal_angle(d, a, c, d, b, c) <-- cyclic(a, b, c, d);

            // Midpoint implies congruence and collinearity
            congruent(a, m, m, b) <-- midpoint(m, a, b);
            collinear(a, m, b) <-- midpoint(m, a, b);

            // Congruent Triangles imply corresponding parts (Contri1)
            congruent(a, b, d, e) <-- contri1(a, b, c, d, e, f);
            congruent(b, c, e, f) <-- contri1(a, b, c, d, e, f);
            congruent(c, a, f, d) <-- contri1(a, b, c, d, e, f);
            equal_angle(a, b, c, d, e, f) <-- contri1(a, b, c, d, e, f);
            equal_angle(b, c, a, e, f, d) <-- contri1(a, b, c, d, e, f);
            equal_angle(c, a, b, f, d, e) <-- contri1(a, b, c, d, e, f);

            // Congruent Triangles imply corresponding parts (Contri2)
            congruent(a, b, d, e) <-- contri2(a, b, c, d, e, f);
            congruent(b, c, e, f) <-- contri2(a, b, c, d, e, f);
            congruent(c, a, f, d) <-- contri2(a, b, c, d, e, f);
            equal_angle(a, b, c, f, e, d) <-- contri2(a, b, c, d, e, f);
            equal_angle(b, c, a, d, f, e) <-- contri2(a, b, c, d, e, f);
            equal_angle(c, a, b, e, d, f) <-- contri2(a, b, c, d, e, f);

            // Similar Triangles imply equal angles and ratios (Simtri1)
            equal_angle(c, a, b, f, d, e) <-- simtri1(a, b, c, d, e, f);
            equal_angle(b, c, a, e, f, d) <-- simtri1(a, b, c, d, e, f);
            equal_angle(a, b, c, d, e, f) <-- simtri1(a, b, c, d, e, f);
            eq_ratio(a, b, d, e, b, c, e, f) <-- simtri1(a, b, c, d, e, f);
            eq_ratio(b, c, e, f, c, a, f, d) <-- simtri1(a, b, c, d, e, f);
            eq_ratio(a, b, d, e, c, a, f, d) <-- simtri1(a, b, c, d, e, f);

            // Similar Triangles imply equal angles and ratios (Simtri2)
            equal_angle(c, a, b, e, d, f) <-- simtri2(a, b, c, d, e, f);
            equal_angle(b, c, a, d, f, e) <-- simtri2(a, b, c, d, e, f);
            equal_angle(a, b, c, f, e, d) <-- simtri2(a, b, c, d, e, f);
            eq_ratio(a, b, d, e, b, c, e, f) <-- simtri2(a, b, c, d, e, f);
            eq_ratio(b, c, e, f, c, a, f, d) <-- simtri2(a, b, c, d, e, f);
            eq_ratio(a, b, d, e, c, a, f, d) <-- simtri2(a, b, c, d, e, f);

            // ----------------------------------------------------------------
            // Deductive Rules
            // ----------------------------------------------------------------

            // Congruent Transitivity
            congruent(a, b, e, f) <-- congruent(a, b, c, d), congruent(c, d, e, f);

            // Parallel Transitivity
            parallel(c, d, e, f) <-- parallel(a, b, c, d), parallel(a, b, e, f);

            // Parallel to Equal Angles
            equal_angle(c, a, b, a, c, d) <-- parallel(a, b, c, d) 
                if a != b && a != c && a != d && b != c && b != d && c != d;

            // Transversal Alternate Interior Angles
            equal_angle(b, a, e, d, c, e) <-- parallel(a, b, c, d), collinear(a, e, c),
                if a != b && a != c && a != d && b != c && b != d && c != d && a != e && c != e;
            equal_angle(e, a, b, e, c, d) <-- parallel(a, b, c, d), collinear(a, e, c),
                if a != b && a != c && a != d && b != c && b != d && c != d && a != e && c != e;

            // Parallelogram Opposite Sides Congruent
            congruent(a, b, c, d) <-- parallel(a, b, c, d), parallel(b, c, d, a),
                if a != b && a != c && a != d && b != c && b != d && c != d;

            // Col to Equal Angles
            equal_angle(a, e, d, a, e, c) <-- collinear(e, a, b), collinear(e, c, d),
                if a != b && a != c && a != d && b != c && b != d && c != d && a != e && b != e && c != e && d != e;
            equal_angle(b, e, d, b, e, c) <-- collinear(e, a, b), collinear(e, c, d),
                if a != b && a != c && a != d && b != c && b != d && c != d && a != e && b != e && c != e && d != e;
            equal_angle(c, e, a, c, e, b) <-- collinear(e, a, b), collinear(e, c, d),
                if a != b && a != c && a != d && b != c && b != d && c != d && a != e && b != e && c != e && d != e;
            equal_angle(d, e, a, d, e, b) <-- collinear(e, a, b), collinear(e, c, d),
                if a != b && a != c && a != d && b != c && b != d && c != d && a != e && b != e && c != e && d != e;

            // Perpendicular + Perpendicular = Parallel
            parallel(a, b, e, f) <-- perpendicular(a, b, c, d), perpendicular(e, f, c, d);

            // Perpendicular + Parallel = Perpendicular
            perpendicular(c, d, e, f) <-- parallel(a, b, c, d), perpendicular(a, b, e, f);

            // Vertical Angles
            equal_angle(a, b, d, c, b, e) <-- collinear(a, b, c), collinear(d, b, e),
                if a != c && a != d && a != e && b != c && b != d && b != e && c != d && c != e && d != e;

            // AA Similarity
            simtri1(a, b, c, d, e, f) <-- equal_angle(b, a, c, e, d, f), equal_angle(b, c, a, e, f, d), sameclock(a, b, c, d, e, f),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;
            simtri2(a, b, c, d, e, f) <-- equal_angle(b, a, c, e, d, f), equal_angle(b, c, a, e, f, d), sameclock(a, b, c, f, e, d),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;

            // ASA Congruence
            contri1(a, b, c, d, e, f) <-- equal_angle(b, a, c, e, d, f), equal_angle(c, b, a, f, e, d), congruent(a, b, d, e), sameclock(a, b, c, d, e, f),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;
            contri2(a, b, c, d, e, f) <-- equal_angle(b, a, c, f, e, d), equal_angle(c, b, a, d, e, f), congruent(a, b, d, e), sameclock(a, b, c, f, e, d),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;

            // SAS Congruence
            contri1(a, b, c, d, e, f) <-- equal_angle(b, a, c, e, d, f), congruent(a, c, d, f), congruent(a, b, d, e), sameclock(a, b, c, d, e, f),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;
            contri2(a, b, c, d, e, f) <-- equal_angle (b, a, c, f, e, d), congruent(a, c, d, f), congruent(a, b, d, e), sameclock(a, b, c, f, e, d),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;

            // SSS Congruence
            contri1(a, b, c, d, e, f) <-- congruent(a, c, d, f), congruent(a, b, d, e), congruent(c, b, f, e), sameclock(a, b, c, d, e, f),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;
            contri2(a, b, c, d, e, f) <-- congruent(a, c, d, f), congruent(a, b, d, e), congruent(c, b, f, e), sameclock(a, b, c, f, e, d),
                if a != b && a != c &&
                   b != c &&
                   d != e && d != f &&
                   e != f;
        }

        let mut prog = AscentProgram::default();

        // Initialize input relations
        prog.point = points.into_iter().map(|x| (x,)).collect();
        prog.collinear = col_facts;
        prog.parallel = para_facts;
        prog.perpendicular = perp_facts;
        prog.congruent = cong_facts;
        prog.equal_angle = eqangle_facts;
        prog.cyclic = cyclic_facts;
        prog.sameclock = sameclock_facts;
        prog.midpoint = midp_facts;
        prog.contri1 = contri1_facts;
        prog.contri2 = contri2_facts;
        prog.simtri1 = simtri1_facts;
        prog.simtri2 = simtri2_facts;

        prog.run();

        // Extract derived results
        self.derived_collinear = prog.collinear;
        self.derived_parallel = prog.parallel;
        self.derived_perpendicular = prog.perpendicular;
        self.derived_congruent = prog.congruent;
        self.derived_equal_angles = prog.equal_angle;
        self.derived_cyclic = prog.cyclic;
        self.derived_sameclock = prog.sameclock;
        self.derived_midpoint = prog.midpoint;
        self.derived_contri1 = prog.contri1;
        self.derived_contri2 = prog.contri2;
        self.derived_simtri1 = prog.simtri1;
        self.derived_simtri2 = prog.simtri2;
        self.derived_equal_ratios = prog.eq_ratio;
    }

    // Output methods
    fn get_points(&self) -> Vec<(String, f64, f64)> {
        self.points.clone()
    }

    fn get_collinear(&self) -> Vec<(String, String, String)> {
        self.derived_collinear.clone()
    }

    fn get_parallel(&self) -> Vec<(String, String, String, String)> {
        self.derived_parallel.clone()
    }

    fn get_perpendicular(&self) -> Vec<(String, String, String, String)> {
        self.derived_perpendicular.clone()
    }

    fn get_congruent(&self) -> Vec<(String, String, String, String)> {
        self.derived_congruent.clone()
    }

    fn get_equal_angles(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_equal_angles.clone()
    }

    fn get_cyclic(&self) -> Vec<(String, String, String, String)> {
        self.derived_cyclic.clone()
    }

    fn get_sameclock(&self) -> Vec<(String, String, String, String, String, String)> {
        self.derived_sameclock.clone()
    }

    fn get_midpoint(&self) -> Vec<(String, String, String)> {
        self.derived_midpoint.clone()
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

    fn get_equal_ratios(&self) -> Vec<(String, String, String, String, String, String, String, String)> {
        self.derived_equal_ratios.clone()
    }
}

#[pymodule]
fn ascent_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GeometryProgram>()?;
    Ok(())
}
