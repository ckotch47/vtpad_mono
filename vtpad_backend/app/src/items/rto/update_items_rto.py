from .get_items_rto import ItemsRto


class UpdateItemsRto(ItemsRto):
    subItem: list[ItemsRto]