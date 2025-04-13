bill_items = []

def add_to_bill(item):
    bill_items.append(item)

def remove_from_bill(item):
    bill_items.remove(item)

def clear_bill():
    bill_items.clear()

def get_bill_items():
    return bill_items

def calculate_total():
    return sum(i[1] * i[2] for i in bill_items)
