from rest_framework_jwt.views import RefreshJSONWebToken
from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer
from rest_framework import serializers



class CZRefreshTokenSerializer(RefreshJSONWebTokenSerializer):
    """
    Need to munge the attributes from attrs['data']['token'] to attrs['token']
    """

    token = serializers.CharField(required=False)
    data = serializers.JSONField()
    def validate(self, attrs):
        attrs['token'] = attrs['data']['token']
        return super(CZRefreshTokenSerializer, self).validate(attrs)


class CZRefreshTokenView(RefreshJSONWebToken):
    serializer_class = CZRefreshTokenSerializer


cz_verify_jwt_token = CZRefreshTokenView.as_view()
