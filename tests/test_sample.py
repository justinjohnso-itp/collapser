
# "pytest" on command line will find everything starting "test_" in base folder or subdirectories.

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5