class Graph(Element):
    def __init__(self, sd, parameters):
        Element.__init__(self, sd, parameters)
        adomik_colors = ["#29AAE1", "#7DCBF2", "#599AD3", "#A4DAF5", "#40A3A3", "#D3F1F3", "#F7C32D", "#FCAF47", "#EA433B", ]
        default_parameters = {
            "kind":"line",
            "horizontal":False,
            "linewidth":2.2,
            "colors":adomik_colors,
            "figsize":(16, 8),
            "rotation":70,
            "stacked":False, 
            "alpha":1
        }
        self.graph_parameters = check_parameters(self.parameters, default_parameters)
        self.build_content()
        
    def build_content(self):
        now = time.time()
        plt.figure()
        self.snapshot_data = self.parameters["root_snapshot_data"].format_sd(self.parameters["format_parameters"])
        self.graphable_df = self.snapshot_data.get_graphable_pddf(pretty_named=True)#, set_ind=self.parameters["format_parameters"]
        extra_params = {}
        if self.graph_parameters["kind"] == "line":
            extra_params["marker"] = "o"
        elif self.graph_parameters["kind"] in ["bar", "hbar"]:
            bar_width = 0.2
            nb_cols = len(self.graphable_df.columns)
            total_width = bar_width*nb_cols
            extra_params["width"] = total_width
            
        self.graphable_df.plot(kind=self.graph_parameters["kind"], stacked=self.graph_parameters["stacked"], figsize=self.graph_parameters["figsize"], legend=True, linewidth=self.graph_parameters["linewidth"], color=self.graph_parameters["colors"], alpha=self.graph_parameters["alpha"], **extra_params)
        plt.xticks(rotation=self.graph_parameters["rotation"])
            
        if len(self.graphable_df.index) == 1 and self.graph_parameters["kind"] in ["bar", "hbar"]:
            x_ind = [-(nb_cols-1)*bar_width/2 + i*bar_width for i in range (nb_cols)]
            x_labels = list(self.graphable_df.columns)
            plt.xticks(x_ind, x_labels, rotation=self.graph_parameters["rotation"])
          
        if self.snapshot_data.columns[self.parameters["format_parameters"]["values"].keys()[0]].col_type == "perc":
            formatter = tick.FuncFormatter(self.to_percent)
            if self.graph_parameters["kind"] in ['barh']:
                plt.gca().xaxis.set_major_formatter(formatter)
            else:
                plt.gca().yaxis.set_major_formatter(formatter)
        elif self.snapshot_data.columns[self.parameters["format_parameters"]["values"].keys()[0]].col_type == "amount":
            formatter = tick.FuncFormatter(self.to_cur)
            if self.graph_parameters["kind"] in ['barh']:
                plt.gca().xaxis.set_major_formatter(formatter)
            else:
                plt.gca().yaxis.set_major_formatter(formatter)
        elif self.graph_parameters["kind"] not in ['barh']:
            formatter = tick.FuncFormatter(self.to_num)
            plt.gca().yaxis.set_major_formatter(formatter)
        if "Date" in self.graphable_df.columns:
            plt.xticks(self.graphable_df.index, list(self.graphable_df["Date"]))
        plt.grid(b=True, linestyle=":")
        if self.graph_parameters["kind"] not in ['bar', 'barh']:
            plt.gcf().subplots_adjust(left=0.05)
        #plt.tight_layout()
        bucket_name,key,timestamp = get_figure_path(self.parameters)
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(Body=img_data, ContentType='image/png', Key=key)
        #plt.cla()
        #plt.clf()
        plt.close('all')
        
        self.timestamp = timestamp
            
        
    def get_download_url(self):
        bucket_name = "adomik-maths-preproduction"
        directory_path = "henri/uplift_reports"
        try:
            seller_id = self.parameters["root_snapshot_data"].snapshot.parameters["seller"].seller_id
            ts = self.timestamp
            key = "{}/{}/{}.png".format(directory_path, seller_id, ts)
            s3_url = get_s3_url(bucket_name, key)
            return(s3_url)
        except e:
            print("you have to build the table before retrieving the url")
            return
        
    def to_percent(self, y, position):
        return '{:.2%}'.format(y)

    def to_cur(self, y, position):
        return ((str(self.snapshot_data.snapshot.parameters["currency"])+'{:,.2f}'.format(y)).decode("utf-8"))
        
    def to_num(self, y, position):
        return '{:,.0f}'.format(y)