from datetime import datetime

from rest_framework import serializers

from django_popularity.models import DateGraphPoint, Popularity, Standard


class DateGraphPointSerializer(serializers.ModelSerializer):
    days_ago = serializers.SerializerMethodField()

    class Meta:
        model = DateGraphPoint
        fields = (
            'date',
            'value',
            'days_ago',
        )

    def get_days_ago(self, obj):
        return (datetime.today().date() - obj.date).days


class StandardSerializer(serializers.ModelSerializer):
    graph_data = serializers.SerializerMethodField()

    class Meta:
        model = Standard
        fields = (
            'created',
            'updated',
            'geo',
            'title',
            'graph_data',
        )

    def get_graph_data(self, obj):
        return DateGraphPointSerializer(obj.graph.date_points.all(), many=True).data


class PopularitySerializer(serializers.ModelSerializer):
    graph_data = serializers.SerializerMethodField()
    standard = StandardSerializer()
    standard2 = StandardSerializer()

    class Meta:
        model = Popularity
        fields = (
            'created',
            'updated',
            'geo',
            'title',
            'graph_data',
            'standard',
            'standard2',
        )

    def get_graph_data(self, obj):
        return DateGraphPointSerializer(obj.graph.date_points.all(), many=True).data
