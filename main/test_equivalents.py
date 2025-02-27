from equivalents import CalculatorModel

model = CalculatorModel()

def test_to_mols():
    """Verifies if the output is correct."""
    # solids
    assert round(model.to_mols('tetracycline', 1.75), 5) == 0.00394
    # liquids
    assert round(model.to_mols('triethylamine', 5.2), 5) == 0.03751
    # solution %
    assert round(model.to_mols('ammonia solution', 0.8), 5) ==  0.01069
    # solution mol/L
    assert model.to_mols('2M HCl', 15) == 0.03
    
def test_from_mols():
    """Verifies if the output is correct."""
    # solids
    assert model.from_mols('L-lysine hydrochloride', 0.002) == 0.3653
    # liquids
    assert round(model.from_mols('pyridine', 0.0015), 5) == 0.12107
    # solution %
    assert round(model.from_mols('formalin', 0.003), 5) ==  0.24108
    # solution mol/L
    assert model.from_mols('1M H2SO4', 0.0035) == 3.5