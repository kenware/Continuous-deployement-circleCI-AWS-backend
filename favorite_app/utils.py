import datetime
from enum import Enum

# core Django import
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import serializers
# local import
from favorite_app.models import FavoriteThings
from favorite_app.constants import constant_messages


def validate_ranking(max_ranking, ranking):
    """
    validate that ranking is within a range of sequence within a category
    Parameters:
        max_ranking: max_ranking in a category
        ranking: incoming ranking to be updated
    """
    if ranking > (max_ranking + 1):
        raise serializers.ValidationError({
            'ranking': [
                'ranking out of range',
                f'The next valid ranking is in this category is {max_ranking + 1} or less'
            ]
        })


def re_order_ranking(validated_data, request, action, *args, **kwargs):
    """
    re_order ranking such that ranking does not repeat when a new favorite
    things is added within a category during POST, UPDATE AND DELETE

    Parameters:
        validated_data: validated data from the request
        request: request object
    """
    caterory_id_from_arg = args
    ranking = validated_data.get('ranking')
    category_id = request.data.get('category', None) or caterory_id_from_arg

    max_ranking = FavoriteThings.objects.filter(
        category_id=category_id).order_by('-ranking').first()

    if max_ranking:
        validate_ranking(max_ranking.ranking, int(ranking))
    else:
        validate_ranking(0, int(ranking))

    upper_favorite_things = FavoriteThings.objects.filter(
        ranking__gte=ranking, category_id=category_id)

    # re-order on delete or creation
    for favorite_thing in upper_favorite_things:
        if action == 'create':
            favorite_thing.ranking += 1
        elif action == 'delete':
            favorite_thing.ranking -= 1
        favorite_thing.save()

    # re-order on update
    if action == 'update':
        instance_ranking = kwargs['instance_ranking']
        ranking_lte = ranking if int(
            ranking) > instance_ranking else instance_ranking
        ranking_gte = instance_ranking if int(
            ranking) > instance_ranking else ranking
        lower_favorite_things = FavoriteThings.objects.filter(
            ranking__lte=ranking_lte,
            ranking__gte=ranking_gte,
            category_id=category_id)
        validate_ranking((max_ranking.ranking - 1), int(ranking))

        for favorite_thing in lower_favorite_things:
            if int(ranking) > instance_ranking:
                favorite_thing.ranking -= 1
            else:
                favorite_thing.ranking += 1
            favorite_thing.save()


def metadata_log(initial_data, new_metatada):
    """
    Generate audit log when during update on favorite things on metadata

    Parameters:
        initial_data: existing favoriteThings metadata to be updated
        new_metatada: Incoming(new) FavoriteThings metadata
    Returns:
        logs for metadata
    """
    messages = []
    for key, value in initial_data.items():
        new_value = new_metatada.get(key)
        if new_value:
            if new_value != value:
                messages.append(
                    constant_messages['meta_property_not_equall'].format(
                        key, value, new_value))
        else:
            messages.append(
                constant_messages['meta_property_removed'].format(key))
    for key, value in new_metatada.items():
        if key not in initial_data:
            messages.append(
                constant_messages['meta_property_addedd'].format(key))
    return messages


def gnerate_audit_log(instance, data):
    """
    Generate audit log when during update on favorite things

    Parameters:
        instance: existing favoriteThings data to be updated
        data: Incoming(new) FavoriteThings data
    Returns:
        audit log
    """

    initial_data = {
        'title': instance.title,
        'description': instance.description,
        'ranking': instance.ranking
    }
    audit_log = instance.audit_log
    message = []

    for key, value in initial_data.items():
        new_value = data.get(key)
        if new_value and new_value != value:
            message.append(constant_messages[key].format(value, new_value))
    message = message + metadata_log(instance.metadata, data.get('metadata'))
    if len(message):
        log = {
            'message': message,
            'date': f'{timezone.now()}'
        }
        audit_log.append(log)
    return audit_log


def validate_id(id):
    """
    validate an id

    Parameters:
        id: int
    Returns:
        Bool: True
        Response: Bad response
    """
    try:
        int(id)
    except ValueError:
        raise serializers.ValidationError(
            {'status': constant_messages['invalid_id']})
    return True


def check_value_type(key, value):
    """
    validate metadata property
    """

    is_valid = False
    valid_types = [float, complex, str, datetime.date, int, Enum]
    for types in valid_types:
        if isinstance(value, types):
            is_valid = True
    if not is_valid:
        raise serializers.ValidationError(
            constant_messages['invalid_type'].format(key))
