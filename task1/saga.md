
| Этап                  | Тип события  | Название               |
| --------------------- | ------------ | ---------------------- |
| Создание заказа       | domain       | OrderCreated           |
| Резервирование товара | domain       | StockReserved          |
| Ошибка резерва        | failure      | StockReservationFailed |
| Запрос оплаты         | domain       | PaymentRequested       |
| Успешная оплата       | domain       | PaymentSucceeded       |
| Ошибка оплаты         | failure      | PaymentFailed          |
| Запрос возврата       | compensation | RefundRequested        |
| Успешный возврат      | compensation | RefundSucceeded        |
| Освобождение резерва  | compensation | StockReleased          |
| Создание доставки     | domain       | DeliveryRequested      |
| Доставка создана      | domain       | DeliveryCreated        |
| Завершение заказа     | domain       | OrderCompleted         |
| Отмена заказа         | domain       | OrderCancelled         |
