from types import SimpleNamespace

from app.services.sync_service import _measurement_has_changed


def test_move_change_creates_a_new_measurement():
    latest = SimpleNamespace(
        level=20, experience=1000, nickname="FARFETCH'D", hp=50,
        iv_hp=1, iv_attack=2, iv_defense=3, iv_speed=4, iv_sp_attack=5, iv_sp_defense=6,
        ev_hp=0, ev_attack=0, moves=[{"move_id": 64, "move_name": "Picotazo"}],
    )
    pkm = SimpleNamespace(
        level=20, experience=1000, nickname="FARFETCH'D",
        ivs=SimpleNamespace(hp=1, attack=2, defense=3, speed=4, sp_attack=5, sp_defense=6),
        evs=SimpleNamespace(hp=0, attack=0),
        moves=[SimpleNamespace(move_id=64), SimpleNamespace(move_id=15)],
    )

    assert _measurement_has_changed(latest, pkm)


def test_same_moves_do_not_create_a_new_measurement():
    latest = SimpleNamespace(
        level=20, experience=1000, nickname="FARFETCH'D", hp=50,
        iv_hp=1, iv_attack=2, iv_defense=3, iv_speed=4, iv_sp_attack=5, iv_sp_defense=6,
        ev_hp=0, ev_attack=0, moves=[{"move_id": 64}, {"move_id": 15}],
    )
    pkm = SimpleNamespace(
        level=20, experience=1000, nickname="FARFETCH'D",
        ivs=SimpleNamespace(hp=1, attack=2, defense=3, speed=4, sp_attack=5, sp_defense=6),
        evs=SimpleNamespace(hp=0, attack=0),
        moves=[SimpleNamespace(move_id=64), SimpleNamespace(move_id=15)],
    )

    assert not _measurement_has_changed(latest, pkm)
