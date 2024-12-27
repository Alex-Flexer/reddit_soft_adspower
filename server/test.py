def calc_full_price(amount: int) -> int:
        prefix_prices = [18, 34, 48, 60]
        if amount <= 10:
            return amount * 20
        if amount > 10:
            return 100 + prefix_prices[min(3, amount - 11)] + max(0, amount - 14) * 12


for i in range(1, 20):
    print(f"{i}: {calc_full_price(i)}")