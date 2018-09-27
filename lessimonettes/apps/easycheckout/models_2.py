#!/usr/local/bin/python
# coding: utf-8

from django.db import models
from django.template.defaultfilters import slugify

from django.utils.translation import ugettext as _
from simpleproduct.models import *
from django.core.mail import send_mail
#try:
#    from django.contrib.auth import get_user_model
#except ImportError:
#    from django.contrib.auth.models import User
from django.contrib.auth.models import User

STATUS = [
    (u'Validée', u'Validée'),
    (u'Annulée', u'Annulée'),
    (u'En cours', u'En cours'),
]
class BaseAddress(models.Model):
    """
    Base address

    BaseAddress class to create un new address
    """   

    user = models.ForeignKey(User, verbose_name="Utilisateur")
    name = models.CharField(_(u"Nom et prénom*"), max_length=1024)
    phone_number = models.CharField(_(u'Numéro de téléphone*'), max_length=250)
    address1 = models.CharField(_("Adresse 1*"), max_length=1024)
    address2 = models.CharField(_("Adresse 2"), max_length=1024, blank=True, null=True)
    zip_code = models.CharField(_("Code postal*"), max_length=12)
    city = models.CharField(_("Ville*"), max_length=1024)
    country = models.CharField(_("Pays"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Addresse de livraison')
        verbose_name_plural = _('Adresses de livraison')

    def save(self, *args, **kwargs):
        super(BaseAddress, self).save()

    def __str__(self):
        return self.address1

    def get_as_text(self):
        """
        Return this comment as plain text. Useful for emails.
        """
        d = {
            'name': self.name,
            'phone': self.phone_number,
            'address1': self.address1,
            'address2': self.address2,
            'zip_code': self.zip_code,
            'city': self.city,
        }
        return ('%(name)s\r\n'
                  '%(phone)s\r\n'
                  '%(address1)s\r\n'
                  '%(address2)s\r\n'
                  '%(zip_code)s\r\n'
                  '%(city)s') % d

class ShippingAddress(BaseAddress):
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")

class BillingAddress(BaseAddress):
    class Meta:
        verbose_name = _("Billing Address")
        verbose_name_plural = _("Billing Addresses")


class OrderManager(models.Manager):
    def create_order(self, user_pk, status):
        order = self.create(user=user_pk, status=status)
        return order

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur")
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    status = models.CharField(_(u'Etat'), choices=STATUS, max_length=150, blank=True)
    total = models.IntegerField(_(u'Total'), blank=True, null=True, default=0)
    delivery_date = models.DateField(_(u'Date de livraison souhaitée'), blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, verbose_name="Adresse de livraison*", null=True, blank=True)
    billing_as_shipping = models.BooleanField(_(u'Utiliser l\'adresse de livraison comme adresse de facturation'), default=True)
    billing_address = models.ForeignKey(BillingAddress, verbose_name="Adresse de facturation", null=True, blank=True)
    cgv = models.BooleanField(_(u'Valider les conditions générales de vente'), default=False)
    use_credit = models.BooleanField(_(u'Je souhaite utiliser mon avoir'), default=False)
    is_paid = models.BooleanField(_(u'A été payée'), default=False)
    payment_status = models.CharField(_(u'Status du paiement'), max_length=250, blank=True)
    payment_auth_code = models.CharField(_(u'Code \'authorisation'), max_length=250, blank=True)
    chronopost = models.CharField(_(u'Code chronopost'), max_length=150, blank=True)

    objects = OrderManager()

    class Meta:
        verbose_name = _('Commande')
        verbose_name_plural = _('Commandes')

    def save(self, *args, **kwargs):
        remained = False
        if self.status == 'En cours':
            remained = False
        elif self.status == 'Annulée':
            remained = False
        else:
            remained = True
        if self.chronopost != '':
            send_mail(
                u'Envoie du steak : votre numéro de suivi Chronofresh©',
                u'Bonjour '+self.shipping_address.name+',\r\n Votre commande n°'+str(self.pk)+'. est en cours de préparation dans nos locaux.\r\n\r\nLa livraison est prévue pour le '+str(self.delivery_date)+' entre 8h et 13h à l’adresse suivante: '+self.shipping_address.get_as_text()+'\r\n\r\n\r\nVous pouvez suivre les étapes de la livraison sur www.chronopost.fr en saisissant le numéro de suivi Chronopost: '+self.chronopost+' ou en vous connectant à l\'adresse suivante : https://www.chronopost.fr/fr/chrono_suivi_search?listeNumerosLT='+self.chronopost+'&lang=fr&op=&form_build_id=form-eiwQhOOFYadiSnafKd_nsSITf3HefjpjjZ6w4mT1o_U&form_id=chrono_suivi_colis_block_form.\r\n\r\nLorsque votre commande sera prise en charge par Chronopost, vous recevrez un email et un sms vous en informant.\r\nVous aurez alors la possibilité de modifier le jour et/ou le lieu de livraison si besoin.\r\n\r\nChronofresh garantit un transport entre 0 et 4°C jusqu’à chez vous. N’oubliez pas ensuite de mettre vos produits au frais !\r\n\r\nSi vous avez la moindre question, n’hésitez pas à nous contacter par mail (bonjour@envoiedusteak.fr), nous nous ferons un plaisir de vous répondre.\r\n\r\nAllez, à nous d’envoyer maintenant !\r\n\r\nAu plaisir de vous revoir sur envoiedusteak.fr\r\n\r\nRetrouvez-nous également sur https://www.facebook.com/envoiedusteak/',
                u'bonjour@envoiedusteak.fr',
                [self.user.email,],
                fail_silently=False,
             ) 
        super(Order, self).save()

    def __str__(self):
        return u'Commande {0}'.format(self.pk)

    def get_bill(self):
        try:
            bill = Bill.objects.filter(order=self).first()
            return str(bill.id)
        except:
            pass

    def get_items(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = Item.objects.filter(order=self)
        return items

    def get_items_as_text(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """  
        items = Item.objects.filter(order=self)
        items_text = ""
        for i in items:
            items_text += str(i.product.title)+' - Poids de la pièce : '+str(i.basis_weight)+'g - Quantité : x'+str(i.quantity)+'\r\n'
            #if i.orientation == 1 or i.orientation == 2:
            #    "Cowfunding"
        return items_text



    def get_total_weight(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = Item.objects.filter(order=self)
        weight = 0
        for i in items:
            weight += i.quantity * i.basis_weight
        return weight


    def calculate_stock_delivery(self):
        """
        Function to get all stock items from an order
        and calculate delivery price
            :param self: 

            Return:
                object: 
        """   
        items = Item.objects.filter(order=self, product__category__slug="stock")
        total = 0
        if items:
            for i in items:
                total += int(i.quantity) * int(i.basis_weight) * int(i.product.price) / 1000
            if total >= 50:
                delivery = 7
            elif total >= 100:
                delivery = 0
            else:
                delivery = 15
        else:
            delivery = 0
        return delivery 

    def calculate_cowfunding_delivery(self):
        """
        Function to get all cowfunding from an order
        and calculate delivery price
            :param self: 

            Return:
                object: 
        """ 
        items = Item.objects.filter(order=self, product__category__slug="cowfunding")
        total = 0
        panier = 0
        if items:
            for i in items:
                if i.orientation.pk == 1:
                    cowfunding = True
                if i.product.title == "Steak":
                    panier += 70 * i.quantity
                if i.product.title == "Faux-filet":
                    panier += 5 * i.quantity
                    fauxfilet = True
                if i.product.title == "Façon tournedos":
                    panier += 5 * i.quantity
                if i.orientation.pk == 2:
                    panier += int(i.quantity) * int(i.basis_weight) * int(i.product.price) / 1000
            total = panier
            if total >= 100:
                delivery = 0
            else:
                delivery = 7
        else:
            delivery = 0
        return delivery 

    def calculate_dry_delivery(self):
        """
        Function to get all dry items from an order
        and calculate delivery price
            :param self: 

            Return:
                object: 
        """   
        items = Item.objects.filter(order=self, product__category__slug="dry")
        total = 0
        if items:
            for i in items:
                total += int(i.quantity) * int(i.basis_weight) * int(i.product.price) / 1000
            if total >= 100:
                delivery = 0
            else:
                delivery = 7
        else:
            delivery = 0
        return delivery 




    def subtract_items(self):
        """
        Function to subtract weight to a muscle from each item
            :param self: 

            Return:
                string: 
        """   
        items = Item.objects.filter(order=self)
        for i in items:
            if (i.product.category.slug == 'stock') or (i.product.category.slug == 'dry'):
                i.product.number = i.product.number - i.quantity
                i.product.save()
            elif i.product.category.slug == 'cowfunding':
                for n in range(int(i.quantity)):
                #weight_to_subtract = int(i.quantity) * int(i.basis_weight)
                    i.product.subtract_weight_to_product(int(i.product.weight))
                    i.product.save()

    def empty_order(self):
        """
        Function to empty the order
        Delete all items in relation with the order
            :param self: 

            Return:
                string: 
        """   
        items = Item.objects.filter(order=self)
        for i in items:
            i.delete()

    def get_delivery(self):
        total = 0
        cowfunding_delivery = self.calculate_cowfunding_delivery()
        stock_delivery = self.calculate_stock_delivery()
        dry_delivery = self.calculate_dry_delivery()
        delivery = cowfunding_delivery + stock_delivery + dry_delivery
        return delivery

    def total_product(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        fauxfilet = False
        cowfunding = False
        for i in self.get_items():
            if i.orientation.pk == 1:
                cowfunding = True
            if i.product.title == "Steak":
                panier += 70 * i.quantity
            if i.product.title == "Faux-filet":
                panier += 5 * i.quantity
                fauxfilet = True
            if i.product.title == "Façon tournedos":
                panier += 5 * i.quantity
            if i.orientation.pk == 1:
                total += 0
            else:
                #total += (float(i.quantity) * float(i.product.price) * float(i.basis_weight))/1000
                other_total = (float(i.quantity) * float(i.product.price) * float(i.basis_weight))/1000
                #add TVA
                #other_total = other_total + other_total * 5.5/100
                total += other_total
        if cowfunding:
            total += panier
        return int(total*100)

    def total_cowfunding(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        fauxfilet = False
        cowfunding = False
        for i in self.get_items():
            if i.orientation.pk == 1:
                cowfunding = True
            if i.product.title == "Steak":
                panier += 70 * i.quantity
            if i.product.title == "Faux-filet":
                panier += 5 * i.quantity
                fauxfilet = True
            if i.product.title == "Façon tournedos":
                panier += 5 * i.quantity
        return int(panier)

    def total_complements(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        for i in self.get_items():
            if i.orientation.pk == 2:
                panier_ht += (i.quantity * i.basis_weight * i.product.price) / 10
                panier_ttc = panier_ht + panier_ht * 5.5 /100
                panier += panier_ttc
        return int(panier)


    def total_quantity_cowfunding(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        quantity = 0
        for i in self.get_items():
            if i.product.title == "Steak":
                quantity += i.quantity
        return int(quantity)



    def total_amount(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        fauxfilet = False
        cowfunding_delivery = self.calculate_cowfunding_delivery()
        stock_delivery = self.calculate_stock_delivery()
        dry_delivery = self.calculate_dry_delivery()


        total_credit = 0
        if self.use_credit:
            credit = Credit.objects.filter(user=self.user).first()
            if credit:
                total_credit = credit.total
            else:
                total_credit = 0

        delivery = cowfunding_delivery + stock_delivery + dry_delivery
        cowfunding = False
        #total += delivery * 1000
        for i in self.get_items():
            if i.orientation.pk == 1:
                cowfunding = True
            if i.product.title == "Steak":
                panier += 70 * i.quantity
            if i.product.title == "Faux-filet":
                panier += 5 * i.quantity
                fauxfilet = True
            if i.product.title == "Façon tournedos":
                panier += 5 * i.quantity
            if i.orientation.pk == 1:
                total += 0
            else:
                other_total = (float(i.quantity) * float(i.product.price) * float(i.basis_weight))/1000
                #add TVA
                other_total = other_total + other_total * 5.5/100
                total += other_total
        if cowfunding:
            total += panier
        #add delivery
        total += delivery
        total = int(total*100)
        if total_credit < total:
            total = total - total_credit
        else:
            total = 700
        if self.total != total:
            self.total = total
            self.save()
        return total

class ItemManager(models.Manager):
    def create_item(self, order_pk, product_pk, quantity, basis_weight, orientation):
        item = self.create(order=order_pk, product=product_pk, quantity=quantity, basis_weight=basis_weight, orientation=orientation)
        return item

class Item(models.Model):
    order = models.ForeignKey(Order, verbose_name="Commande")
    product = models.ForeignKey(Product, verbose_name="Produit")
    quantity = models.IntegerField(verbose_name="Quantité", default=1)
    basis_weight = models.PositiveIntegerField(verbose_name="Poids de la pièce", null=True, blank=True)
    orientation = models.ForeignKey(Orientation, verbose_name="Orientation", null=True, blank=True)
    #orientation = models.CharField(verbose_name="Orientation", max_length=255, null=True, blank=True)

    objects = ItemManager()
    
    def save(self, *args, **kwargs):
        super(Item, self).save()

    def __str__(self):
        return self.product.title

    def get_price(self):
        return (self.quantity * self.product.price * self.basis_weight) / 1000


class OrderCartManager(models.Manager):
    def create_order_cart(self, status):
        order = self.create(status=status)
        return order

class OrderCart(models.Model):
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    status = models.CharField(_(u'panier'), max_length=500, blank=True)
    total = models.IntegerField(_(u'Total'), blank=True, null=True, default=0)

    objects = OrderCartManager()

    class Meta:
        verbose_name = _('Panier')
        verbose_name_plural = _('Paniers')

    def save(self, *args, **kwargs):
        super(OrderCart, self).save()

    def __str__(self):
        return u'Panier {0}'.format(self.pk)

    def get_items(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        return items

    def get_total_weight(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        weight = 0
        for i in items:
            weight += i.quantity * i.basis_weight
        return weight


    def calculate_stock_delivery(self):
        """
        Function to get all stock items from an order
        and calculate delivery price
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self, product__category__slug="stock")
        total = 0
        if items:
            for i in items:
                total += int(i.quantity) * int(i.basis_weight) * int(i.product.price) / 1000
            if total >= 50:
                delivery = 7
            elif total >= 100:
                delivery = 0
            else:
                delivery = 15
        else:
            delivery = 0
        return delivery 

    def calculate_cowfunding_delivery(self):
        """
        Function to get all cowfunding from an order
        and calculate delivery price
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self, product__category__slug="cowfunding")
        total = 0
        panier = 0
        if items:
            for i in items:
                if i.orientation.pk == 1:
                    cowfunding = True
                if i.product.title == "Steak":
                    panier += 70 * i.quantity
                if i.product.title == "Faux-filet":
                    panier += 5 * i.quantity
                    fauxfilet = True
                if i.product.title == "Façon tournedos":
                    panier += 5 * i.quantity
                if i.orientation.pk == 2:
                    panier += int(i.quantity) * int(i.basis_weight) * int(i.product.price) / 1000
            total = panier
            if total >= 100:
                delivery = 0
            else:
                delivery = 7
        else:
            delivery = 0
        return delivery 


    def total_cowfunding(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        fauxfilet = False
        cowfunding = False
        for i in self.get_items():
            if i.orientation.pk == 1:
                cowfunding = True
            if i.product.title == "Steak":
                panier += 70 * i.quantity
            if i.product.title == "Faux-filet":
                panier += 5 * i.quantity
                fauxfilet = True
            if i.product.title == "Façon tournedos":
                panier += 5 * i.quantity
        return int(panier)

    def total_complements(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        for i in self.get_items():
            if i.orientation.pk == 2:
                panier_ht = (i.quantity * i.basis_weight * i.product.price) / 10
                panier_ttc = float(panier_ht) + float(panier_ht) * 5.5 /100
                panier += panier_ttc
        return int(panier)



    def calculate_dry_delivery(self):
        """
        Function to get all dry items from an order
        and calculate delivery price
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self, product__category__slug="dry")
        total = 0
        if items:
            for i in items:
                total += int(i.quantity) * int(i.basis_weight) * int(i.product.price) / 1000
            if total >= 100:
                delivery = 0
            else:
                delivery = 7
        else:
            delivery = 0
        return delivery 




    def subtract_items(self):
        """
        Function to subtract weight to a muscle from each item
            :param self: 

            Return:
                string: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        for i in items:
            if (i.product.category.slug == 'stock') or (i.product.category.slug == 'dry'):
                i.product.number = i.product.number - i.quantity
                i.product.save()
            elif i.product.category.slug == 'cowfunding':
                for n in range(int(i.quantity)):
                #weight_to_subtract = int(i.quantity) * int(i.basis_weight)
                    i.product.subtract_weight_to_product(int(i.product.weight))
                    i.product.save()

    def empty_order(self):
        """
        Function to empty the order
        Delete all items in relation with the order
            :param self: 

            Return:
                string: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        for i in items:
            i.delete()

    def get_delivery(self):
        total = 0
        cowfunding_delivery = self.calculate_cowfunding_delivery()
        stock_delivery = self.calculate_stock_delivery()
        dry_delivery = self.calculate_dry_delivery()
        delivery = cowfunding_delivery + stock_delivery + dry_delivery
        return delivery

    def total_product(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        fauxfilet = False
        cowfunding = False
        for i in self.get_items():
            if i.orientation.pk == 1:
                cowfunding = True
            if i.product.title == "Steak":
                panier += 70 * i.quantity
            if i.product.title == "Faux-filet":
                panier += 5 * i.quantity
                fauxfilet = True
            if i.product.title == "Façon tournedos":
                panier += 5 * i.quantity
            if i.orientation.pk == 1:
                total += 0
            else:
                total += (float(i.quantity) * float(i.product.price) * float(i.basis_weight))/1000
        if cowfunding:
            total += panier
        return int(total*100)

    def total_amount(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        fauxfilet = False
        cowfunding_delivery = self.calculate_cowfunding_delivery()
        stock_delivery = self.calculate_stock_delivery()
        dry_delivery = self.calculate_dry_delivery()

        delivery = cowfunding_delivery + stock_delivery + dry_delivery
        cowfunding = False
        for i in self.get_items():
            if i.orientation.pk == 1:
                cowfunding = True
            if i.product.title == "Steak":
                panier += 70 * i.quantity
            if i.product.title == "Faux-filet":
                panier += 5 * i.quantity
                fauxfilet = True
            if i.product.title == "Façon tournedos":
                panier += 5 * i.quantity
            if i.orientation.pk == 1:
                total += 0
            else:
                other_total = (float(i.quantity) * float(i.product.price) * float(i.basis_weight))/1000
                #add TVA
                other_total = other_total + other_total * 5.5/100
                total += other_total
        if cowfunding:
            total += panier
        #add TVA
        total = total + total * 5.5/100
        #add delivery
        total += delivery
        total = int(total*100)
        if self.total != total:
            self.total = total
            self.save()
        return total

class ItemCartManager(models.Manager):
    def create_item_cart(self, order_cart_pk, product_pk, quantity, basis_weight, orientation):
        item = self.create(order_cart=order_cart_pk, product=product_pk, quantity=quantity, basis_weight=basis_weight, orientation=orientation)
        return item

class ItemCart(models.Model):
    order_cart = models.ForeignKey(OrderCart, verbose_name="Commande")
    product = models.ForeignKey(Product, verbose_name="Produit")
    quantity = models.IntegerField(verbose_name="Quantité", default=1)
    basis_weight = models.PositiveIntegerField(verbose_name="Poids de la pièce", null=True, blank=True)
    orientation = models.ForeignKey(Orientation, verbose_name="Orientation", null=True, blank=True)

    objects = ItemCartManager()
    
    def save(self, *args, **kwargs):
        super(ItemCart, self).save()

    def __str__(self):
        return self.product.title

    def get_price(self):
        return (self.quantity * self.product.price * self.basis_weight) / 1000

class Credit(models.Model):
    reference = models.CharField(_(u'Référence'), max_length=20, blank=True)
    user = models.ForeignKey(User, verbose_name="Utilisateur")
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    total = models.IntegerField(_(u'Total'), blank=True, null=True, default=0)

    def save(self, *args, **kwargs):
        super(Credit, self).save()

    def __str__(self):
        return self.reference


class Bill(models.Model):
    reference = models.CharField(_(u'Référence'), max_length=20, blank=True)
    order = models.ForeignKey(Order, verbose_name="Commande")
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    credit = models.IntegerField(_(u'Avoir'), blank=True, null=True, default=0)
    total_product_ht = models.FloatField(_(u'Total hors taxes'), blank=True, null=True, default=0)
    total_product_tva = models.FloatField(_(u'Total TVA'), blank=True, null=True, default=0)
    total_delivery_ht = models.FloatField(_(u'Total hors taxes des frais de livraison'), blank=True, null=True, default=0)
    total_delivery_tva = models.FloatField(_(u'Total TVA des frais de livraison'), blank=True, null=True, default=0)
   
    def __str__(self):
        return self.reference

    def get_total_invoice_ttc(self):
        return self.total_product_ht + self.total_product_tva + self.total_delivery_ht + self.total_delivery_tva

    def get_total_invoice_ht(self):
        return self.total_product_ht + self.total_delivery_ht

    def get_total_amount(self):
        return self.total_product_ht + self.total_product_tva + self.total_delivery_ht + self.total_delivery_tva - self.credit/100

    def get_total_product(self):
        return self.total_product_ht + self.total_product_tva
    
    def get_total_delivery(self):
        return self.total_delivery_ht + self.total_delivery_tva

    def recalculate(self):
        self.save()

    def save(self, *args, **kwargs):
        super(Bill, self).save()
        cowfunding_delivery = self.order.calculate_cowfunding_delivery()
        stock_delivery = self.order.calculate_stock_delivery()
        dry_delivery = self.order.calculate_dry_delivery()

        delivery = cowfunding_delivery + stock_delivery + dry_delivery

        self.total_product_ht = (self.order.total_product()/100) / 1.055
        self.total_delivery_ht = delivery / 1.2
        self.total_product_tva = (self.order.total_product()/100) - ((self.order.total_product()/100) / 1.055)
        self.total_delivery_tva = delivery - (delivery / 1.2)
        super(Bill, self).save()

            
            
