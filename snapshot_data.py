class Snapshot_data():
    def __init__(self, snapshot, parameters):
        self.snapshot = snapshot
        default_parameters = {
            "file_name":None,
            "sup_path":"*",
            "dimensions":None,
            "metrics":None,
            "sort_dim":None,
            "pre_agg_filter":None,
            "post_agg_filter":None,
            "compared_value":None,
            "aggregate_comp":None,
            "calculated_values":None,
            "select":None,
            "product":["display"],
            "renamer":cp.deepcopy(self.snapshot.parameters["renamer"]),
            "recalculate_revenue":True,
            "dataframe":None
        }
        self.parameters = check_parameters(parameters, default_parameters)
        if self.parameters["dataframe"] is None:
            self.dataframe = self.build_dataframe()
        else:
            self.dataframe = self.parameters["dataframe"]
        if not self.dataframe is None:
            self.init_columns()
            self.init_format()
        
    def rename_columns(self, df):
        rd = self.parameters["renamer"]
        col_mapping = {rd[n]["pretty_name"]:{"name":n, "type":rd[n]["type"]} for n in rd}
        for col in col_mapping:
            compared_col = col if col_mapping[col]["type"] != "amount" else col+" ({cur})".format(cur=self.snapshot.parameters["currency"])#.decode("utf-8")
            if compared_col in df.columns:
                df = df.withColumn(col_mapping[col]["name"], col_cast(compared_col, col_mapping[col]["type"]))
                df = df.drop(c(compared_col))
        return(df)
        
    def init_columns(self):
        self.columns = {}
        rd = self.parameters["renamer"]
        for col in self.dataframe.columns:
            if col in rd:
                self.add_column(col, pretty_name=rd[col]["pretty_name"], col_type=rd[col]["type"])
            elif col.split("(")[-1].split(")")[0] in rd:
                agg_col = col.split("(")[-1].split(")")[0]
                self.add_column(agg_col, pretty_name="Total "+rd[agg_col]["pretty_name"], col_type=rd[agg_col]["type"])
                self.rename_column(col, agg_col)
            else:
                self.add_column(col, pretty_name=col, col_type="string")
                
        
    def build_dataframe(self):
        formated_df = self.get_gdx_log()
        if formated_df is None:
            return(None)
        self.snapshot.parameters["currency"] = self.guess_currency(formated_df)
        formated_df = self.rename_columns(formated_df)
        if "estimated_revenue" in formated_df.columns and "ad_e_cpm" in formated_df.columns and "imps" in formated_df.columns and self.parameters["recalculate_revenue"]:
            formated_df = formated_df.withColumn("revenue", c("ad_e_cpm")*c("imps")/1000).drop("estimated_revenue")
        #formated_df = formated_df.withColumn("revenue", c("estimated_revenue")).drop("estimated_revenue")
            
        if not self.parameters["pre_agg_filter"] is None:
            formated_df = formated_df.filter(self.parameters["pre_agg_filter"])
        
        self.pure_df = formated_df
        
        if not self.parameters["dimensions"] is None and not self.parameters["metrics"] is None:
            formated_df = formated_df.groupBy(self.parameters["dimensions"]).agg(self.parameters["metrics"])
            formated_df = self.rename_metrics(formated_df, self.parameters["metrics"])
            
        self.agg_df = formated_df
            
        if not self.parameters["post_agg_filter"] is None:
            formated_df = formated_df.filter(self.parameters["post_agg_filter"])
        
        if not self.parameters["compared_value"] is None:
            keys = self.parameters["compared_value"].keys()
            for i in range (len(keys)):
                new_dim = cp.deepcopy(self.parameters["dimensions"])
                if self.parameters["compared_value"][keys[i]]["type"] == "is_any_of":
                    filtered_df = formated_df.filter(c(keys[i]).isin(self.parameters["compared_value"][keys[i]]["param"]))
                elif self.parameters["compared_value"][keys[i]]["type"] == "contains":
                    filtered_df = formated_df.filter(c(keys[i]).like("%"+str(self.parameters["compared_value"][keys[i]]["param"])+"%"))
                    
                if keys[i] in self.parameters["dimensions"]:
                    new_dim.remove(keys[i])
                
                if not self.parameters["aggregate_comp"] is None:
                    filtered_df = filtered_df.groupBy(new_dim).agg(self.parameters["metrics"]).withColumn(keys[i], lit(self.parameters["aggregate_comp"]))
                    
                aggregated_df = formated_df.groupBy(new_dim).agg(self.parameters["metrics"]).withColumn(keys[i], lit("ALL"))
                formated_df = filtered_df.select(sorted(filtered_df.columns)).union(aggregated_df.select(sorted(aggregated_df.columns)))
        
        formated_df = self.rename_metrics(formated_df, self.parameters["metrics"])
        self.gross_df = formated_df
        return(formated_df)
        
    def init_format(self):
        if not self.parameters["calculated_values"] is None:
            self.add_calculated_metric(self.parameters["calculated_values"])
        if not  self.parameters["select"] is None:
            self.select(self.parameters["select"])
        if not  self.parameters["sort_dim"] is None:
            self.sort(self.parameters["sort_dim"])
    
    def guess_currency(self, df):
        cols = df.columns
        rd = self.parameters["renamer"]
        col_mapping = {rd[n]["pretty_name"]:{"name":n, "type":rd[n]["type"]} for n in rd}
        for c in cols:
            splited_name = c.split(" (")
            if splited_name[0] in col_mapping:
                if col_mapping[splited_name[0]]["type"] == "amount":
                    return(splited_name[1].split(")")[0])
        return("$")
        
    def get_gdx_log(self):
        path_root = "s3a://"
        bucket = "adomik-production-logs-gdx"
        list_of_dates = build_dates_list(self.snapshot.parameters["start_date"], self.snapshot.parameters["end_date"])
        path = path_root+bucket+"/"+"{0}/%*%/{1}/{2}".format(self.snapshot.parameters["seller"].seller_id, self.parameters["sup_path"], self.parameters["file_name"])
        list_of_dir = build_dir_list(path, dateTimeToList(list_of_dates))
        if len(list_of_dir) > 0:
            new_df =  sqlContext.read.format('csv')\
            .option("sep","\t")\
            .option("header",True)\
            .load(list_of_dir, sep="\t", header=True)\
            .withColumn('Date', date_from_filename_udf(input_file_name()))
        else:
            print("No data available, the report cannot be generated.")
            return None
    
        if self.parameters["file_name"] == "*":
            new_df = new_df.withColumn('file_name', fn_from_filename_udf(input_file_name()))
        if self.snapshot.parameters["seller"].seller_id == "*":
            new_df = new_df.withColumn('seller_id', seller_id_from_filename_udf(input_file_name()))
        return(new_df)
    
    def build_bc_data(self):
        bc_dim = cp.deepcopy(self.parameters["dimensions"])
        if "channel" in bc_dim:
            bc_dim.drop("channel")
        
        pc_list = []
        if "display" in self.parameters["product"]:
            pc_list.append("ad")
        if "inapp" in self.parameters["product"]:
            pc_list.append("ada")
        if "game" in self.parameters["product"]:
            pc_list.append("adg")
        if "AMP" in self.parameters["product"]:
            pc_list.append("ad_amp_group=ad")
            
        filter_str = " or ".join(['channel = "{}_bc"'.format(p) for p in pc_list])
        
        bc_perf_parameters = {
            "file_name":"floor_rule_metrics.csv",
            "sup_path":"rtb/auctions",
            "dimensions":bc_dim,
            "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
            "pre_agg_filter":filter_str
        }
        
        bc_perf = self.snapshot.build_snapshot_data(bc_perf_parameters).dataframe\
        .withColumnRenamed("revenue", "revenue_bc")\
        .withColumnRenamed("imps", "imps_bc")\
        .withColumnRenamed("ad_requests", "ad_requests_bc")
        
        self.bc_sd = bc_perf
        
        
        return(bc_perf)
        
    def add_calculated_metric(self, metrics):
        join_dim = cp.deepcopy(self.parameters["dimensions"])
        bc_perf = self.build_bc_data()
        if "channel" in join_dim:
            join_dim.remove("channel")
            bc_perf = bc_perf.drop("channel")
        
        if len(join_dim) > 0:
            formated_df = self.dataframe.join(bc_perf, join_dim, 'inner')
        else:
            formated_df = self.dataframe.crossJoin(bc_perf)
        if "uplift_perc" in metrics:
            formated_df = formated_df.withColumn("uplift_perc", ((c("revenue")*c("ad_requests_bc"))/(c("revenue_bc")*c("ad_requests")))-1)
            self.add_column("uplift_perc", pretty_name="Uplift", col_type="perc")
        if "uplift_cur" in metrics:
            formated_df = formated_df.withColumn("uplift_cur", c("revenue")-c("ad_requests")*(c("revenue_bc")/c("ad_requests_bc")))
            self.add_column("uplift_cur", pretty_name="Uplift", col_type="amount")
        if "rev_wo_adk" in metrics:
            formated_df = formated_df.withColumn("rev_wo_adk", c("ad_requests")*c("revenue_bc")/c("ad_requests_bc"))
            self.add_column("rev_wo_adk", pretty_name="Revenue w/o Adomik", col_type="amount")
        if "rpm" in metrics:
            formated_df = formated_df.withColumn("rpm", 1000*c("revenue")/c("ad_requests"))
            self.add_column("rpm", pretty_name="RPM", col_type="amount")
        if "bc_rpm" in metrics:
            formated_df = formated_df.withColumn("bc_rpm", 1000*c("revenue_bc")/c("ad_requests_bc"))
            self.add_column("bc_rpm", pretty_name="RPM w/o Adomik", col_type="amount")
        if "cpm" in metrics:
            formated_df = formated_df.withColumn("cpm", 1000*c("revenue")/c("imps"))
            self.add_column("cpm", pretty_name="CPM", col_type="amount")
        if "bc_cpm" in metrics:
            formated_df = formated_df.withColumn("bc_cpm", 1000*c("revenue_bc")/c("imps_bc"))
            self.add_column("bc_cpm", pretty_name="CPM w/o Adomik", col_type="amount")
        if "fill_rate" in metrics:
            formated_df = formated_df.withColumn("fill_rate", c("imps")/c("ad_requests"))
            self.add_column("fill_rate", pretty_name="Fill Rate", col_type="perc")
        if "bc_fill_rate" in metrics:
            formated_df = formated_df.withColumn("bc_fill_rate", c("imps_bc")/c("ad_requests_bc"))
            self.add_column("bc_fill_rate", pretty_name="Fill Rate w/o Adomik", col_type="perc")
        self.dataframe = formated_df.select(self.parameters["dimensions"]+self.parameters["metrics"].keys()+metrics)
    
    def add_column(self, col_name, pretty_name=None, col_type="string"):
        new_col = Column(col_name, pretty_name=pretty_name, col_type=col_type)
        self.columns[col_name] = new_col
        self.parameters["renamer"][col_name] = {"pretty_name":pretty_name, "type":col_type}
        
    def format_sd(self, format_parameters, inplace=False):
        new_df = self.dataframe
        if not format_parameters is None:
            if is_l1_in_l2(format_parameters.keys(), ["keys", "groups", "values"]):
                new_df = new_df.groupBy(*format_parameters["keys"])
                if len(format_parameters["groups"]) > 0:
                    new_df = new_df.pivot(*format_parameters["groups"])
                new_df = new_df.agg(format_parameters["values"])
                new_df = self.rename_metrics(new_df, format_parameters["values"])
            if "select" in format_parameters:
                new_df = new_df.select(format_parameters["select"])
            
        if not inplace:
            new_sd_para = {
                "renamer":cp.deepcopy(self.parameters["renamer"]),
                "dataframe":new_df
            }
            new_sd = self.snapshot.build_snapshot_data(new_sd_para)
            return(new_sd)
        else:
            self.dataframe = new_df
        
    def get_graphable_pddf(self, set_ind=None, pretty_named=False):
        new_df = self.dataframe
        new_ind = []
        if pretty_named:
            for col in self.columns:
                new_col_name = ""
                try:
                    if len(set_ind["keys"]) > 0:
                        new_col_name += "Total "
                except:
                    pass
                
                if self.columns[col].col_type == "amount":
                    new_col_name += self.columns[col].pretty_name + " ({cur})".format(cur=self.snapshot.parameters["currency"])
                elif self.columns[col].col_type == "perc":
                    new_col_name += self.columns[col].pretty_name + " (%)"
                else:
                    new_col_name += self.columns[col].pretty_name
                    
                new_df = new_df.withColumnRenamed(col, new_col_name)
                try:
                    if col in set_ind["keys"]:
                        new_ind.append(new_col_name)
                except:
                    pass
        
        new_df = new_df.toPandas()
        try:
            if len(set_ind["keys"]) > 0:
                new_df.set_index(new_ind, inplace=True)
        except:
            pass
        return(new_df)
    
    def rename_metrics(self, df, metrics, pretty=False):
        if not metrics is None:
            for m in metrics:
                if not pretty:
                    df = df.withColumnRenamed(metrics[m]+"("+m+")", m)
                else:
                    df = df.withColumnRenamed(metrics[m]+"("+m+")", metrics[m] + " of "+self.columns[m].pretty_name)
        return(df)
        
    def create_element(self, el_params):
        if el_params["type"] == "graph":
            new_el = Graph(self, el_params)
        elif el_params["type"] == "table":
            new_el = Table(self, el_params)
        return(new_el)
        
    def show(self):
        z.show(self.dataframe)
        
    def rename_column(self, name_from, name_to):
        self.dataframe = self.dataframe.withColumnRenamed(name_from, name_to)
        
    def limit(self, number):
        self.dataframe = self.dataframe.limit(number)
        
    def sort(self, col, asc=True):
        self.dataframe = self.dataframe.sort(col, ascending=asc)
        
    def select(self, list_to_select):
        self.dataframe = self.dataframe.select(list_to_select)