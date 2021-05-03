class File:
    def __init__(self, path: str, is_new: bool, is_changed: bool):
        self.path = path
        self.is_new = is_new
        self.is_changed = is_changed
