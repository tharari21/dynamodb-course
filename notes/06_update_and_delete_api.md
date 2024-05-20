Dynamo does not allow bulk updates/deletes.

Must provide key attributes to identify the item you want to delete
Can use `ConditionExpression` with update/delete. This will only update/delete if condition expression is evaluated to true on the item

If you pass the condition expression to a delete let's say, request goes to request router, which forwards to appropriate partition. In the partition the record that matches the PK or PK/SK in composite key table will be fetched. Once it has the item, the partition will then evaluate the condition expression and if true it will delete the item from partition storage

So UpdateItem and DeleteItem require Primary key for the item and can only update/delete one item at a time
optionally can pass condition expression to be evaluated before update/delete 