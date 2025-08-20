use std::collections::HashMap;

fn main() {
    println!("Working test");
    
    let mut pattern_map = HashMap::new();
    pattern_map.insert("DEBUG", 1);
    pattern_map.insert("RSDS", 2);
    pattern_map.insert("NB10", 3);
    pattern_map.insert("PDB", 4);
    
    println!("Pattern map: {:?}", pattern_map);
}
