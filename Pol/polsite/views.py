from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from django.db import connection
from .models import Partners, PartnerProducts, Products, Address, Streets, Cities, Regions, ProductType, MaterialType
from .forms import MaterialCalculationForm


def main_page_view(request):
    partners = Partners.objects.all()

    # Рассчитываем скидки для каждого партнера
    partners_with_discounts = []
    for partner in partners:
        # Суммируем общее количество проданной продукции партнером
        total_sales = PartnerProducts.objects.filter(
            partner=partner
        ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        # Рассчитываем скидку на основе общего количества
        discount = calculate_discount(total_sales)

        # Форматируем телефон
        formatted_phone = format_phone(partner.phone)

        partners_with_discounts.append({
            'partner': partner,
            'total_sales': total_sales,
            'discount': discount,
            'formatted_phone': formatted_phone
        })

    # Обработка формы расчета материалов
    calculation_result = None
    if request.method == 'POST' and 'calculate_materials' in request.POST:
        form = MaterialCalculationForm(request.POST)
        if form.is_valid():
            calculation_result = calculate_material_required(
                form.cleaned_data['product_type'].id,
                form.cleaned_data['material_type'].id,
                form.cleaned_data['product_quantity'],
                form.cleaned_data['param1'],
                form.cleaned_data['param2']
            )
    else:
        form = MaterialCalculationForm()

    return render(request, 'mainpage.html', {
        'partners_with_discounts': partners_with_discounts,
        'material_form': form,
        'calculation_result': calculation_result,
        'show_modal': request.method == 'POST' and 'calculate_materials' in request.POST
    })


def calculate_discount(total_sales):
    """Функция расчета скидки на основе общего количества продаж"""
    if total_sales >= 300000:
        return 15
    elif total_sales >= 50000:
        return 10
    elif total_sales >= 10000:
        return 5
    else:
        return 0


def format_phone(phone):
    """Функция форматирования телефона"""
    if not phone:
        return ""

    # Убираем все нецифровые символы
    clean_phone = ''.join(filter(str.isdigit, str(phone)))

    # Форматируем в зависимости от длины
    if len(clean_phone) == 11 and clean_phone.startswith('8'):
        # Формат: 8 (XXX) XXX-XX-XX
        return f"8 ({clean_phone[1:4]}) {clean_phone[4:7]}-{clean_phone[7:9]}-{clean_phone[9:]}"
    elif len(clean_phone) == 11 and clean_phone.startswith('7'):
        # Формат: +7 (XXX) XXX-XX-XX
        return f"+7 ({clean_phone[1:4]}) {clean_phone[4:7]}-{clean_phone[7:9]}-{clean_phone[9:]}"
    elif len(clean_phone) == 10:
        # Формат: +7 (XXX) XXX-XX-XX (без первой 7)
        return f"+7 ({clean_phone[0:3]}) {clean_phone[3:6]}-{clean_phone[6:8]}-{clean_phone[8:]}"
    else:
        # Если не подходит под стандартные форматы, возвращаем как есть
        return phone


def calculate_material_required(product_type_id, material_type_id, product_quantity, param1, param2):
    """
    Метод расчета количества материала, требуемого для производства продукции
    """
    try:
        # Проверяем существование типов продукции и материалов
        product_type = ProductType.objects.get(id=product_type_id)
        material_type = MaterialType.objects.get(id=material_type_id)

        # Проверяем валидность входных данных
        if product_quantity <= 0 or param1 <= 0 or param2 <= 0:
            return -1

        # Рассчитываем количество материала на одну единицу продукции
        material_per_unit = param1 * param2 * float(product_type.coefficient)

        # Рассчитываем общее количество материала без учета брака
        total_material_without_defect = material_per_unit * product_quantity

        # Учитываем процент брака материала
        defect_percentage = float(material_type.defect_percentage)
        total_material_with_defect = total_material_without_defect / (1 - defect_percentage)

        # Округляем до целого числа в большую сторону
        return int(total_material_with_defect) + 1 if total_material_with_defect % 1 > 0 else int(
            total_material_with_defect)

    except (ProductType.DoesNotExist, MaterialType.DoesNotExist, ValueError):
        return -1


def fix_sequence(table_name):
    """Функция для исправления последовательности ID"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT setval('polsite_{table_name}_id_seq', (SELECT MAX(id) FROM polsite_{table_name}))")
    except Exception as e:
        print(f"Ошибка при исправлении последовательности для {table_name}: {e}")


def editadd_page_view(request, partner_id=None):
    # Если передан partner_id - редактирование, иначе - добавление
    partner = None
    if partner_id:
        partner = get_object_or_404(Partners, id=partner_id)

    if request.method == 'POST':
        print("POST запрос получен")

        # Получаем данные из формы
        partner_type = request.POST.get('partner_type')
        partner_name = request.POST.get('partner_name')
        director = request.POST.get('director')
        phone = request.POST.get('phone')
        rating = request.POST.get('rating')
        inn = request.POST.get('inn')
        email = request.POST.get('email')

        # Поля адреса
        region_name = request.POST.get('region_name')
        city_name = request.POST.get('city_name')
        street_name = request.POST.get('street_name')
        house = request.POST.get('house')
        postal_code = request.POST.get('postal_code')

        print(f"Данные формы: {partner_name}, {director}, {phone}")

        # Базовая валидация обязательных полей
        required_fields = [partner_type, partner_name, director, phone, rating, inn, email]
        if not all(required_fields):
            print("Не все обязательные поля заполнены")
            form_data = {
                'partner_type': partner_type or '',
                'partner_name': partner_name or '',
                'director': director or '',
                'phone': phone or '',
                'rating': rating or '',
                'inn': inn or '',
                'email': email or '',
                'region_name': region_name or '',
                'city_name': city_name or '',
                'street_name': street_name or '',
                'house': house or '',
                'postal_code': postal_code or '',
            }
            return render(request, 'editaddpage.html', {
                'partner': partner,
                'form_data': form_data,
                'is_editing': partner_id is not None,
                'error': 'Пожалуйста, заполните все обязательные поля'
            })

        try:
            if partner:
                print("Редактирование существующего партнера")
                # Редактирование существующего партнера
                partner.partner_type = partner_type
                partner.partner_name = partner_name
                partner.director = director
                partner.phone = phone
                partner.rating = int(rating)
                partner.inn = inn
                partner.email = email

                # Обновление адреса
                if partner.address:
                    address = partner.address
                    address.house = house or ''
                    address.postal_code = postal_code or ''

                    # Обновление улицы
                    street = address.street
                    street.street_name = street_name or ''

                    # Обновление города
                    city = street.city
                    city.city_name = city_name or ''

                    # Обновление региона
                    region = city.region
                    region.region_name = region_name or ''

                    region.save()
                    city.save()
                    street.save()
                    address.save()

                partner.save()
                print("Партнер успешно обновлен")
            else:
                print("Создание нового партнера")

                # Исправляем последовательности перед созданием
                fix_sequence('regions')
                fix_sequence('cities')
                fix_sequence('streets')
                fix_sequence('address')
                fix_sequence('partners')

                # Создание нового партнера с новым адресом
                region = Regions(region_name=region_name or 'Не указано')
                region.save()

                city = Cities(city_name=city_name or 'Не указано', region=region)
                city.save()

                street = Streets(street_name=street_name or 'Не указано', city=city)
                street.save()

                address = Address(
                    postal_code=postal_code or '',
                    street=street,
                    house=house or ''
                )
                address.save()

                # Создаем партнера
                partner = Partners(
                    partner_type=partner_type,
                    partner_name=partner_name,
                    director=director,
                    phone=phone,
                    rating=int(rating),
                    inn=inn,
                    email=email,
                    address=address
                )
                partner.save()
                print("Партнер успешно создан")

            return redirect('main_page')

        except Exception as e:
            print(f"Ошибка при сохранении: {str(e)}")
            form_data = {
                'partner_type': partner_type or '',
                'partner_name': partner_name or '',
                'director': director or '',
                'phone': phone or '',
                'rating': rating or '',
                'inn': inn or '',
                'email': email or '',
                'region_name': region_name or '',
                'city_name': city_name or '',
                'street_name': street_name or '',
                'house': house or '',
                'postal_code': postal_code or '',
            }
            return render(request, 'editaddpage.html', {
                'partner': partner,
                'form_data': form_data,
                'is_editing': partner_id is not None,
                'error': f'Ошибка при сохранении: {str(e)}'
            })

    # GET запрос - отображение формы
    print("GET запрос - отображение формы")
    form_data = {}
    if partner:
        form_data = {
            'partner_type': partner.partner_type,
            'partner_name': partner.partner_name,
            'director': partner.director,
            'phone': partner.phone,
            'rating': partner.rating,
            'inn': partner.inn,
            'email': partner.email,
        }

        # Добавляем данные адреса, если они есть
        if partner.address:
            address = partner.address
            form_data['postal_code'] = address.postal_code
            form_data['house'] = address.house
            form_data['street_name'] = address.street.street_name
            form_data['city_name'] = address.street.city.city_name
            form_data['region_name'] = address.street.city.region.region_name

    return render(request, 'editaddpage.html', {
        'partner': partner,
        'form_data': form_data,
        'is_editing': partner_id is not None
    })


def history_page_view(request):
    partner_products = PartnerProducts.objects.select_related('partner', 'product').all()
    return render(request, 'history.html', {'partner_products': partner_products})