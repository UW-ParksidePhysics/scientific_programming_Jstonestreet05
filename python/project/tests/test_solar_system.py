from project.solar_system import load_all_bodies, load_body_with_facts

def test_load_all_bodies():
    bodies = load_all_bodies()
    assert isinstance(bodies, dict)
    assert "mars" in bodies

def test_load_body_with_facts():
    combined = load_body_with_facts("mars")
    assert "meta" in combined
    assert "facts_html" in combined
