import pytest

from poe_lib.objects.notes_parser import Note


def test_parsing():

    obj = Note()

    assert not obj.is_valid


def test_valid():

    test_strings = [
        '~b/o 1 chaos',
        'b/o 1 chaos',

    ]

    for test_string in test_strings:
        obj = Note(test_string)
        assert obj.is_valid


def test_values():

    obj = Note('~b/o 1 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(1)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('~b/o 1/2 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(0.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('~b/o 1./2 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(0.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('~b/o 10/20 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(0.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('b/o 1.5 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(1.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('price 1.5 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(1.5)
    assert obj.type == 'price'
    assert obj.unit == 'Chaos Orb'

    obj = Note('b/0 1.5 chaos')
    assert obj.is_valid
    assert obj.value == pytest.approx(1.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('b/0 1.5 chaos-orb')
    assert obj.is_valid
    assert obj.value == pytest.approx(1.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'

    obj = Note('b/0 1.5 CHAOS')
    assert obj.is_valid
    assert obj.value == pytest.approx(1.5)
    assert obj.type == 'b/o'
    assert obj.unit == 'Chaos Orb'


def test_invalid_values():

    obj = Note('pricees 1.5 chaos')
    assert not obj.is_valid

    obj = Note('pricees 1//4 chaos')
    assert not obj.is_valid

    obj = Note('1.5 chaos')
    assert not obj.is_valid

    obj = Note('price 1//4 chaos')
    assert not obj.is_valid
