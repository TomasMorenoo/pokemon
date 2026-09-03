# Partidas de tercera generación

Cada juego tiene su enlace de Drive, colección, equipo y mochila. El identificador
de un Pokémon incluye el juego; un intercambio entre partidas no mezcla sus datos.
La opción Todo reúne las colecciones sin deduplicar individuos de juegos distintos.

Sincronizar lee todas las partidas configuradas. Confirmar aplica el conjunto en
una transacción; un archivo inválido o cambiado cancela el conjunto. Los ausentes
se retiran únicamente de su juego. Los registros manuales se conservan.

Las carátulas aparecen después de la primera sincronización, incluso si una
partida queda vacía. Los sprites shiny usan la variante shiny de PokeAPI.

## Referencias de formato y recursos

- [Bloques de guardado de PKHeX](https://github.com/kwsch/PKHeX/tree/master/PKHeX.Core/Saves/Blocks/Gen3): posiciones del equipo y claves de cifrado.
- [Mochilas de PKHeX](https://github.com/kwsch/PKHeX/tree/master/PKHeX.Core/Items/Bags): posiciones de MT/MO y cantidades cifradas.
- [Identificadores internos de especies](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/PKM/Util/Conversion/SpeciesConverter.cs): correspondencia con la Pokédex nacional.
- [Carátulas de Libretro](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts): imágenes de las ediciones originales; marcas e ilustraciones pertenecen a sus titulares.
- [Sprites de PokeAPI](https://github.com/PokeAPI/sprites): variantes normales y shiny.

## Base de datos

Aplicar `alembic -c alembic/alembic.ini upgrade head` dentro del backend antes
de ejecutar esta versión sobre una base existente. Migración actual: 0007.
