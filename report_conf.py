general_parameters = {
    "uplift_report":{
        "content":[
            {
                "snapshot_data_parameters":{
                    "file_name":"floor_rule_metrics.csv",
                    "sup_path":"rtb/auctions",
                    "dimensions":[],
                    "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
                    "pre_agg_filter":'channel in ({channels})',
                    "calculated_values":["uplift_perc", "uplift_cur"],
                    "select":["uplift_cur", "uplift_perc"],
                },
                "elements":[
                    {
                        "format_parameters":{
                            "select":["uplift_cur", "uplift_perc"]
                        },
                        "type":"table",
                        "title":"Summary", #If we change the name, we must change the function as well
                        "attachment_name":"uplift_summary"
                    }
                ]
            },
            {
                "snapshot_data_parameters":{
                    "file_name":"floor_rule_metrics.csv",
                    "sup_path":"rtb/auctions",
                    "dimensions":["date"],
                    "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
                    "pre_agg_filter":'channel in ({channels})',
                    "sort_dim":["date"],
                    "calculated_values":["uplift_perc", "uplift_cur", "rev_wo_adk", "rpm", "bc_rpm", "cpm", "bc_cpm", "fill_rate", "bc_fill_rate"],
                    "select":["date", "revenue", "rev_wo_adk", "uplift_cur", "uplift_perc", "rpm", "bc_rpm", "cpm", "bc_cpm", "fill_rate", "bc_fill_rate"],
                },
                "elements":[
                    {
                        "format_parameters":{
                            "keys":["date"], 
                            "groups":[],
                            "values":{"uplift_cur":"sum"}
                        },
                        "type":"graph",
                        "title":"Adomik PRICE uplift ({cur})",
                        "kind":"area",
                        "alpha":0.3
                    },
                    {
                        "format_parameters":{
                            "keys":["date"], 
                            "groups":[],
                            "values":{"uplift_perc":"avg"},
                        },
                        "type":"graph",
                        "title":"Adomik PRICE uplift (%)",
                        "kind":"area",
                        "alpha":0.3
                    },
                    {
                        "format_parameters":{
                            "keys":["date"], 
                            "groups":[],
                            "values":{"fill_rate":"avg", "bc_fill_rate":"avg"},
                        },
                        "type":"graph",
                        "title":"Coverage (%)",
                        "kind":"line"
                    },
                    {
                        "format_parameters":{
                            "keys":['date'], 
                            "groups":[],
                            "values":{"cpm":"avg", "bc_cpm":"avg"},
                        },
                        "type":"graph",
                        "title":"CPM ({cur})",
                        "kind":"line"
                    },
                    {
                        "format_parameters":{
                            "select":["date", "revenue", "rev_wo_adk", "uplift_cur", "uplift_perc", "rpm", "bc_rpm", "fill_rate", "bc_fill_rate"]
                        },
                        "type":"table",
                        "title":"Detailed data",
                        "attachment_name":"uplift_details"
                    }
                ]
            }
        ],
        "email_conf":{
            "title":"<strong>{seller_name}</strong><br/>Uplift Report - {product_type}",
            "subtitle":"{month} {year}",
            "subject":"Adomik PRICE - {seller_name} - Uplift Report - {product_type} - {month} {year}",
            "sender":"report@adomik.com",
            "cta_link":"https://app.adomik.com/",
            "cta_btn":get_s3_url("adomik-maths-preproduction", "henri/uplift_reports/img/platform_btn.png"),
            "extra_infos":{"product_type":"Product"},
            "client_message":"In <strong>{month}</strong>, Adomik PRICE generated a <strong>{uplift_perc}</strong> uplift on <strong>{product_type}</strong>, which accounts for <strong>{uplift_cur}</strong> of additional revenue.",
            "outline_css":get_s3_file("adomik-maths-preproduction", "henri/uplift_reports/conf_files/mail_style.css", "css") 
        },
        "extra_parameters":{
            "product_type":"display"
        },
        "function":build_uplift_report
    },
    "wallapop_uplift_report":{
        "content":[
            {
                "snapshot_data_parameters":{
                    "file_name":"floor_rule_metrics.csv",
                    "sup_path":"rtb/auctions",
                    "dimensions":[],
                    "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
                    "pre_agg_filter":'channel in ({channels})',
                    "calculated_values":["uplift_perc", "uplift_cur"],
                    "select":["uplift_cur", "uplift_perc"],
                    "product":["display"]
                },
                "elements":[
                    {
                        "format_parameters":{
                            "select":["uplift_cur", "uplift_perc"]
                        },
                        "type":"table",
                        "title":"Summary - Display" #If we change the name, we must change the function as well
                    }
                ]
            },
            {
                "snapshot_data_parameters":{
                    "file_name":"floor_rule_metrics.csv",
                    "sup_path":"rtb/auctions",
                    "dimensions":[],
                    "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
                    "pre_agg_filter":'channel in ({channels})',
                    "calculated_values":["uplift_perc", "uplift_cur"],
                    "select":["uplift_cur", "uplift_perc"],
                    "product":["inapp"]
                },
                "elements":[
                    {
                        "format_parameters":{
                            "select":["uplift_cur", "uplift_perc"]
                        },
                        "type":"table",
                        "title":"Summary - Inapp" #If we change the name, we must change the function as well
                    }
                ]
            },
            {
                "snapshot_data_parameters":{
                    "file_name":"floor_rule_metrics.csv",
                    "sup_path":"rtb/auctions",
                    "dimensions":["date"],
                    "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
                    "pre_agg_filter":'channel in ({channels})',
                    "sort_dim":["date"],
                    "calculated_values":["uplift_perc", "uplift_cur", "rev_wo_adk", "rpm", "bc_rpm", "cpm", "bc_cpm", "fill_rate", "bc_fill_rate"],
                    "select":["date", "revenue", "rev_wo_adk", "uplift_cur", "uplift_perc", "rpm", "bc_rpm", "cpm", "bc_cpm", "fill_rate", "bc_fill_rate"],
                    "product":["display", "inapp"]
                },
                "elements":[
                    {
                        "format_parameters":{
                            "keys":["date"], 
                            "groups":[],
                            "values":{"uplift_cur":"sum"}
                        },
                        "type":"graph",
                        "title":"Adomik PRICE uplift ({cur}) - Display & Inapp",
                        "kind":"area",
                        "alpha":0.3
                    },
                    {
                        "format_parameters":{
                            "keys":["date"], 
                            "groups":[],
                            "values":{"uplift_perc":"avg"},
                        },
                        "type":"graph",
                        "title":"Adomik PRICE uplift (%) - Display & Inapp",
                        "kind":"area",
                        "alpha":0.3
                    },
                    {
                        "format_parameters":{
                            "keys":["date"], 
                            "groups":[],
                            "values":{"fill_rate":"avg", "bc_fill_rate":"avg"},
                        },
                        "type":"graph",
                        "title":"Coverage (%) - Display & Inapp",
                        "kind":"line"
                    },
                    {
                        "format_parameters":{
                            "keys":['date'], 
                            "groups":[],
                            "values":{"cpm":"avg", "bc_cpm":"avg"},
                        },
                        "type":"graph",
                        "title":"CPM ({cur}) - Display & Inapp",
                        "kind":"line"
                    }
                ]
            },
            {
                "snapshot_data_parameters":{
                    "file_name":"floor_rule_metrics.csv",
                    "sup_path":"rtb/auctions",
                    "dimensions":["date"],
                    "metrics":{"ad_requests":"sum", "imps":"sum", "revenue":"sum"},
                    "pre_agg_filter":'channel in ({channels})',
                    "sort_dim":["date"],
                    "calculated_values":["uplift_perc", "uplift_cur", "rev_wo_adk", "rpm", "bc_rpm", "cpm", "bc_cpm", "fill_rate", "bc_fill_rate"],
                    "select":["date", "revenue", "rev_wo_adk", "uplift_cur", "uplift_perc", "rpm", "bc_rpm", "cpm", "bc_cpm", "fill_rate", "bc_fill_rate"],
                    "product":["display", "inapp"]
                },
                "elements":[
                    {
                        "format_parameters":{
                            "select":["date", "revenue", "rev_wo_adk", "uplift_cur", "uplift_perc", "rpm", "bc_rpm", "fill_rate", "bc_fill_rate"]
                        },
                        "type":"table",
                        "title":"Detailed data - Display & Inapp"
                    }
                ]
            }
        ],
        "email_conf":{
            "title":"<strong>{seller_name}</strong><br/>Uplift Report - Display & Inapp",
            "subtitle":"{month} {year}",
            "subject":"Adomik PRICE - {seller_name} - Uplift Report - Display & Inapp - {month} {year}",
            "sender":"report@adomik.com",
            "cta_link":"https://app.adomik.com/",
            "cta_btn":get_s3_url("adomik-maths-preproduction", "henri/uplift_reports/img/platform_btn.png"),
            "client_message":"""
                In <strong>{month}</strong>, Adomik PRICE generated a <strong>{uplift_perc_display}</strong> uplift on <strong>Display</strong>, which accounts for <strong>{uplift_cur_display}</strong> of additional revenue 
                and <strong>{uplift_perc_inapp}</strong> uplift on <strong>Inapp</strong>, which accounts for <strong>{uplift_cur_inapp}</strong> of additional revenue.<br>
            """,
            "outline_css":get_s3_file("adomik-maths-preproduction", "henri/uplift_reports/conf_files/mail_style.css", "css") 
        },
        "function":build_uplift_report_wallapop
    }
}