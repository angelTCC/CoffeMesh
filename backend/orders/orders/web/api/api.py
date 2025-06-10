import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from starlette import status
from starlette.responses import Response

from orders.orders_service.exceptions import OrderNotFoundError
from orders.orders_service.orders_service import OrdersService

from orders.repository.orders_repository import OrdersRepository
from orders.repository.unit_of_work import UnitOfWork

from orders.web.app import app
from fastapi import APIRouter
from orders.web.api.schemas import (
    GetOrderSchema,
    CreateOrderSchema,
    GetOrdersSchema,
)

orders = []

@app.get("/orders", response_model=GetOrdersSchema)
def get_orders(cancelled: Optional[bool] = None, limit: Optional[int] = None):
    '''
    if cancelled is None and limit is None:
        return {"orders": orders}

    query_set = [order for order in orders]

    if cancelled is not None:
        if cancelled:
            query_set = [order for order in query_set if order["status"] == "cancelled"]
        else:
            query_set = [order for order in query_set if order["status"] != "cancelled"]

    if limit is not None and len(query_set) > limit:
        return {"orders": query_set[:limit]}

    return {"orders": query_set}
    '''
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        orders_service = OrdersService(repo)
        results = orders_service.list_orders(limit=limit, cancelled=cancelled)
    return {'orders': [result.dict() for result in results]}


@app.post('/orders', status_code=status.HTTP_201_CREATED)
def create_order(payload: CreateOrderSchema):
    '''
    order = order_details.dict()
    order['id'] = uuid.uuid4()
    order['created'] = datetime.now()
    order['status'] = 'created'
    orders.append(order)
    return order
    '''
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        orders_service = OrdersService(repo)
        order = orders_service.place_order(payload.dict()['order'])
        order = payload.dict()['order']
        for item in order:
            item['size'] = item['size'].value
        order = orders_service.place_order(order)
        unit_of_work.commit()
        return_payload = order.dict()
    return return_payload

@app.get('/orders/{order_id}', response_model=GetOrderSchema)
def get_order(order_id: UUID):
    '''
    for order in orders:
        if order['id'] == order_id:
            return order
    raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')
    '''
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.get_order(order_id=order_id)
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')

@app.put('/orders/{order_id}', response_model=GetOrderSchema)
def update_order(order_id: UUID, order_details: CreateOrderSchema):
    '''
    for order in orders:
        if order['id'] == order_id:
            order.update(order_details.dict())
            return order
    raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')
    '''
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = order_details.dict()['order']
            for item in order:
                item['size'] = item['size'].value
            order = orders_service.update_order( order_id=order_id, items=order )
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException( status_code=404, detail=f'Order with ID {order_id} not found' )


@app.delete('/orders/{order_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_order(order_id: UUID):
    '''
    for index, order in enumerate(orders):
        if order['id'] == order_id:
            orders.pop(index)
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
    raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')
    '''
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            orders_service.delete_order(order_id=order_id)
            unit_of_work.commit()
        return
    except OrderNotFoundError:
        raise HTTPException( status_code=404, detail=f'Order with ID {order_id} not found')


@app.post('/orders/{order_id}/cancel', response_model=GetOrderSchema)
def cancel_order(order_id: UUID):
    '''
    for order in orders:
        if order['id'] == order_id:
            order['status'] = 'cancelled'
            return order
    raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')
    '''
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.cancel_order(order_id=order_id)
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException( status_code=404, detail=f'Order with ID {order_id} not found' )

@app.post('/orders/{order_id}/pay', response_model=GetOrderSchema)
def pay_order(order_id: UUID):
    '''
    for order in orders:
        if order['id'] == order_id:
            order['status'] = 'progress'
            return order
    raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')
    '''
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.pay_order(order_id=order_id)
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException( status_code=404, detail=f'Order with ID {order_id} not found' )