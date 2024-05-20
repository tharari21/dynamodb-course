DynamoDB is running behind the scenes on hundreds of thousands of hidden EC2 instances in each region managed by AWS engineers.
Each ec2 instance hosts a large number partitions. Each partitions stores items from different customers (customer does not get an entire ec2 instance dedicated to them - they share hardware with other customers). The data you write to dynamo is sharded across partitions. To determine which partition data is written to, dynamo hashes the partition key of the item you write.

max item size is 400kb
max partition size is 10GB
max RCU for partition is 3000 RCU = 3000 Strongly consistent reads of 4KB per second or 6,000 eventually consistent reads of 4KB per second
max WCU for partition is 1000 WCU = 1000 writes of 1KB chunks per second

## API
Maximum 1MB of items retrieval 
If response is greater than 1MB then `LastEvaluatedKey` attribute will appear in response and you'll need to send additional request with the key to get the next "page". Works like pagination.

By default these requests use eventually consistent reads (reads from any partition not necessarily the primary so data may be stale)

Behind the scenes dynamo uses **Request Router** which handles routing your requests to the correct partition. For instance if I send a GetItem where pk=tomer, the request router checks the table metadata for the mapping between the value of the hash function applied against "tomer" and the partition those items live on. IT gets the partition from there and then it knows where to forward request to. When request hits partition, the partition then applies the "selection criteria" if any (the expression you pass for the sort key, if there is one) - this gathers the items in the partition that match selection criteria. Then filter (if specified) is applied to those items and after that, the projections (if specified) are applied to filtered items and the final result is returned to user

Filter expressions apply to key and non-key attributes and can only be used with Query and Scan

### PutItem
Create or update record. If item with the same PK or PK/SK in event of compose primary key table exists, then it will simply update by default unless you specify a `ConditionExpression`. A condition expression is evaluated before the write operation and only carries out the write operation if the condition is evaluated to true. In this case we can specify the `attribute_not_exists(PK)` where PK is the partition key column - this will make sure the item you're trying to add's partition key does not already exist in the table before it creates it. If it does exist then expression will return false and create won't occur and a ConditionalCheckFailedException occurs

`BulkWriteItem` uses multiple `PutItem`s behind the scenes and is more efficient than `PutItem`

### GetItem
Get single item by pk on a simple primary key table or by pk and sk in a composite primary key table.

`BulkGetItem` runs multiple `GetItem`s behind the scenes but it's more efficient. Returns object of failed gets if there are any so process those in application.

### Query
Get single item by partition key in a simple primary key table or get item collection by partition key in a composite primary key table. Must contain partition key equality expression then you can optionally specify sort key condition (for example `begins_with("...")`) The key expression you pass to Query is known as `key condition expression`. Key condition expression only applies to Query
To include sort key expression must use AND keyword after PK equality check

example:
```bash
Key Condition Expression: PK = :pk AND SK = :sk
Expression Attribute Values:pk = "A", :sk = 1
```
Sort key operators:
`#sortKeyName = :sortKeyVal`
`#sortKeyName < :sortKeyVal`
`#sortKeyName > :sortKeyVal`
`#sortKeyName <= :sortKeyVal`
`#sortKeyName >= :sortKeyVal`
`#sortKeyName BETWEEN :sortKeyVal1 AND :sortKeyVal2`
`#begins_with(sortKeyName, :sortKeyValue)` (can't be used with numbers)


### Scan
Reads all items from all partitions in table or in index. DynamoDB uses a single process to read all items from all partititons
The way it works is when you send a scan request, dynamo gets all items from one partition and returns it then retrieves all items on partition 2 and returns it and on and on until all partitions are read

For tables with a large number of items, performance is not good. For that reason Dynamo supports **parallel scan**.
A parallel scan reads items from N partitions in parallel. N is a number you specify. If N is 2 dynamo will launch 2 threads where each thread will run in parallel with others and retrieve data from a partition. This increases performance when running scan


#### Filter
Applies to key and non-key attributes. Can be used with only Query and Scan. Performance and cost depends on size of `ScannedCount` (the number of items scanned before filter was applied). Best practice to use Key condition expression wherever possible and use filter only as needed

## Update/Delete
UpdateItem and DeleteItem require Primary key (PK for simple key table and PK + SK for composite key table) for the item and can only update/delete one item at a time
optionally can pass condition expression to be evaluated before update/delete 

### UpdateItem
Requires `UpdateExpression` to tell dynamo how it should modify non-key attribute/s of item
If item is not found, by default, item is created. If you want to avoid this, include `ConditionExpression`

#### `UpdateExpression`
Defines actions/values for one or more attributes to be updated.
4 types of expressions:
- `[SET action, [, action]]`
     - updates attribute if attribute exists on item, otherwise it creates it. 
     - For attributes of type number, you can perform additions/subtractions on the attribute value (increment/decrement)  e.g. `SET attribValue = attribValue + 1`
     - Can use `if_not_exists(path, operand)` to avoid overwriting an attribute that may be present in the item (only update attribute if it does not exist on item)
     - Can use `list_append(operand,operand)` to add item to attribute of type list
- `[REMOVE action, [, action]]`
    - removes one or more attributes from item
- `[ADD action, [, action]]`
    - Adds attribute if it does not exist. 
        Otherwise it depends on the attribute's data type:
        If type is number, mathematical addition to the current attribute's value (e.g. we `ADD 5` and current val is 1, then new value is 6)
        if ttype is Set, ADD will add elements to attribute value (the arg you pass to ADD must be a set if attribute you're modifying is a set or you get error)
        If not number or set then attribute will simply get updated with the value you pass to add (e.g. `ADD "Tomer"` for an attribute)
- `[DELETE action, [, action]]`
    - Applies only to Set type attributes. Removes element from set

Expression can contain multiple actions in any order. Each clause/action can appear only once

### DeteletItem
Deletes a single item
Can delete many with `BatchWriteItem` by passing a `DeleteRequest`