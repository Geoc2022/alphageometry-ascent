use pyo3::prelude::*;
use ascent::ascent;

// Define a generic Ascent program wrapper
#[pyclass]
struct AscentProgram {
    relations: std::collections::HashMap<String, Vec<Vec<i64>>>,
}

#[pymethods]
impl AscentProgram {
    #[new]
    fn new() -> Self {
        AscentProgram {
            relations: std::collections::HashMap::new(),
        }
    }
    
    fn add_relation(&mut self, name: String) {
        self.relations.insert(name, Vec::new());
    }
    
    fn add_fact(&mut self, relation: String, fact: Vec<i64>) {
        if let Some(rel) = self.relations.get_mut(&relation) {
            rel.push(fact);
        }
    }
    
    fn get_relation(&self, name: String) -> PyResult<Vec<Vec<i64>>> {
        Ok(self.relations.get(&name).cloned().unwrap_or_default())
    }
}

// Example: Specific graph program
#[pyclass]
struct GraphProgram {
    edges: Vec<(i32, i32)>,
    paths: Vec<(i32, i32)>,
}

#[pymethods]
impl GraphProgram {
    #[new]
    fn new() -> Self {
        GraphProgram {
            edges: Vec::new(),
            paths: Vec::new(),
        }
    }
    
    fn add_edge(&mut self, from: i32, to: i32) {
        self.edges.push((from, to));
    }
    
    fn run(&mut self) {
        // Define Ascent program
        ascent! {
            relation edge(i32, i32);
            relation path(i32, i32);
            
            path(x, y) <-- edge(x, y);
            path(x, z) <-- edge(x, y), path(y, z);
        }
        
        let mut prog = AscentProgram::default();
        prog.edge = self.edges.clone();
        prog.run();
        self.paths = prog.path;
    }
    
    fn get_paths(&self) -> Vec<(i32, i32)> {
        self.paths.clone()
    }
    
    fn get_edges(&self) -> Vec<(i32, i32)> {
        self.edges.clone()
    }
}

#[pymodule]
fn ascent_py(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<AscentProgram>()?;
    m.add_class::<GraphProgram>()?;
    Ok(())
}
