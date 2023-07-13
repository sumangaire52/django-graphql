import graphene
from graphene_django import DjangoObjectType
# from graphene_django.forms.mutation import DjangoModelFormMutation
# from django import forms
# from graphene_django.rest_framework.mutation import SerializerMutation
# from rest_framework import serializers

from .models import Category, Blog


class CategoryObjectType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "title", "blogs")


class BlogObjectType(DjangoObjectType):
    class Meta:
        model = Blog
        fields = ("id", "title", "category", "author", "content", "created_at", "updated_at",)


class BlogInputType(graphene.InputObjectType):
    title = graphene.String(required=True)
    category_ids = graphene.List(graphene.ID, required=True)
    author_id = graphene.ID(required=True)
    content = graphene.String(required=True)


class BlogMutation(graphene.Mutation):
    class Arguments:
        pk = graphene.ID(required=False)
        blog_data = BlogInputType(required=True)

    blog = graphene.Field(BlogObjectType)

    @classmethod
    def mutate(cls, root, info, blog_data, pk=None):
        # pop the category_ids as we can't directly use it
        category_ids = blog_data.pop("category_ids")
        # if we get the pk that means we need to perform update
        if pk:
            try:
                blog = Blog.objects.get(pk=pk)
            except Blog.DoesNotExist:
                return None
            for attr, value in blog_data.items():
                setattr(blog, attr, value)
        else:
            blog = Blog(**blog_data)
        blog.save()
        # assign categories
        for category_id in category_ids:
            blog.category.add(category_id)
        return BlogMutation(blog=blog)

# class BlogForm(forms.ModelForm):
#     class Meta:
#         model = Blog
#         fields = ("title", "category", "author", "content",)
#
#
# class BlogMutation(DjangoModelFormMutation):
#     blog = graphene.Field(BlogObjectType)
#
#     class Meta:
#         form_class = BlogForm
#         input_field_name = "blog_data"
#
# class BlogSerializer(serializers.ModelSerializer):
#     category = serializers.ListField(child=serializers.IntegerField())
#
#     class Meta:
#         model = Blog
#         fields = ("id", "title", "category", "author", "content",)
#
#
# class BlogMutation(SerializerMutation):
#     blog = graphene.Field(BlogObjectType)
#
#     class Meta:
#         serializer_class = BlogSerializer


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryObjectType)
    blogs = graphene.List(BlogObjectType)
    category_by_id = graphene.Field(CategoryObjectType, pk=graphene.Int())
    blog_by_id = graphene.Field(BlogObjectType, pk=graphene.Int())

    @staticmethod
    def resolve_categories(root, info):
        return Category.objects.all()

    @staticmethod
    def resolve_blogs(root, info):
        return Blog.objects.all()

    @staticmethod
    def resolve_category_by_id(root, info, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def resolve_blog_by_id(root, info, pk):
        try:
            return Blog.objects.get(pk=pk)
        except Blog.DoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    create_or_update_blog = BlogMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
