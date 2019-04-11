class Snapshot():
    def __init__(self, parameters):
        default_parameters = {
            "start_date":datetime.datetime.today() - datetime.timedelta(1),
            "end_date":datetime.datetime.today(),
            "seller":"mandatory",
            "renamer":cp.deepcopy(renamer_dict)
        }
        
        self.parameters = check_parameters(parameters, default_parameters)
        self.elements = []
        
    def build_snapshot_data(self, sd_params):
        return(Snapshot_data(self, sd_params))
    
    def add_element(self, el):
        if isinstance(el, list):
            self.elements += el
        else:
            self.elements.append(el)
    
    def build_email(self, email_params):
        new_email = Email(self, parameters=email_params) 
        self.email = new_email
        
    def send(self):
        self.email.send_email()