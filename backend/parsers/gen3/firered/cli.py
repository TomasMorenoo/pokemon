"""CLI tool to validate parser against a real .sav file."""
import sys
import json
from pathlib import Path
from .parser import FireRedParser
from ...base.types import SaveParseError


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m parsers.gen3.firered.cli <save_file.sav>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    data = path.read_bytes()
    parser = FireRedParser()

    try:
        save = parser.parse(data)
    except SaveParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    print(f"=== Trainer: {save.trainer.name} ===")
    print(f"  ID: {save.trainer.trainer_id}  SID: {save.trainer.secret_id}")
    print(f"  Gender: {save.trainer.gender}")
    print(f"\n=== Party ({len(save.party)} Pokémon) ===")
    for pkm in save.party:
        shiny_marker = " ★" if pkm.is_shiny else ""
        print(f"  [{pkm.party_slot}] {pkm.species_name}{shiny_marker} Lv.{pkm.level} ({pkm.nature_name})")
        print(f"      Nickname: {pkm.nickname}  OT: {pkm.ot_name} [{pkm.ot_id}]")
        print(f"      IVs: HP={pkm.ivs.hp} Atk={pkm.ivs.attack} Def={pkm.ivs.defense} "
              f"Spe={pkm.ivs.speed} SpA={pkm.ivs.sp_attack} SpD={pkm.ivs.sp_defense}")
        print(f"      EVs: HP={pkm.evs.hp} Atk={pkm.evs.attack} Def={pkm.evs.defense} "
              f"Spe={pkm.evs.speed} SpA={pkm.evs.sp_attack} SpD={pkm.evs.sp_defense}")
        print(f"      Moves: {', '.join(m.move_name for m in pkm.moves)}")

    total_box = sum(1 for box in save.boxes for pkm in box if pkm is not None)
    print(f"\n=== PC Boxes: {total_box} Pokémon ===")
    for box_num, box in enumerate(save.boxes):
        count = sum(1 for pkm in box if pkm is not None)
        if count > 0:
            print(f"  Box {box_num + 1}: {count} Pokémon")
            for pkm in box:
                if pkm:
                    print(f"    [{pkm.box_slot}] {pkm.species_name} (EXP {pkm.experience})")


if __name__ == "__main__":
    main()
