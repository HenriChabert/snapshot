def main(seller, start_date, end_date, snapshot_type, gp, email_extra_conf={}, **kwargs):
    now = time.time()
    print("""
        /////////////////////////////////////////////////////////////////////////////////\n
        Start of the {snapshot_type} generation for the seller {seller_name}.\n
        The report will be sent to {recipients}.
        /////////////////////////////////////////////////////////////////////////////////
    """.format(snapshot_type=snapshot_type, seller_name=seller.seller_name if not seller.seller_name is None else str(seller.seller_id), recipients=", ".join(email_extra_conf["recipients"])))
    root_parameters = {
        "start_date":strToDateTime(start_date),
        "end_date":strToDateTime(end_date),
        "seller":seller
    }
    try:
        snapshot_parameters = cp.deepcopy(gp[snapshot_type])
    except:
        print("You have selected a wrong snapshot type. Available types are : "+", ".join(gp.keys()))
        
    new_snapshot = Snapshot(root_parameters)
    email_conf = cp.deepcopy(snapshot_parameters["email_conf"])
    email_conf.update(email_extra_conf)
    new_snapshot.build_email(email_conf)
    
    if "extra_parameters" in snapshot_parameters:
        checked_parameters = check_parameters(kwargs, snapshot_parameters["extra_parameters"])
        new_snapshot.parameters["extra_parameters"] = checked_parameters
    else:
        checked_parameters = kwargs
    
    snapshot_parameters["function"](new_snapshot, snapshot_parameters, checked_parameters)
    
    if len(new_snapshot.elements) > 0:
        new_snapshot.send()
    else:
        print("The Snapshot does not contain any data, no email sent.")
    
    print("""
        /////////////////////////////////////////////////////////////////////////////////\n
        The {snapshot_type} has been sent.\n
        Execution time : {exec_time}s.
        /////////////////////////////////////////////////////////////////////////////////
    """.format(snapshot_type=snapshot_type, exec_time=str(time.time()-now))) 
    
    return(new_snapshot)

clients_list_json = get_s3_file("adomik-maths-preproduction", "henri/uplift_reports/conf_files/tam_repartition_v2.json", "json") 
seller_list = [Seller(**conf) for conf in clients_list_json]

serv = start_gmail_server()
start_time = time.time()
clients_sd = []
print("Program started")
#for tam in client_list:
wallapop_id = "130868815"
new_sellers = get_seller_from_seller_list(seller_list, "tam", "arnaud")
for new_seller in new_sellers:
    if new_seller.send_mail:
        email_personal_conf = {
            "recipients":new_seller.email,
            #"recipients":["henri@adomik.com"],
            "attach_files":new_seller.attach_file,
            "smtp_server":serv,
            "reply_to":new_seller.tam+"@adomik.com"
        }
        if new_seller.seller_id == wallapop_id:
            clients_sd.append(main(new_seller, "2019-03-01", "2019-03-31", "wallapop_uplift_report", general_parameters, email_extra_conf=email_personal_conf))
        else:
            clients_sd.append(main(new_seller, "2019-03-01", "2019-03-31", "uplift_report", general_parameters, email_extra_conf=email_personal_conf))


print("Program ended in : {}s".format(str(time.time()-start_time)))
serv.quit()