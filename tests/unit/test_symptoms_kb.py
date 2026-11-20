"""Тесты целостности базы знаний симптомов."""

from diagninten98.knowledge.symptoms import GROUPS, find_group, find_symptom
from diagninten98.strings import LANGS


def test_groups_exist():
    assert len(GROUPS) >= 6


def test_unique_ids():
    group_ids = [g.id for g in GROUPS]
    assert len(group_ids) == len(set(group_ids))
    for group in GROUPS:
        symptom_ids = [s.id for s in group.symptoms]
        assert len(symptom_ids) == len(set(symptom_ids)), group.id
        assert group.symptoms, f"группа {group.id} пуста"


def test_all_names_trilingual():
    for group in GROUPS:
        assert len(group.name) == len(LANGS) and all(group.name)
        for symptom in group.symptoms:
            assert len(symptom.name) == len(LANGS) and all(symptom.name)
            assert symptom.causes, f"симптом {symptom.id} без причин"
            for cause in symptom.causes:
                assert len(cause.name) == len(LANGS) and all(cause.name)


def test_finders():
    assert find_group("power") is not None
    assert find_symptom("power", "dead") is not None
    assert find_symptom("power", "nope") is None
    assert find_group("nope") is None
    assert find_symptom("nope", "dead") is None


def test_symptom_has_prioritized_causes():
    dead = find_symptom("power", "dead")
    assert [c.id for c in dead.causes][:2] == ["usb_port_mech", "m92t36"]
