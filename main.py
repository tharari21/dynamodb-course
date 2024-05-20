import boto3
from botocore.exceptions import ClientError

ERROR_HELP_STRINGS = {
    # Operation specific errors
    'TransactionCanceledException': 'Transaction Cancelled, implies a client issue, fix before retrying',
    'TransactionInProgressException': 'The transaction with the given request token is already in progress, consider changing retry strategy for this type of error',
    'IdempotentParameterMismatchException': 'Request rejected because it was retried with a different payload but with a request token that was already used,' +
                                            'change request token for this payload to be accepted',
    # Common Errors
    'InternalServerError': 'Internal Server Error, generally safe to retry with exponential back-off',
    'ProvisionedThroughputExceededException': 'Request rate is too high. If you\'re using a custom retry strategy make sure to retry with exponential back-off.' +
                                              'Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index',
    'ResourceNotFoundException': 'One of the tables was not found, verify table exists before retrying',
    'ServiceUnavailable': 'Had trouble reaching DynamoDB. generally safe to retry with exponential back-off',
    'ThrottlingException': 'Request denied due to throttling, generally safe to retry with exponential back-off',
    'UnrecognizedClientException': 'The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying',
    'ValidationException': 'The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying',
    'RequestLimitExceeded': 'Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying',
}

# Use the following function instead when using DynamoDB local
#def create_dynamodb_client(region):
#    return boto3.client("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")

def create_dynamodb_client(region="us-east-1"):
    return boto3.client("dynamodb", endpoint_url='http://localhost:8000', region_name=region)


def create_transact_get_items_input():
    return {
        "TransactItems": [
            {
                "Get": {
                    "TableName": "Employee",
                    "Key": {
                        "LoginAlias": {"S":"tomerh"}
                    }
                }
            }
        ]
    }

def create_update_item_input(dynamodb_client, **input):
    try:
        dynamodb_client.update_item(**input)
    except ClientError as error:
        handle_error(error)
    except BaseException as Error:
        print("Unknown error executing TransactGetItem operation: " +
              error.response['Error']['Message'])

def execute_transact_get_items(dynamodb_client, input):
    try:
        response = dynamodb_client.transact_get_items(**input)
        print("TransactGetItems executed successfully.")
        for item in response["Responses"]:
            print(item)
        # Handle response
    except ClientError as error:
        handle_error(error)
    except BaseException as error:
        print("Unknown error executing TransactGetItem operation: " +
              error.response['Error']['Message'])


def handle_error(error):
    error_code = error.response['Error']['Code']
    error_message = error.response['Error']['Message']

    error_help_string = ERROR_HELP_STRINGS[error_code]

    print('[{error_code}] {help_string}. Error message: {error_message}'
          .format(error_code=error_code,
                  help_string=error_help_string,
                  error_message=error_message))


def main():
    # Create the DynamoDB Client with the region you want
    dynamodb_client = create_dynamodb_client()
    # print(dynamodb_client.list_tables())

    # Create the dictionary containing arguments for transact_get_items call
    transact_get_items_input = create_transact_get_items_input()

    # Call DynamoDB's transact_get_items API
    execute_transact_get_items(dynamodb_client, transact_get_items_input)


if __name__ == "__main__":
    main()