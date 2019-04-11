class Element():
    def __init__(self, snapd, parameters):
        default_parameters = {
            "type":"mandatory",
            "root_snapshot_data":snapd,
            "format_parameters":"mandatory",
            "title":None,
            "sub_title":None,
            "description":None,
            "attachment_name":None
        }
        self.parameters = check_parameters(parameters, default_parameters)