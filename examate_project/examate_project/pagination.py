from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound,ValidationError
from rest_framework.response import Response
from examate_project import messages

class CustomSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    page_query_param = "page"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        try:
        
            page_number = int(page_number)
        except ValueError:
        # If conversion fails, raise a validation error with error code
            raise ValidationError({"message": messages.P1002, "errorCode": "P1002"})

        try:
            self.page = paginator.page(page_number)
        except Exception:

            msg = {"errorCode": "P10001", "message": "Page out of range"}
            raise NotFound(msg)
    
        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
                "current_page_size": len(data),
                "page_size": self.page_size,
            }
        )
    
class PaginationforExam(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100
