class UninitializedDcelError(RuntimeError):
    """
    Raised when an uninitialized DCEL topological reference is accessed before wiring.
    """
    pass
