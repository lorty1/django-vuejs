from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from datetime import datetime, timedelta
from .models import Order, Item, BaseAddress
from simpleproduct.models import Product, Cow, Muscle, Orientation, MuscleType, Category
from django.core.management import call_command

class OrderTests(TestCase):
    def setUp(self):
        call_command('loaddata', 'test_fixtures.json', verbosity=0)
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='pierre', email='contact@manufacturegenerale.com', password='top_secret')
        #entrecôte en stock = ID 1
        self.product_in_stock = Product.objects.get(pk=1)
        #rôti en cowfunding = ID 44
        self.product_in_cowfunding = Product.objects.get(pk=44)

    def test_get_items(self):
        """
        Vérifie si la méthode est_recent d'un Article ne
        renvoie pas True si l'Article a sa date de publication
        dans le futur.
        """

        order = Order(user=self.user, date=datetime.now(), status="En cours", total=100)
        order.save()
        # Il n'y a pas besoin de remplir tous les champs, ni de sauvegarder
        #If no items in order
        test = []
        self.assertEqual(list(order.get_items()), test)

        #If list of items in order
        item1 = Item.objects.create_item(order, self.product_in_stock, 1, "200g", "-")
        item2 = Item.objects.create_item(order, self.product_in_cowfunding, 1, "200g", "-")
        test = [item1, item2]
        self.assertEqual(list(order.get_items()), test)
        


# Create your tests here.
#Je suis un utilisateur connecté
#J'ajoute au panier un produit en stock
#J'ajoute au panier un produit en cowfunding
#Je créer ma commande
#Je paye, ma commande est validée

#c = Client()
#c.login(username='test', password='test1982')
#reponse = c.get('/une/url/')
#c.logout()  # La déconnexion n'est pas obligatoire