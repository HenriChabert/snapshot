def get_files_s3(path, only_name=False):
    client = boto3.client('s3')
    path_list = path.split("/")
    bucket = path_list[0]
    prefix = "/".join(path_list[1:])
    objects = client.list_objects_v2(Bucket=bucket, Prefix=prefix)["Contents"]
    objects = filter(lambda a : a["Key"].split("/")[-1] != "_SUCCESS", objects)
    if only_name:
        object_names = [x["Key"].split("/")[-1] for x in objects]
        return(object_names)
    return(objects)
    
def get_s3_file(bucket, key, file_format, **kwargs):
    s3 = boto3.resource('s3')

    content_object = s3.Object(bucket, key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    if file_format == "json":
        file_content = json.loads(file_content)
    return(file_content)

def existing_path(path):
    client = boto3.client('s3')
    path_list = path.split("/")
    bucket = path_list[2]
    key = "/".join(path_list[3:])
    try:
        c = client.get_object(Bucket=bucket, Key=key)
        return(True)
    except:
        print("Missing data : {}".format(path))
        return(False)
    
def show_col(path):
    root_path = "s3a://"
    form = path.split(".")[-1]
    df = sqlContext.read.format(form).load(root_path+path, sep="\t", header=True)
    return(df.columns)
    
def seller_id_from_filename(file_path):
    file_path_sep = file_path.split("/")
    return(file_path_sep[3])
    
def date_from_filename(file_path):
    file_path_sep = file_path.split("/")
    return(file_path_sep[4])
    
def fn_from_filename(file_path):
    file_path_sep = file_path.split("/")
    return(file_path_sep[8])
    
seller_id_from_filename_udf = udf(seller_id_from_filename, StringType())
date_from_filename_udf = udf(date_from_filename, StringType())
fn_from_filename_udf = udf(fn_from_filename, StringType())

def hour_from_filename(string):
	return string.split('/')[10]

def listToTuple(liste): #Transforms a list to a usable tuple in a vertica query
    return('(\''+str(liste[0])+'\')' if len(liste) == 1 else str(tuple(liste)))

def listToTupleOfInt(liste): #Transforms a list to a usable tuple of int in a vertica query
    return('('+str(liste[0])+')' if len(liste) == 1 else str(tuple(liste)))

def listToDateTime(liste): #Transforms a list of String into a list of DateTime
    return(list(map(lambda x : datetime.datetime.strptime(x, '%Y-%m-%d'), liste)))

def dateTimeToList(liste): #Transforms a list of DateTime into a list of String
    return(list(map(lambda x : x.strftime('%Y-%m-%d'), liste)))

def strToDateTime(string): #Transforms a String to DateTime
    return(datetime.datetime.strptime(string, '%Y-%m-%d'))

def dateTimeToStr(string): #Transforms a DateTime to String
    return(string.strftime('%Y-%m-%d'))
    
def is_l1_in_l2(l2, l1):
    for el in l1:
        if not el in l2:
            return (False)
    return(True)
    
def get_timestamp():
    result = str(datetime.datetime.now().strftime("%H-%M-%S-%f"))
    return result
    
def col_cast(col_name, type_to, name_to=None):
    real_type = type_to
    if type_to == "amount" or type_to == "perc":
        real_type = "float"

    if name_to is None:
        name_to = col_name
    return(c(col_name).cast(real_type).alias(name_to))
    
def contains_list(el, l):
    for e in l:
        if e in el:
            return True
    return False

def build_dates_list(sdate, edate):
    dates_list = []
    delta = edate - sdate
    for i in range(delta.days + 1):
        dates_list.append(sdate + datetime.timedelta(i))
    return(dates_list)
    
def build_dir_list(path, list_of_str):
    """Create a list by replacing the character %*%"""
    split_path = path.split("%*%")
    dir_list = []
    for e in list_of_str:
        comp_path = split_path[0]+e+split_path[1]
        if existing_path(comp_path):
            dir_list.append(comp_path)
    return(dir_list)
    
def get_figure_path(parameters):
    bucket_name = "adomik-maths-preproduction"
    directory_path = "henri/uplift_reports"
    timestamp = get_timestamp()
    key = directory_path+"/"+parameters["root_snapshot_data"].snapshot.parameters["seller"].seller_id+"/"+timestamp+".png"
    return([bucket_name, key, timestamp])
    
def check_parameters(parameters, default_values):
    new_params = parameters
    for param in default_values:
        if default_values[param] == "mandatory" and not param in parameters:
            print("You have not defined the parameter : "+str(param)+". Please add it to the parameters then create the object again.")
            return None
        else:
            if not param in parameters:
                new_params[param] = default_values[param]
    return(new_params)
    
def get_s3_url(bucket, key, timeout=100000000):
    s3 = boto3.client('s3')
    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=timeout)
    return(url)
    
def export_excel(df): #Export a DataFrame into xlsx
    with io.BytesIO() as buffer:
        writer = pd.ExcelWriter(buffer)
        df.to_excel(writer)
        writer.save()
        return buffer.getvalue()
        
def get_filter_str_from_dict(filter_dict):
    temp_list = []
    for dim in filter_dict:
        temp_str = "{dim} {rel} in  ({values})".format(dim=dim, rel="not" if not filter_dict[dim]["include"] else "", values=",".join(filter_dict[dim]["values"]))
        temp_list.append(temp_str)
    return(" and ".join(temp_list))
    
def get_seller_from_seller_list(seller_list, key, value):
    return([s for s in seller_list if getattr(s, key) == value])
    
def start_gmail_server():
    smtp_serv = SMTPServer(host="smtp.gmail.com", login="henri@adomik.com", password="LarmorPl@ge46", port=465)
    cont = ssl.create_default_context()
    try:
        serv = smtplib.SMTP(smtp_serv.host)
        #serv.set_debuglevel(1)
        serv.ehlo()
        serv.starttls()
        serv.ehlo()
        print("Connexion ok")
    except:
        coderr = "%s" % sys.exc_info()[1]
        print("Connexion problem (" + coderr + ")")
        return
    if smtp_serv.login != "":
        try:
            serv.login(smtp_serv.login, smtp_serv.password)
            print("Credentials ok")
        except:
            coderr = "%s" % sys.exc_info()[1]
            serv.quit()
            print("Wrong credentials (" + coderr + ")")
            return
    return(serv)