

class TestSubstance:

    def test_get_price_for_tick(self, reps):
        subst = reps.substances['uranium']
        assert subst.get_price_for_tick(0) == 5000000
        prev_price = 5000000
        for i in range(1, 1000):
            new_price = subst.get_price_for_tick(i)
            assert 0.96 <= new_price - prev_price <= 1.04
            prev_price = new_price

