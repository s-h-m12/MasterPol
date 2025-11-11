from django.db import models

# Модель Региона
class Regions(models.Model):
    region_name = models.CharField(max_length=100)

# Модель Города
class Cities(models.Model):
    city_name = models.CharField(max_length=100)
    region = models.ForeignKey(Regions, on_delete=models.CASCADE)

# Модель Улицы
class Streets(models.Model):
    street_name = models.CharField(max_length=100)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE)

# Модель Адреса
class Address(models.Model):
    postal_code = models.CharField(max_length=10)
    street = models.ForeignKey(Streets, on_delete=models.CASCADE)
    house = models.CharField(max_length=10)

# Модель-справочник типа продукта
class ProductType(models.Model):
    type_name = models.CharField(max_length=100)
    coefficient = models.DecimalField(max_digits=5, decimal_places=2)

# Модель-справочник типа материала
class MaterialType(models.Model):
    material_type_name = models.CharField(max_length=100)
    defect_percentage = models.DecimalField(max_digits=5, decimal_places=4)

# Модель Продукта
class Products(models.Model):
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    article = models.CharField(max_length=50)
    min_partner_price = models.DecimalField(max_digits=10, decimal_places=2)
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, null=True, blank=True)

# Модель Партнера
class Partners(models.Model):
    # Предопределенные значения для типов организаций
    PARTNER_TYPES = [
        ('ЗАО', 'ЗАО'),
        ('ООО', 'ООО'),
        ('ПАО', 'ПАО'),
        ('ОАО', 'ОАО'),
    ]

    partner_type = models.CharField(max_length=10, choices=PARTNER_TYPES)
    partner_name = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    inn = models.CharField(max_length=12)
    rating = models.IntegerField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

# Модель для связи партнера с продуктами (продажи)
class PartnerProducts(models.Model):
    partner = models.ForeignKey(Partners, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sale_date = models.DateTimeField()