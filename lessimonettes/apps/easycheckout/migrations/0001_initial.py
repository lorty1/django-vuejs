# Generated by Django 2.0.1 on 2018-09-21 09:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('simpleproduct', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, verbose_name='Nom et prénom*')),
                ('phone_number', models.CharField(max_length=250, verbose_name='Numéro de téléphone*')),
                ('address1', models.CharField(max_length=1024, verbose_name='Adresse 1*')),
                ('address2', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Adresse 2')),
                ('zip_code', models.CharField(max_length=12, verbose_name='Code postal*')),
                ('city', models.CharField(max_length=1024, verbose_name='Ville*')),
                ('country', models.CharField(blank=True, max_length=255, null=True, verbose_name='Pays')),
            ],
            options={
                'verbose_name': 'Addresse de livraison',
                'verbose_name_plural': 'Adresses de livraison',
            },
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(blank=True, max_length=20, verbose_name='Référence')),
                ('date', models.DateField(auto_now=True, verbose_name='date')),
                ('total', models.IntegerField(blank=True, default=0, null=True, verbose_name='Total')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Quantité')),
                ('basis_weight', models.PositiveIntegerField(blank=True, null=True, verbose_name='Poids de la pièce')),
            ],
        ),
        migrations.CreateModel(
            name='ItemCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Quantité')),
                ('basis_weight', models.PositiveIntegerField(blank=True, null=True, verbose_name='Poids de la pièce')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True, verbose_name='date')),
                ('status', models.CharField(blank=True, choices=[('Validée', 'Validée'), ('Annulée', 'Annulée'), ('En cours', 'En cours')], max_length=150, verbose_name='Etat')),
                ('total', models.IntegerField(blank=True, default=0, null=True, verbose_name='Total')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='Date de livraison prévue')),
                ('billing_as_shipping', models.BooleanField(default=True, verbose_name="Utiliser l'adresse de livraison comme adresse de facturation")),
                ('cgv', models.BooleanField(default=False, verbose_name='Valider les conditions générales de vente')),
                ('is_paid', models.BooleanField(default=False, verbose_name='A été payée')),
                ('payment_status', models.CharField(blank=True, max_length=250, verbose_name='Status du paiement')),
                ('payment_auth_code', models.CharField(blank=True, max_length=250, verbose_name="Code 'authorisation")),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Commande',
                'verbose_name_plural': 'Commandes',
            },
        ),
        migrations.CreateModel(
            name='OrderCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True, verbose_name='date')),
                ('status', models.CharField(blank=True, max_length=500, verbose_name='panier')),
                ('total', models.IntegerField(blank=True, default=0, null=True, verbose_name='Total')),
            ],
            options={
                'verbose_name': 'Panier',
                'verbose_name_plural': 'Paniers',
            },
        ),
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='easycheckout.BaseAddress')),
            ],
            options={
                'verbose_name': 'Billing Address',
                'verbose_name_plural': 'Billing Addresses',
            },
            bases=('easycheckout.baseaddress',),
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='easycheckout.BaseAddress')),
            ],
            options={
                'verbose_name': 'Shipping Address',
                'verbose_name_plural': 'Shipping Addresses',
            },
            bases=('easycheckout.baseaddress',),
        ),
        migrations.AddField(
            model_name='itemcart',
            name='order_cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='easycheckout.OrderCart', verbose_name='Commande'),
        ),
        migrations.AddField(
            model_name='itemcart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simpleproduct.Product', verbose_name='Produit'),
        ),
        migrations.AddField(
            model_name='item',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='easycheckout.Order', verbose_name='Commande'),
        ),
        migrations.AddField(
            model_name='item',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simpleproduct.Product', verbose_name='Produit'),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='easycheckout.BillingAddress', verbose_name='Adresse de facturation'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='easycheckout.ShippingAddress', verbose_name='Adresse de livraison*'),
        ),
    ]
