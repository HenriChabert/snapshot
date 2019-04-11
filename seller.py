class Seller():
    def __init__(self, seller_id, seller_name=None, product="display", email=[], tam=None, custom_filter=None, attach_file=True, send_mail=True):
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.product = product
        self.email = email
        self.custom_filter = custom_filter
        self.attach_file = attach_file
        self.tam = tam
        self.send_mail = send_mail