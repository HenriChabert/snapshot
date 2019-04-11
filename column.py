class Column():
    def __init__(self, name, col_type="string", pretty_name=None):
        self.name = name
        self.pretty_name = pretty_name
        self.col_type = col_type