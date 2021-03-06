# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.test import TestCase
from model_mommy import mommy

from dashboard.libs.rate_converter import last_date_in_month
from ..constants import COST_TYPES
from ..models import Product, PersonCost, Person, Rate, Task


start_date = date(2017, 1, 1)
month_one_start = start_date  # 21 Days
month_two_start = start_date + relativedelta(months=1)  # 20 Days
today = date(2017, 3, 1)

contractor_rate = Decimal('100')
non_contractor_rate = Decimal('110')
non_contractor_rate_two = Decimal('130')


class ProductCostTestCase(TestCase):
    fixtures = ['test_product_costs.yaml']

    def assertDecimalEqual(self, a, b):
        self.assertEqual(round(a, 2), round(b, 2))

    def setUp(self):
        self.product1 = mommy.make(Product)
        self.product2 = mommy.make(Product)

        self.contractor = mommy.make(Person, is_contractor=True)
        self.non_contractor = mommy.make(Person, is_contractor=False)
        self.non_contractor_two = mommy.make(Person, is_contractor=False)

        mommy.make(
            Rate,
            start_date=start_date,
            rate=contractor_rate,
            person=self.contractor
        )

        mommy.make(
            Rate,
            start_date=start_date,
            rate=non_contractor_rate,
            person=self.non_contractor
        )
        mommy.make(
            PersonCost,
            start_date=month_one_start,
            person=self.non_contractor,
            end_date=last_date_in_month(month_one_start),
            type=COST_TYPES.MONTHLY,
            name='ASLC',
            cost=Decimal('21')
        )
        mommy.make(
            PersonCost,
            start_date=month_one_start,
            person=self.non_contractor,
            end_date=last_date_in_month(month_one_start),
            type=COST_TYPES.MONTHLY,
            name='ERNIC',
            cost=Decimal('42')
        )

        mommy.make(
            Rate,
            start_date=start_date,
            rate=non_contractor_rate_two,
            person=self.non_contractor_two
        )
        mommy.make(
            PersonCost,
            start_date=month_one_start,
            person=self.non_contractor_two,
            end_date=last_date_in_month(month_one_start),
            type=COST_TYPES.MONTHLY,
            name='ASLC',
            cost=Decimal('84')
        )
        mommy.make(
            PersonCost,
            start_date=month_two_start,
            person=self.non_contractor_two,
            end_date=last_date_in_month(month_two_start),
            type=COST_TYPES.MONTHLY,
            name='ASLC',
            cost=Decimal('20')
        )

    def test_product_costs_with_part_time_people(self):
        """
        This tests product costs with multiple people working part time.

        It is quite long but I wanted to test everything together.
        """
        self.assertEqual(
            self.product1.people_costs(month_one_start,
                                       last_date_in_month(month_one_start)),
            Decimal('0'))

        # 1 x 100 = 100
        mommy.make(
            Task,
            person=self.contractor,
            product=self.product1,
            start_date=date(2017, 1, 3),
            end_date=date(2017, 1, 4),
            days=1
        )

        # 1 x (110 + 21/21 + 42/21) = 113
        mommy.make(
            Task,
            person=self.non_contractor,
            product=self.product1,
            start_date=date(2017, 1, 3),
            end_date=date(2017, 1, 4),
            days=1
        )

        # 0.25 x (130 +  84/21) = 33.5
        mommy.make(
            Task,
            person=self.non_contractor_two,
            product=self.product1,
            start_date=date(2017, 1, 3),
            end_date=date(2017, 1, 4),
            days=Decimal('0.25')
        )

        self.assertEqual(
            self.product1.people_costs(month_one_start,
                                       last_date_in_month(month_one_start)),
            Decimal('246.5'))

        self.assertEqual(
            self.product2.people_costs(month_one_start,
                                       last_date_in_month(month_one_start)),
            Decimal('0'))

        # 1 x (110 + 21/21 + 42/21) = 84.75
        mommy.make(
            Task,
            person=self.non_contractor,
            product=self.product1,
            start_date=date(2017, 1, 4),
            end_date=date(2017, 1, 5),
            days=0.75
        )

        self.assertEqual(
            self.product1.people_costs(month_one_start,
                                       last_date_in_month(month_one_start)),
            Decimal('331.25'))

        self.assertEqual(
            self.product1.cost_to(last_date_in_month(month_two_start)),
            Decimal('331.25'))

        self.assertEqual(
            self.product1.total_cost(),
            Decimal('331.25'))

        # 0.5 x (110 + 21/21 + 42/21) = 56.5
        mommy.make(
            Task,
            person=self.non_contractor,
            product=self.product1,
            start_date=date(2017, 2, 1),
            end_date=date(2017, 2, 2),
            days=Decimal('0.5')
        )

        self.assertEqual(
            self.product1.people_costs(month_two_start,
                                       last_date_in_month(month_two_start)),
            Decimal('56.5'))

        self.assertEqual(
            self.product1.people_costs(month_one_start,
                                       last_date_in_month(month_one_start)),
            Decimal('331.25'))

        self.assertEqual(
            self.product1.cost_to(last_date_in_month(month_two_start)),
            Decimal('387.75'))

        self.assertEqual(
            self.product1.total_cost(),
            Decimal('387.75'))

    def test_product_costs_from_fixture(self):
        """
        fixture loaded

        month 10: (21 working days)

        days = 13 (one in 5th task)
        rate =  310
        aditional_costs = 80
        aditional_rate = 80/21

        total = 13 * (310 + 80/21)
        Decimal('4079.52380952380953')


        month 11: (22 working days)

        days = 10 (one in 8th task)
        rate = 290
        aditional_costs = 80
        aditional_rate = 80/22

        total = 10 * (290 + 80/22)
        Decimal('2936.3636363636364')


        month 12: (20 working days)

        days = 10
        rate = 300
        aditional_costs = 80
        aditional_rate = 80/20

        total = 12 * (300 + 80/20)
        Decimal('3040')



        total:

        days = 33

        Decimal('10055.88744588744593')

        """
        product = Product.objects.get(pk=79)

        self.assertDecimalEqual(
            product.stats_between(
                date(2016, 10, 1), date(2016, 10, 31)
            )['total'],
            Decimal('4079.52380952380953'))

        self.assertDecimalEqual(
            product.stats_between(
                date(2016, 11, 1), date(2016, 11, 30)
            )['total'],
            Decimal('2936.3636363636364'))

        self.assertDecimalEqual(
            product.stats_between(
                date(2016, 12, 1), date(2016, 12, 31)
            )['total'],
            Decimal('3040.00'))

        self.assertDecimalEqual(product.total_cost(), Decimal('10055.90'))
