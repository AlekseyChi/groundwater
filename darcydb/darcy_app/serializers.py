# from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import DictEntities, WellsDepression, WellsEfw, WellsRegime, WellsWaterDepth

# , WellsRate


class WellsWaterDepthSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellsWaterDepth
        fields = ["water_depth"]


class TypeEfwSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictEntities
        fields = ["id", "name"]


class PumpTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictEntities
        fields = ["id", "name"]


class WellsRegimeSerializer(serializers.ModelSerializer):
    water_depth = WellsWaterDepthSerializer(many=False, required=True, write_only=True)

    class Meta:
        model = WellsRegime
        fields = ["well", "date", "water_depth"]

    def create(self, validated_data):
        water_depth_data = validated_data.pop("water_depth", None)
        wells_regime = WellsRegime.objects.create(**validated_data)
        if water_depth_data:
            wells_regime.waterdepths.create(**water_depth_data)
        return wells_regime


class WellsDepressionSerializer(serializers.ModelSerializer):
    water_depth = WellsWaterDepthSerializer(many=False, required=True, write_only=True)

    class Meta:
        model = WellsDepression
        fields = ["time_measure", "water_depth"]


class WellsEfwSerializer(serializers.ModelSerializer):
    # water_depth = WellsWaterDepthSerializer(many=False)
    depressions = WellsDepressionSerializer(many=True, write_only=True)
    type_efw = TypeEfwSerializer(read_only=True)
    pump_type = PumpTypeSerializer(read_only=True)

    class Meta:
        model = WellsEfw
        fields = ["well", "date", "type_efw", "pump_type", "pump_depth", "pump_time", "doc", "depressions"]

    def create(self, validated_data):
        depressions = validated_data.pop("depressions", None)
        efw = WellsEfw.objects.create(**validated_data)
        if depressions:
            for depression in depressions:
                water_depth = depression.pop("water_depth", None)
                if water_depth:
                    depression_instance = WellsDepression.objects.create(efw_id=efw, **depression)
                    depression_instance.waterdepths.create(**water_depth)

        return efw
