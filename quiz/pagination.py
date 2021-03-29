from rest_framework import pagination
from rest_framework.response import Response



# class PaginationWithPageNumber(pagination.PageNumberPagination):
# 	page_size = 1
	
# 	def get_paginated_response(self, data):
# 		return Response({
# 			'count': self.page.paginator.count,
# 			'page_number': self.page.number,
# 			'links': {
# 				'next': self.get_next_link(),
# 				'prev': self.get_previous_link()
# 			},
# 			'results': data,
# 		})


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'current_page_number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'items_per_page': len(self.page),
            'results': data
        })