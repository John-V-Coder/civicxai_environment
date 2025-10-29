"""
AtomSpace Manager
Handles the lifecycle and access to the MeTTa AtomSpace
"""
import logging
from hyperon import MeTTa

# Configure logging
logger = logging.getLogger(__name__)

class AtomSpaceManager:
    """
    Manages a singleton instance of the MeTTa AtomSpace
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AtomSpaceManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.metta = MeTTa()
            self.initialized = True
            logger.info("AtomSpaceManager initialized.")

    def get_atomspace(self):
        """
        Returns the underlying MeTTa AtomSpace
        """
        return self.metta.space()

    def add_atom(self, atom_str: str):
        """
        Adds an atom to the AtomSpace from a string representation
        """
        logger.debug(f"Adding atom: {atom_str}")
        try:
            # MeTTa.run returns a list of lists of atoms, so we flatten it
            result = self.metta.run(atom_str)
            return result
        except Exception as e:
            logger.error(f"Failed to add atom '{atom_str}': {e}")
            return None

# Singleton instance
_atomspace_manager_instance = None

def get_atomspace_manager() -> "AtomSpaceManager":
    """
    Get the singleton instance of the AtomSpaceManager
    """
    global _atomspace_manager_instance
    if _atomspace_manager_instance is None:
        _atomspace_manager_instance = AtomSpaceManager()
    return _atomspace_manager_instance
