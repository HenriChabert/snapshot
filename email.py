from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from premailer import transform
import smtplib, ssl

class SMTPServer():
    def __init__(self, host="", port=25, login="", password=""):
        """conserve les paramètres d'un compte mail sur un serveur SMTP"""
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        
class Email():
    def __init__(self, snapshot, parameters={}):
        default_parameters = {
            "recipients":"mandatory",
            "subject":"[Adomik Snapshot] Report - "+dateTimeToStr(datetime.datetime.today()),
            "sender":"report@adomik.com",
            "reply_to":"report@adomik.com",
            "title":"Report - "+dateTimeToStr(datetime.datetime.today()),
            "extra_infos":None,
            "client_message":None,
            "attachment_format":"xlsx",
            "version":"0.9",
            "smtp_server":None,
            "attach_files":True
        }
        self.parameters = check_parameters(parameters, default_parameters)
        self.snapshot = snapshot
        self.cpt_elements = 0
        self.cpt_tables = 0
        
    def build_content(self):
        self.content = ""
        self.content += self.get_email_preheader()
        self.content += self.get_email_css()
        self.content += self.get_email_header()
        for element in self.snapshot.elements:
            if element.parameters["title"] is None:
                element.parameters["title"] = u"Figure "+str(self.cpt_elements)
            else:
                element.parameters["title"] = element.parameters["title"].format(cur=element.parameters["root_snapshot_data"].snapshot.parameters["currency"]).decode("utf-8")
            self.content += self.get_element_header(element)
            if element.parameters["type"] == "graph":
                self.content += u"""<img class="element graph" src=\"""" + element.get_download_url()+ u""""/>"""
            elif element.parameters["type"] == "table":
                self.content += u"""<div class="element table" align="center">"""+element.html+u"""</div>"""
            else:
                print("Wrong element name")
            self.content += self.get_element_footer(element)
            self.cpt_elements += 1
        self.content += self.get_email_footer()
        self.html = self.content
        self.content = transform(self.content, disable_validation=True)
    
    def get_element_header(self, element):
        header_html = u"""
        <tr pardot-repeatable="" style="">
	        <td align="left" class="bodyContent" pardot-data="" pardot-region="body_content00" style="text-size-adjust: 100%; color: rgb(41, 170, 225); font-family: &quot;Nunito Sans&quot;, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 21px; text-align: left; padding: 20px; background: rgb(255, 255, 255);" valign="top">
	            <h2 style="font-family: &quot;Nunito Sans&quot;, Helvetica, Arial, sans-serif; display: block; font-size: 20px; font-weight: 300; line-height: 19px; margin-left: 0px; margin-top: 0px; margin-bottom: 10px; border-bottom: 1px solid rgb(123, 134, 145); padding-bottom: 7px; border-collapse: collapse !important; color: rgb(41, 170, 225) !important;">
	                {element_title}
	            </h2>
        """.format(element_title=element.parameters["title"])
        return(header_html)
        
    def get_element_footer(self, element):
        footer_html = u"""
            </td>
        </tr>"""
        return(footer_html)
        
    def get_email_preheader(self):
        preheader_html =  u"""
        <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
                <meta property="og:title" content="{subject}">
                <title>{subject}</title>
            </head>
            <body style="-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; height: 100% !important; width: 100% !important; background-color: #FAFAFA; margin: 0; padding: 0;" bgcolor="#FAFAFA">
        """.format(subject=self.parameters["subject"])
        
        return(preheader_html)
    
    def get_email_css(self):
        css = """
        <style type="text/css">
            {outline_css}
        </style>
        """.format(outline_css=self.parameters["outline_css"])
        return(css)
        
    def get_email_header(self):
        logo_url = get_s3_url("adomik-maths-preproduction", "henri/Adomik-official-logo-dark.png")
        
        header_html =  u"""
            <table align="center" border="0" cellpadding="0" cellspacing="0" id="bodyTable" style="-ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; background-color: #FAFAFA; border-collapse: collapse !important; height: 100% !important; margin: 0; mso-table-lspace: 0pt; mso-table-rspace: 0pt; padding: 0; width: 100% !important" width="100%">
            	<tbody>
            		<tr>
            			<td align="center" id="bodyCell" style="-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; mso-table-lspace: 0pt; mso-table-rspace: 0pt; height: 100% !important; width: 100% !important; border-top-width: 4px; border-top-color: #dddddd; border-top-style: solid; margin: 0; padding: 20px;" valign="top"><!-- BEGIN TEMPLATE // -->
            			    <table border="0" cellpadding="0" cellspacing="0" id="templateContainer" style="background: #fff; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-collapse: collapse !important; width: 800px; border: 1px solid #dddddd;">
            				    <tbody>
                				    <tr>
                						<td align="center" style="-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; mso-table-lspace: 0pt; mso-table-rspace: 0pt;" valign="top"><!-- BEGIN HEADER // -->
                    						<table border="0" cellpadding="0" cellspacing="0" id="templateHeader" style="-ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; background-color: #FFFFFF; mso-table-lspace: 0pt; mso-table-rspace: 0pt" width="100%">
                    							<tbody>
                    								<tr pardot-repeatable="" style="">
                    									<td align="left" class="headerContent" pardot-data="line-height:12px;" pardot-region="header_image" style="background: url({header_img});background-size: contain;background-position: -21% 50%;background-repeat: no-repeat;position:relative;height: 360px;text-size-adjust: 100%;color: rgb(80, 80, 80);font-family: Helvetica;font-size: 40px;font-weight: bold;line-height: 12px;text-align: left;vertical-align: middle;padding: 0 20px 20px 20px;" valign="top">
                        									<table border="0" cellpadding="10" cellspacing="0" class="brandtable" style="width: 358px;">
                        										<tbody>
                        											<tr>
                        												<td style="width: 334px;"><a href="https://www.adomik.com/"><img alt="" border="0" height="32" src="{adomik_logo}" style="position: relative;z-index: 1;width: 135px;height: 32px;margin: 15px 0 20px 0;border-width: 0px;border-style: solid;" width="135"></a>
                        												<h1 style="color: #435060;font-family:'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 26px;line-height: 30px;margin: 0 0 0px 0;font-weight: 300;">{title}</h1>
                        												<h2 style="color: #29aae1;font-family:'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 16px;line-height: 22px;margin: 0 0 15px 0;font-weight: 300;font-style: italic;">{subtitle}</h2>
                        												<a href="{cta_link}"><img alt="" border="0" height="44" src="{cta_btn}" style="width: 130px; height: 44px; border-width: 0px; border-style: solid;" width="130"></a><br>
                        												<br>
                        												&nbsp;&nbsp;</td>
                        											</tr>
                        										</tbody>
                        									</table>
                    									</td>
                    								</tr>
                    							</tbody>
                    						</table>
                    						<!-- // END HEADER --></td>
            					       </tr>
            					       <tr>
                			               <td align="center" style="-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; mso-table-lspace: 0pt; mso-table-rspace: 0pt;" valign="top"><!-- BEGIN BODY // --><!-- Introduction ---->
                					           <table border="0" cellpadding="0" cellspacing="0" id="Bloc1" style=" -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; background-color: #FFFFFF; mso-table-lspace: 0pt; mso-table-rspace: 0pt" width="100%">
                					               <tbody>
                    						           <tr pardot-repeatable="" style="">
                    							           <td align="left" class="bodyContent" pardot-data="" pardot-region="body_content00" style="text-size-adjust: 100%; color: rgb(102, 102, 102); font-family: &quot;Nunito Sans&quot;, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 21px; text-align: left; padding: 20px; background: rgb(255, 255, 255);" valign="top">
                    							               <div class="client_message" style="text-align: center;">{client_message}</div>
                    							           </td>
                    								    </tr>
        """.format(adomik_logo=get_s3_url("adomik-maths-preproduction", "henri/uplift_reports/img/logo_adomik.png"),\
        header_img=get_s3_url("adomik-maths-preproduction", "henri/uplift_reports/img/Homepage_big.jpg"),\
        title=self.parameters["title"].decode("utf-8"),\
        subtitle=self.parameters["subtitle"].decode("utf-8"),\
        cta_btn=self.parameters["cta_btn"],\
        cta_link=self.parameters["cta_link"],\
        client_message=self.parameters["client_message"].decode("utf-8"))
        return(header_html)
        
    def get_email_footer(self):
        footer_html =  u"""
                                </tbody>
        					</table>
        					<table border="0" cellpadding="0" cellspacing="0" id="Wave-separator2" style=" -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; mso-table-lspace: 0pt; mso-table-rspace: 0pt" width="100%">
        						<tbody style="">
        							<tr pardot-repeatable="" style="" class="">
        								<td align="left" class="bodyContent" pardot-region="body_content00" style="-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;mso-table-lspace: 0pt;mso-table-rspace: 0pt;color: #666666;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 14px;line-height: 21px;text-align: left;" valign="top"><img alt="" border="0" height="147" src="{footer_img}" style="width: 805px; height: 147px; border-width: 0px; border-style: solid;" width="805"></td>
        							</tr>
        						</tbody>
        					</table>
        					<table border="0" cellpadding="0" cellspacing="0" id="templatePreheader6" style=" -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; background-color: #FFFFFF; mso-table-lspace: 0pt; mso-table-rspace: 0pt" width="100%">
							    <tbody>
								    <tr class="bloca4" pardot-repeatable="" style="">
									    <td align="left" class="bodyContent" pardot-region="body_content00" style="background-color: #FFFFFF;border-collapse: collapse !important;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;mso-table-lspace: 0pt;mso-table-rspace: 0pt;color: #505050;font-family: Helvetica;font-size: 14px;line-height: 21px;text-align: left;padding: 10px 0 10px 0;" valign="top">
    									    <h2 style="text-align: center;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-weight: 500;"><span style="color:#5c677c;">Adomik Suite of products</span></h2>
                                            <table style="width:100%; padding:10px;">
                                            	<tbody style="width:100%;">
                                            		<tr style="width:100%">
                                            			<td class="borderd" style="border: 1px solid #E7EBEC;border-radius: 2px;box-shadow: 0 2px 4px 1px #E7EBEC;padding: 0px 5px 0 5px !important;width: 19.2%;text-align: left;background-color: #FFFFFF;border-bottom-color: #ea443d;border-bottom-style: solid;border-bottom-width: 3px;border-collapse: collapse !important;"><img alt="" border="0" height="45" src="http://go.pardot.com/l/709813/2019-02-25/3yh/709813/508/icon_produit_report.png" style="width: 45px; height: 45px; border-width: 0px; border-style: solid;" width="45">
                                            			<h3 style="color:#EA433B;margin: 10px 0 3px 0 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;line-height: 17px;height: 35px;"><a href="https://www.adomik.com/adomik-report/" style="text-decoration:none;color:#EA433B !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 16px;font-weight: 300;">Report</a></h3>
                                            			<a href="https://www.adomik.com/adomik-report/" style="text-decoration:none;color:#666666;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 11px;line-height: 15px;height: 70px;display: block;">All of your advertising data in one place</a></td>
                                            			<td style="width: 1%;">&nbsp;</td>
                                            			<td class="borderd" style="border: 1px solid #E7EBEC;border-radius: 2px;box-shadow: 0 2px 4px 1px #E7EBEC;padding: 0px 5px 0 5px !important;width: 19.2%;text-align: left;background-color: #FFFFFF;border-bottom-color: #12abf1;border-bottom-style: solid;border-bottom-width: 3px;border-collapse: collapse !important;"><img alt="" border="0" height="45" src="http://go.pardot.com/l/709813/2019-02-25/3yk/709813/510/icon_produit_price_.png" style="width: 45px; height: 45px; border-width: 0px; border-style: solid;" width="45">
                                            			<h3 style="color:#12ABF1;margin: 10px 0 0 0 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;line-height: 17px;height: 35px;"><a href="https://www.adomik.com/adomik-price/" style="text-decoration:none;color:#12ABF1 !important;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 16px;font-weight: 300;">Price</a></h3>
                                            			<a href="https://www.adomik.com/adomik-price/" style="text-decoration:none;color:#666666;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 11px;line-height: 15px;height: 70px;display: block;">Make more money with intelligent pricing</a></td>
                                            			<td style="width: 1%;">&nbsp;</td>
                                            			<td class="borderd" style="border: 1px solid #E7EBEC;border-radius: 2px;box-shadow: 0 2px 4px 1px #E7EBEC;padding: 0px 5px 0 5px !important;width: 19.2%;text-align: left;background-color: #FFFFFF;border-bottom-color: #eca322;border-bottom-style: solid;border-bottom-width: 3px;border-collapse: collapse !important;"><img alt="" border="0" height="45" src="http://go.pardot.com/l/709813/2019-02-22/3b5/709813/468/Copy_of_icon_produit_sell.png" style="width: 45px; height: 45px; border-width: 0px; border-style: solid;" width="45">
                                            			<h3 style="color:#eca322;margin: 10px 0 3px 0 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;line-height: 17px;height: 35px;"><a href="https://www.adomik.com/adomik-sell/" style="text-decoration:none;color: #eca322 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 16px;font-weight: 300;">Sell</a></h3>
                                            			<a href="https://www.adomik.com/adomik-sell/" style="text-decoration:none;color: #666666;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 11px;line-height: 15px;height: 70px;display: block;">Stay ahead with our exclusive advertising market index</a></td>
                                            			<td style="width: 1%;">&nbsp;</td>
                                            			<td class="borderd" style="border: 1px solid #E7EBEC;border-radius: 2px;box-shadow: 0 2px 4px 1px #E7EBEC;padding: 0px 5px 0 5px !important;width: 19.2%;text-align: left;background-color: #FFFFFF;border-bottom-color: #e76803;border-bottom-style: solid;border-bottom-width: 3px;border-collapse: collapse !important;"><img alt="" border="0" height="45" src="http://go.pardot.com/l/709813/2019-02-25/43y/709813/514/icon_produit_manage_.png" style="width: 45px; height: 45px; border-width: 0px; border-style: solid;" width="45">
                                            			<h3 style="color:#e76803;margin: 10px 0 3px 0 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;line-height: 17px;height: 35px;"><a href="https://www.adomik.com/adomik-manage/" style="text-decoration:none;color:#e76803 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 16px;font-weight: 300;">Manage</a></h3>
                                            			<a href="https://www.adomik.com/adomik-manage/" style="text-decoration:none;color:#666666;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 11px;line-height: 15px;height: 70px;display: block;">Fuel your internal tools with the raw dataset you need</a></td>
                                            			<td style="width: 1%;">&nbsp;</td>
                                            			<td class="borderd" style="border: 1px solid #E7EBEC;border-radius: 2px;box-shadow: 0 2px 4px 1px #E7EBEC;padding: 0px 5px 0 5px !important;width: 19.2%;text-align: left;background-color: #FFFFFF;border-bottom-color: #64778f;border-bottom-style: solid;border-bottom-width: 3px;border-collapse: collapse !important;"><img alt="" border="0" height="45" src="http://go.pardot.com/l/709813/2019-03-11/77r/709813/1346/icon_prof_serv.png" style="width: 45px; height: 45px; border-width: 0px; border-style: solid;" width="45">
                                            			<h3 style="color: #64778f;margin: 10px 0 3px 0 !important;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;line-height: 17px;height: 35px;"><a href="https://www.adomik.com/adomik-troubleshoot/" style="text-decoration:none;color: #64778f !important;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;font-size: 16px;font-weight: 300;">Professional Services</a></h3>
                                            			<a href="https://www.adomik.com/adomik-troubleshoot/" style="color:#666666;margin:0;font-family: 'Nunito Sans', Helvetica, Arial, Sans-serif;text-decoration:none;font-size: 11px;line-height: 15px;height: 70px;display: block;">Consulting and customized sevices</a></td>
                                            		</tr>
                                            	</tbody>
                                            </table>    
                                        </td>
    								</tr>
    							</tbody>
    						</table>
        				</td>
                    </tr>
                 </tbody>
              </table>
           </body>
        </html>""".format(footer_img=get_s3_url("adomik-maths-preproduction", "henri/uplift_reports/img/price_page_waves2.png"))
        return(footer_html)
        
    def build_message(self):
        # Create the root message and fill in the from, to, and subject headers
        self.msg = MIMEMultipart('related')
        self.msg['Subject'] = self.parameters["subject"]
        self.msg['From'] = self.parameters["sender"]
        self.msg['To'] = ",".join(self.parameters["recipients"])
        self.msg.add_header('reply-to', self.parameters["reply_to"])
        self.msg.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display
        self.msgAlternative = MIMEMultipart('alternative')
        self.msg.attach(self.msgAlternative)

        # first add plain text
        self.msg_text = MIMEText('The sender was not able to send you the email in an HTML format')
        self.msgAlternative.attach(self.msg_text)
        
        if self.parameters['attach_files']:
            for el in self.snapshot.elements:
                if el.parameters['type'] == "table":
                    filename = el.parameters['attachment_name']+"."+self.parameters["attachment_format"] if not el.parameters['attachment_name'] is None else "table"+str(self.cpt_tables)+"."+self.parameters["attachment_format"]
                    attachment = MIMEApplication(export_excel(el.pddf))
                    attachment['Content-Disposition'] = "attachment; filename= %s" % filename
                    self.msg.attach(attachment)
                    self.cpt_tables += 1

        self.build_content()

        self.msg_html = MIMEText(self.content, 'html', 'utf-8')
        self.msgAlternative.attach(self.msg_html)
        
        print("!! email ready to be sent !!")
        
        return(self.msg)

    def send_email(self, server="adomik"):
        if server == "localhost":
            s = smtplib.SMTP('localhost')
        elif server == "adomik":
            print("Start sending")
            if self.parameters["smtp_server"] is None:
                s = start_gmail_server()
            else:
                s = self.parameters["smtp_server"]
            print("Connexion and credentials ok")
                    
        attached_msg = self.build_message().as_string()
        print("Message built")
        s.sendmail(self.parameters["sender"], self.parameters["recipients"]+["henri@adomik.com"], attached_msg)
        print("Message sent") 