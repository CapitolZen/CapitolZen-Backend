from capitolzen.groups.models import Group, Page

from django.contrib.auth import get_user_model

from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework.validators import UniqueValidator

from config.serializers import BaseInternalModelSerializer, RemoteFileField

from capitolzen.organizations.api.app.serializers import OrganizationSerializer
from capitolzen.proposals.models import Bill, Event, Wrapper

from capitolzen.users.utils import token_decode, token_encode
from capitolzen.users.notifications import email_user_password_reset_request
from capitolzen.organizations.models import Organization
from capitolzen.users.models import Action
from capitolzen.users.tasks import generate_user_magic_link
from capitolzen.organizations.services import (
    IntercomOrganizationSync,
    StripeOrganizationSync)

User = get_user_model()


class UserSerializer(BaseInternalModelSerializer):
    """
    Model: User

    """
    organizations = ResourceRelatedField(
        many=True,
        read_only=True,
        source='organizations_organization'
    )

    username = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email address is already in use",
            )]
    )
    avatar = RemoteFileField(required=False)
    organization_role = serializers.SerializerMethodField()

    def get_organization_role(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        if not hasattr(request, 'organization'):
            return None

        organization = request.organization

        if not organization:
            return None

        if organization.is_owner(obj):
            return "Owner"

        if organization.is_admin(obj):
            return "Admin"

        if organization.is_guest(obj):
            return "Guest"

        if organization.organization_users.filter(user=obj):
            return "Member"

        return None

    class Meta:
        model = User
        fields = (
            'id',
            'created',
            'modified',
            'name',
            'username',
            'is_staff',
            'is_active',
            'is_superuser',
            'organizations',
            'date_joined',
            'avatar',
            'metadata',
            'organization_role',
            'features',
            'notification_preferences'
        )
        read_only_fields = (
            'id',
            'is_staff',
            'is_superuser',
            'organizations',
            'date_joined',
        )
        lookup_field = 'id'


class RegistrationSerializer(serializers.Serializer):
    """
    User registration serializer. Creates a user and an org.
    """

    # User Fields
    name = serializers.CharField()
    username = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email address is already in use",
            )]
    )
    confirm_password = serializers.CharField()
    password = serializers.CharField()

    # Organization Fields
    organization_name = serializers.CharField()

    def validate(self, data):
        """
        TODO: We're currently passing org data into the user serializer model.
        This might cause conflicts. Consider doing something smarter.
        :param data:
        :return:
        """
        #
        # User Validation

        # Perform server side validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Password and Confirm Password should be the same'
            )

        user_serializer = UserSerializer(data=data)
        user_serializer.is_valid(raise_exception=True)

        organization_data = {
            'name': data['organization_name']
        }

        organization_serializer = OrganizationSerializer(data=organization_data)
        organization_serializer.is_valid(raise_exception=True)

        data['user_serializer'] = user_serializer
        data['organization_serializer'] = organization_serializer

        return data

    def save(self, **kwargs):
        user_serializer = self.validated_data['user_serializer']
        organization_serializer = self.validated_data['organization_serializer']

        #
        # Make the user first
        user_serializer.save()
        user = user_serializer.instance
        user.set_password(self.validated_data['password'])
        user.save()

        #
        # Do organization things
        organization_serializer.save()
        organization = organization_serializer.instance
        organization.add_user(user)

        #
        # Holy shit this is real frustrating that I can't do this any other way...
        # Lets see here...
        # 1) Can't just let the normal celery tasks handle this because
        #    We save the org so many times we get duplicate tasks trying to create
        #    Multiple resources
        #
        # 2) Can't use kwargs.created in a signal because the owner hasn't been added
        #    to the organization at that point (until we run organization.add_user
        #    and we can't do that until we create, because we need an organization id.

        # Intercom
        IntercomOrganizationSync().execute(organization, "create_or_update")

        # Stripe
        StripeOrganizationSync().execute(organization, "create_or_update")

        return True

    class Meta:
        model = User


class ResetPasswordRequestSerializer(serializers.Serializer):
    """
    Request a new password. Sends an email.
    """
    email = serializers.EmailField()

    def save(self, **kwargs):
        # We don't want to expose that a user may or may not exist
        # Using the password reset form. So we load the user during save
        # and fail silently if we can't find it.
        try:
            user = User.objects.get(username=self.validated_data['email'])
        except User.DoesNotExist:
            return True

        #
        # Again, don't tell the requestor anything about the
        # permissions of the user.
        if user.is_staff or user.is_superuser:
            return True

        # Check to make sure the user isn't _only_ a guest and actually belongs to an org
        orgs = Organization.objects.filter(organization_users=user)
        org_count = orgs.count()
        if org_count < 1:
            return True

        # This is pretty confusing. but if the user is only a guest user, we don't allow them to reset their password.
        is_not_guest = False
        for org in orgs:
            if not org.is_guest(user):
                is_not_guest = True

        if not is_not_guest:
            return True
        token = token_encode(user, action='reset_password')
        email_user_password_reset_request(user.username, token=token)
        return True

    class Meta:
        model = User


class ResetPasswordSerializer(serializers.Serializer):
    """
    Updates password based on token and new password.
    """
    token = serializers.CharField()
    confirm_password = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        # Perform server side validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Password and Confirm Password should be the same'
            )

        payload = token_decode(data['token'])
        if not payload:
            raise serializers.ValidationError("Unable to decode token")

        if payload.get('action') != 'reset_password':
            raise serializers.ValidationError("Invalid Token")

        data['token_payload'] = payload

        try:
            user = User.objects.get(username=payload['username'])
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Unable to load user")

        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()

        return {
            'email': user.username
        }

    class Meta:
        model = User


class ChangePasswordSerializer(serializers.Serializer):
    """
    When a user is logged in, allow them to change their own password
    """
    current_password = serializers.CharField()
    confirm_password = serializers.CharField()
    password = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.get_queryset()
    )

    def validate(self, data):
        # Check current password
        if not data['user'].check_password(data['current_password']):
            raise serializers.ValidationError(
                'Current password is not correct'
            )

        # Perform server side validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Password and Confirm Password should be the same'
            )

        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return True

    class Meta:
        model = User


class ChangeUserStatusSerializer(serializers.Serializer):
    """
    TODO: Can we merge this with the actual UserSerializer?
    """
    status = serializers.BooleanField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.get_queryset()
    )

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.is_active = self.validated_data['status']
        user.save()
        return True

    class Meta:
        model = User


class ChangeUserOrganizationRoleSerializer(serializers.Serializer):
    """
    TODO: Can we merge this with the actual UserSerializer?
    A: I dunno, but i doubled down in the next serializer
    """
    role = serializers.ChoiceField(
        choices=['Member', 'Admin']
    )

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.get_queryset()
    )

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.get_queryset()
    )

    def save(self, **kwargs):
        role = self.validated_data['role']
        user = self.validated_data['user']
        organization = self.validated_data['organization']
        org_user, _ = organization.get_or_add_user(user)

        if role == "Admin":
            org_user.is_admin = True
        else:
            org_user.is_admin = False
        org_user.save()

        return True

    class Meta:
        model = User


class GuestUserCreateSerializer(serializers.Serializer):
    """
    TODO: Matt rewrite with gin
    """
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.get_queryset(),
        many=False
    )

    email = serializers.EmailField()
    name = serializers.CharField()

    # I don't know why, but setting this to be a pk related field errors...
    page = serializers.PrimaryKeyRelatedField(
        queryset=Page.objects.all(),
        many=False
    )

    def save(self, **kwargs):
        email = self.validated_data['email']
        user, created = User.objects.get_or_create(username=email)
        if created:
            user.name = self.validated_data['name']

        organization = self.validated_data['organization']
        org_user, _ = organization.get_or_add_user(user)
        org_user.is_guest = True
        org_user.is_admin = False

        user.save()
        org_user.save()
        page = self.validated_data['page']
        page.viewers.add(user)
        page.save()
        return user

    class Meta:
        model = User
        fields = (
            'name',
            'group'
        )


class GuestLoginRequestSerializer(serializers.Serializer):
    page = serializers.PrimaryKeyRelatedField(
        queryset=Page.objects.all(),
        many=False
    )
    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data['email']
        page = self.validated_data['page']
        group = page.group

        try:
            user = User.objects.get(username=email)
            if group.is_guest(user):
                generate_user_magic_link.delay(user_id=str(user.id), page_id=str(page.id))
            return True
        except Exception:
            # ToDo: Probably add some sort of instrumentation here
            return True

    class Meta:
        model = User
        fields = (
            'name',
            'group'
        )


class ActionSerializer(BaseInternalModelSerializer):
    user = ResourceRelatedField(
        many=False,
        queryset=User.objects,
    )

    bill = ResourceRelatedField(
        many=False,
        queryset=Bill.objects,
        allow_null=True
    )

    wrapper = ResourceRelatedField(
        many=False,
        queryset=Wrapper.objects,
        allow_null=True
    )

    event = ResourceRelatedField(
        many=False,
        queryset=Event.objects,
        allow_null=True
    )

    included_serializers = {
        'user': UserSerializer,
        'bill': 'capitolzen.proposals.api.app.serializers.BillSerializer',
        'event': 'capitolzen.proposals.api.app.serializers.EventSerializer',
        'wrapper': 'capitolzen.proposals.api.app.serializers.WrapperSerializer',
    }

    class Meta:
        model = Action
        fields = (
            'id',
            'user',
            'state',
            'title',
            'priority',
            'created',
            'bill',
            'event',
            'wrapper'
        )

    class JSONAPIMeta:
        included_resources = ['bill', 'event', 'wrapper', 'wrapper.group', 'wrapper.bill',
                              'bill.sponsor', 'bill.current_committee']
