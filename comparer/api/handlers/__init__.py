from .imports import ImportsView
from .nodes import NodesView
from .delete import DeleteView

HANDLERS = (
    ImportsView,
    NodesView,
    DeleteView,
)
