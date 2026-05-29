from typing import Optional


async def paginate(q, page: int = 1, page_size: int = 25,
                   sort_by: Optional[str] = None,
                   sort_order: Optional[str] = 'desc'):
    """Apply sorting, pagination and return standard response dict."""
    if sort_by:
        order = f'{"-" if sort_order == "desc" else ""}{sort_by}'
        q = q.order_by(order)

    total = await q.count()
    items = await q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'pages': (total + page_size - 1) // page_size,
    }
