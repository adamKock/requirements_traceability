

class Vehicle:
    def __init__(self, engine, color, make, price):
        self.engine = engine
        self.color = color
        self.make = make
        self.price = price
        
    def set_discount(self, amount ):
        self._discount = amount

    
    def get_price(self):
        if hasattr(self, "_discount"):
            return self.price - (self.price * self._discount)
        else: 
            return self.price

        
b1 = Vehicle("V6", "Red", "Ford", 1000)

print(b1.get_price())
b1.set_discount(0.25)
print(b1.get_price())


