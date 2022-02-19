from django.db import models


class Notice(models.Model):
    notice_id = models.CharField(max_length=200)
    notice_number = models.IntegerField(
        verbose_name="Номер извещения",
        unique=True,
    )
    bidd_type = models.CharField(verbose_name="Вид торгов", max_length=200)
    bidd_form = models.CharField(verbose_name="Форма проведения торгов", max_length=200)
    procedure_name = models.CharField(
        verbose_name="Наименование процедуры", max_length=200
    )
    publish_date = models.DateTimeField(verbose_name="Дата публикации")
    etp = models.CharField(verbose_name="Электронная площадка", max_length=200)


class Bidder(models.Model):
    name = models.CharField(verbose_name="Полное наименование", max_length=200)
    inn = models.IntegerField(verbose_name="ИНН")
    kpp = models.IntegerField(verbose_name="КПП")
    orgn = models.IntegerField(verbose_name="ОГРН")
    legalAddress = models.CharField(verbose_name="Юридический адрес", max_length=200)
    actualAddress = models.CharField(verbose_name="Фактический адрес", max_length=200)


class ContactPerson(models.Model):
    fullname = models.CharField(verbose_name="Контактное лицо", max_length=200)
    tel = models.CharField(verbose_name="Телефон", max_length=20)
    email = models.CharField(verbose_name="Адрес электронной почты", max_length=200)


class RightHolder(models.Model):
    bidd_org_is_right_holder = models.BooleanField(
        verbose_name="Организатор торгов является правообладателем имущества"
    )
    name = models.CharField(verbose_name="Полное наименование", max_length=200)
    inn = models.IntegerField(verbose_name="ИНН")
    kpp = models.IntegerField(verbose_name="КПП")
    orgn = models.IntegerField(verbose_name="ОГРН")
    legalAddress = models.CharField(verbose_name="Юридический адрес", max_length=200)
    actualAddress = models.CharField(verbose_name="Фактический адрес", max_length=200)


class Lot(models.Model):
    number = models.IntegerField(verbose_name="Номер лота")
    status = models.CharField(verbose_name="Статус лота", max_length=200)
    name = models.CharField(verbose_name="Наименование лота", max_length=200)
    description = models.CharField(verbose_name="Описание лота", max_length=200)
    price_min = models.FloatField(verbose_name="Начальная цена")
    price_step = models.FloatField(verbose_name="Шаг аукциона")
    deposit = models.FloatField(verbose_name="Размер задатка")
