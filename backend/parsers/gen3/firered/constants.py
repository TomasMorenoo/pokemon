# Save file layout
SAVE_SIZE = 0x20000          # 131072 bytes total
SLOT_SIZE = 0x00E000         # 57344 bytes per save slot (14 sections × 4096)
SLOT_A_OFFSET = 0x000000
SLOT_B_OFFSET = 0x00E000

SECTION_SIZE = 0x1000        # 4096 bytes per section
SECTION_DATA_SIZE = 0x0F80   # 3968 bytes of data per section

# Section footer offsets (within a 4096-byte section)
FOOTER_SECTION_ID_OFFSET = 0x0FF4    # u16
FOOTER_CHECKSUM_OFFSET   = 0x0FF6    # u16
FOOTER_SIGNATURE_OFFSET  = 0x0FF8    # u32
FOOTER_SAVE_INDEX_OFFSET = 0x0FFC    # u32
SECTION_SIGNATURE        = 0x08012025

# Section IDs
SECTION_TRAINER_INFO  = 0
SECTION_TEAM_ITEMS    = 1
SECTION_GAME_STATE    = 2
SECTION_MISC_DATA     = 3
SECTION_RIVAL_INFO    = 4
# Sections 5-13: PC Buffer (9 sections × 3968 bytes = 35712 bytes)
SECTION_PC_BUFFER_START = 5
SECTION_PC_BUFFER_END   = 13

# Section 0 (Trainer Info) offsets
TRAINER_NAME_OFFSET     = 0x0000   # 7 bytes
TRAINER_GENDER_OFFSET   = 0x0008   # u8: 0=male 1=female
TRAINER_ID_OFFSET       = 0x000A   # u32: lower 16=public ID, upper 16=secret ID

# Section 1 (Team/Items) offsets
PARTY_COUNT_OFFSET = 0x0034   # u32
PARTY_DATA_OFFSET  = 0x0038   # 6 × 100 bytes

# PC Buffer layout (reconstructed from sections 5-13)
PC_CURRENT_BOX_OFFSET = 0x0000          # u8
PC_BOX_DATA_OFFSET    = 0x0004          # 14 × 30 × 80 bytes
PC_BOX_NAME_OFFSET    = 0x8344          # 14 × 9 bytes
BOX_COUNT    = 14
BOX_CAPACITY = 30
BOX_NAME_LENGTH = 9

# Pokémon structure sizes
PARTY_POKEMON_SIZE = 100   # bytes
BOX_POKEMON_SIZE   = 80    # bytes

# Within a Pokémon structure (offsets from start of Pokémon bytes):
PKM_PID_OFFSET         = 0x00   # u32
PKM_OTID_OFFSET        = 0x04   # u32 (lower 16 = public, upper 16 = secret)
PKM_NICKNAME_OFFSET    = 0x08   # 10 bytes
PKM_LANGUAGE_OFFSET    = 0x12   # u16
PKM_OT_NAME_OFFSET     = 0x14   # 7 bytes
PKM_MARKINGS_OFFSET    = 0x1B   # u8
PKM_CHECKSUM_OFFSET    = 0x1C   # u16
PKM_ENCRYPTED_OFFSET   = 0x20   # 48 bytes (4 × 12-byte substructures)

# Party-only additional data (at offset 0x50 within 100-byte party structure)
PKM_STATUS_OFFSET      = 0x50   # u32
PKM_LEVEL_OFFSET       = 0x54   # u8
PKM_POKERUS_OFFSET     = 0x55   # u8
PKM_CURRENT_HP_OFFSET  = 0x56   # u16
PKM_MAX_HP_OFFSET      = 0x58   # u16
PKM_STAT_ATK_OFFSET    = 0x5A   # u16
PKM_STAT_DEF_OFFSET    = 0x5C   # u16
PKM_STAT_SPE_OFFSET    = 0x5E   # u16
PKM_STAT_SPA_OFFSET    = 0x60   # u16
PKM_STAT_SPD_OFFSET    = 0x62   # u16

# FireRed game code identifier (from ROM header — not in save, detected differently)
GAME_CODE_FIRERED  = b"BPRE"
GAME_CODE_LEAFGREEN = b"BPGE"

# Section 1 (Team/Items) — Bag pockets (FireRed/LeafGreen)
BAG_TM_OFFSET = 0x0464   # 58 TM/HM slots × 4 bytes (u16 item_id + u16 quantity)
BAG_TM_COUNT  = 58
