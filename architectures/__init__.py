"""The four presets. Builders pick one; they cannot define their own. DO NOT EDIT."""
from .sequential import run as sequential
from .debate import run as debate
from .supervisor import run as supervisor
from .manager import run as manager

ARCHITECTURES = {
    "sequential": sequential,
    "debate": debate,
    "supervisor": supervisor,
    "manager": manager,
}
