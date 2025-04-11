from .kabinet import Kabinet
try:
    from .arkitekt import KabinetService
except ImportError:
    pass
try:
    from .rekuest import structure_reg
except ImportError:
    pass


__all__ = ["Kabinet", "structure_reg", "KabinetService"]
