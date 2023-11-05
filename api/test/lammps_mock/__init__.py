__version__ = 0


def lammps():
    return MockLamps()


class MockLamps:
    """Mock return for lammps.lammps()"""

    def command(*args, **kwargs):
        print(f"Command {args}, {kwargs}")
        pass

    def file(*args, **kwargs):
        print(f"File {args}, {kwargs}")
        pass
