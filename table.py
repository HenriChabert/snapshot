class Table(Element):
    def __init__(self, sd, parameters):
        Element.__init__(self,sd, parameters)
        self.build_content()
        
    def build_content(self):
        self.snapshot_data = self.parameters["root_snapshot_data"].format_sd(self.parameters["format_parameters"])
        
        self.pddf = self.snapshot_data.get_graphable_pddf(pretty_named=True, set_ind=self.parameters["format_parameters"])
        form_dict = self.get_formatters_dict(self.pddf)
        html_pddf = self.pddf.to_html(formatters=form_dict, index=False)
        self.html = html_pddf
        self.timestamp = get_timestamp()
        
    def get_formatters_dict(self, df):
        formatters_dict = {}
        cols = self.snapshot_data.columns
        for col in cols:
            if cols[col].col_type == "int":
                formatters_dict[cols[col].pretty_name] = self.to_num
            elif cols[col].col_type == "perc":
                formatters_dict[cols[col].pretty_name+" (%)"] = self.to_perc
            elif cols[col].col_type == "amount":
                formatters_dict[cols[col].pretty_name+" ({cur})".format(cur=self.snapshot_data.snapshot.parameters["currency"])] = self.to_cur
        return(formatters_dict)
    
    
    def to_cur(self, x):
        return str(self.snapshot_data.snapshot.parameters["currency"])+'{:,.2f}'.format(x)
        
    def to_perc(self, x):
        try:
            return '{0:.1%}'.format(x)
        except:
            return -1
    
    def to_num(self, x):
        try:
            return "{:,.0f}".format(x)
        except:
            return -1