from rest_framework.views import exception_handler as _exception_handler


def exception_handler(exc, context):
    response = _exception_handler(exc, context)

    # print(exc.get_codes())

    # if response is not None:
    #     response.data = {
    #         "status_code": response.status_code,
    #         "data": response.data,
    #         "codes": exc.get_codes(),
    #     }

    return response
