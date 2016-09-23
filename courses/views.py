from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response

# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response


from . import models
from . import serializers
from .permissions import IsSuperUser


# class ListCreateCourse(APIView):
#     def get(self, request, format=None):
#         courses = models.Course.objects.all()
#         serializer = serializers.CourseSerializer(courses, many=True)  # multiple objects to be serialized
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = serializers.CourseSerializer(data=request.data)  # get serialized data from client
#         serializer.is_valid(raise_exception=True)  # if invalid, throws exception
#         serializer.save()  # updates database
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# using generics to create view with list and create capabilities
class ListCreateCourse(generics.ListCreateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

class RetrieveUpdateDestroyCourse(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

class ListCreateReview(generics.ListCreateAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        # gets the course id supplied in the url and uses it to filter the query set provided to the page
        return self.queryset.filter(course_id=self.kwargs.get('course_pk'))

    # ensure that the review is created for the correct course
    def perform_create(self, serializer):
        course = get_object_or_404(models.Course, pk=self.kwargs.get('course_pk'))
        serializer.save(course=course)

class RetrieveUpdateDestroyReview(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

    # get the current object
    def get_object(self):
        return get_object_or_404(self.get_queryset(), course_id=self.kwargs.get('course_pk'), pk=self.kwargs.get('pk'))


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSuperUser, permissions.DjangoModelPermissions, )  # ingores default permissions and focus on model permissions
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    # decorator allows us to the the route to view the reviews for a specific task
    # without this, the router can only show information on a single course and nothing attached to it
    @detail_route(methods=['get'])
    def reviews(self, request, pk=None):
        #  set pagination manually because it is unaffected by gobal setings
        self.pagination_class.page_size = 1
        #  get all associated records
        reviews = models.Review.objects.filter(course_id=pk)

        # paginate the queryset
        page = self.paginate_queryset(reviews)

        if page is not None:
            serializer = serializers.ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ReviewSerializer(reviews, many=True)
        # course = self.get_object()
        # serializer = serializers.ReviewSerializer(course.reviews.all(), many=True)
        return Response(serializer.data)

# mixins to remove list capability of reviews
class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

# ModelViewSet is actually a bunch of mixins used together. Above by leaving out the 'mixins.ListModelMixin', we don't get functions on all reviews in the api
# class ReviewViewSet(viewsets.ModelViewSet):
#     queryset = models.Review.objects.all()
#     serializer_class = serializers.ReviewSerializer

