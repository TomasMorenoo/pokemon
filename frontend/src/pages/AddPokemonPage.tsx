import { useNavigate } from 'react-router-dom'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState, useEffect } from 'react'
import { Mars, Venus, Minus } from 'lucide-react'
import { useAddPokemon } from '../hooks/usePokemon'

const NATURES: { en: string; es: string }[] = [
  { en: 'Hardy',   es: 'Fuerte'     },
  { en: 'Lonely',  es: 'Huraña'     },
  { en: 'Brave',   es: 'Osada'      },
  { en: 'Adamant', es: 'Firme'      },
  { en: 'Naughty', es: 'Pícara'     },
  { en: 'Bold',    es: 'Audaz'      },
  { en: 'Docile',  es: 'Dócil'      },
  { en: 'Relaxed', es: 'Plácida'    },
  { en: 'Impish',  es: 'Agitada'    },
  { en: 'Lax',     es: 'Floja'      },
  { en: 'Timid',   es: 'Miedosa'    },
  { en: 'Hasty',   es: 'Activa'     },
  { en: 'Serious', es: 'Seria'      },
  { en: 'Jolly',   es: 'Alegre'     },
  { en: 'Naive',   es: 'Ingenua'    },
  { en: 'Modest',  es: 'Modesta'    },
  { en: 'Mild',    es: 'Afable'     },
  { en: 'Quiet',   es: 'Mansa'      },
  { en: 'Bashful', es: 'Tímida'     },
  { en: 'Rash',    es: 'Alocada'    },
  { en: 'Calm',    es: 'Serena'     },
  { en: 'Gentle',  es: 'Amable'     },
  { en: 'Sassy',   es: 'Grosera'    },
  { en: 'Careful', es: 'Cauta'      },
  { en: 'Quirky',  es: 'Rara'       },
]

function normalize(s: string) {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

const GAMES: { value: string; label: string; gen: string }[] = [
  { value: 'red',              label: 'Rojo',                  gen: 'Gen I'   },
  { value: 'blue',             label: 'Azul',                  gen: 'Gen I'   },
  { value: 'yellow',           label: 'Amarillo',              gen: 'Gen I'   },
  { value: 'gold',             label: 'Oro',                   gen: 'Gen II'  },
  { value: 'silver',           label: 'Plata',                 gen: 'Gen II'  },
  { value: 'crystal',          label: 'Cristal',               gen: 'Gen II'  },
  { value: 'ruby',             label: 'Rubí',                  gen: 'Gen III' },
  { value: 'sapphire',         label: 'Zafiro',                gen: 'Gen III' },
  { value: 'emerald',          label: 'Esmeralda',             gen: 'Gen III' },
  { value: 'firered',          label: 'Rojo Fuego',            gen: 'Gen III' },
  { value: 'leafgreen',        label: 'Verde Hoja',            gen: 'Gen III' },
  { value: 'diamond',          label: 'Diamante',              gen: 'Gen IV'  },
  { value: 'pearl',            label: 'Perla',                 gen: 'Gen IV'  },
  { value: 'platinum',         label: 'Platino',               gen: 'Gen IV'  },
  { value: 'heartgold',        label: 'Oro HeartGold',         gen: 'Gen IV'  },
  { value: 'soulsilver',       label: 'Plata SoulSilver',      gen: 'Gen IV'  },
  { value: 'black',            label: 'Negro',                 gen: 'Gen V'   },
  { value: 'white',            label: 'Blanco',                gen: 'Gen V'   },
  { value: 'black2',           label: 'Negro 2',               gen: 'Gen V'   },
  { value: 'white2',           label: 'Blanco 2',              gen: 'Gen V'   },
  { value: 'x',                label: 'X',                     gen: 'Gen VI'  },
  { value: 'y',                label: 'Y',                     gen: 'Gen VI'  },
  { value: 'omegaruby',        label: 'Rubí Omega',            gen: 'Gen VI'  },
  { value: 'alphasapphire',    label: 'Zafiro Alfa',           gen: 'Gen VI'  },
  { value: 'sun',              label: 'Sol',                   gen: 'Gen VII' },
  { value: 'moon',             label: 'Luna',                  gen: 'Gen VII' },
  { value: 'ultrasun',         label: 'Ultrasol',              gen: 'Gen VII' },
  { value: 'ultramoon',        label: 'Ultraluna',             gen: 'Gen VII' },
  { value: 'letsgopikachu',    label: "Let's Go, Pikachu!",    gen: 'Gen VII' },
  { value: 'letsgoeevee',      label: "Let's Go, Eevee!",      gen: 'Gen VII' },
  { value: 'sword',            label: 'Espada',                gen: 'Gen VIII'},
  { value: 'shield',           label: 'Escudo',                gen: 'Gen VIII'},
  { value: 'brilliantdiamond', label: 'Diamante Brillante',    gen: 'Gen VIII'},
  { value: 'shiningpearl',     label: 'Perla Reluciente',      gen: 'Gen VIII'},
  { value: 'legendsarceus',    label: 'Leyendas: Arceus',      gen: 'Gen VIII'},
  { value: 'scarlet',          label: 'Escarlata',             gen: 'Gen IX'  },
  { value: 'violet',           label: 'Púrpura',               gen: 'Gen IX'  },
]

const GENERATION_REGION: Record<string, string> = {
  'generation-i': 'Kanto', 'generation-ii': 'Johto', 'generation-iii': 'Hoenn',
  'generation-iv': 'Sinnoh', 'generation-v': 'Teselia', 'generation-vi': 'Kalos',
  'generation-vii': 'Alola', 'generation-viii': 'Galar', 'generation-ix': 'Paldea',
}
const VARIANT_LABEL: Record<string, string> = {
  alola: 'Alola', galar: 'Galar', hisui: 'Hisui', paldea: 'Paldea',
  mega: 'Mega', 'mega-x': 'Mega X', 'mega-y': 'Mega Y', gmax: 'Gigantamax',
}
function idFromUrl(url: string): number {
  return parseInt(url.split('/').filter(Boolean).pop()!)
}

const schema = z.object({
  species_id: z.coerce.number().min(1).max(1025),
  species_name: z.string().min(1),
  nickname: z.string().optional(),
  level: z.coerce.number().min(1).max(100),
  nature_name: z.string().optional(),
  gender: z.enum(['M', 'F', 'N', '']).optional(),
  is_shiny: z.boolean().default(false),
  origin: z.string().default('unknown'),
  game: z.string().optional(),
  form_name: z.string().optional(),
  hp: z.coerce.number().optional(),
  attack: z.coerce.number().optional(),
  defense: z.coerce.number().optional(),
  speed: z.coerce.number().optional(),
  sp_attack: z.coerce.number().optional(),
  sp_defense: z.coerce.number().optional(),
})

type FormData = z.infer<typeof schema>

const input = "w-full bg-gray-800 border border-gray-700 focus:border-blue-500 text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"

function ButtonGroup<T extends string>({
  options, value, onChange,
}: { options: { value: T; label: string }[]; value: T; onChange: (v: T) => void }) {
  return (
    <div className="flex border border-gray-700 rounded-xl overflow-hidden">
      {options.map((o, i) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={`flex-1 py-2.5 text-xs font-medium transition-colors ${i > 0 ? 'border-l border-gray-700' : ''} ${
            value === o.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-400">{label}</label>
      {children}
      {error && <p className="text-red-400 text-xs">{error}</p>}
    </div>
  )
}

export default function AddPokemonPage() {
  const navigate = useNavigate()
  const addMutation = useAddPokemon()
  const [lookupError, setLookupError] = useState<string | null>(null)
  const [looking, setLooking] = useState(false)
  const [confirmedId, setConfirmedId] = useState<number | null>(null)

  const { register, handleSubmit, setValue, formState: { errors }, control, watch } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { origin: 'unknown', game: localStorage.getItem('lastGame') ?? '' },
  })

  const speciesId = useWatch({ control, name: 'species_id' })
  const gender = watch('gender') ?? ''
  const origin = watch('origin') ?? 'unknown'
  const isShiny = watch('is_shiny') ?? false
  const currentLevel = watch('level')
  const [natureSearch, setNatureSearch] = useState('')
  const [natureOpen, setNatureOpen] = useState(false)
  const [varieties, setVarieties] = useState<{ label: string; pokemonId: number; formName: string }[]>([])
  const [selectedVariety, setSelectedVariety] = useState(0)
  const [baseStats, setBaseStats] = useState<Record<string, number> | null>(null)

  useEffect(() => {
    const id = Number(speciesId)
    if (!id) {
      setValue('species_name', '')
      setConfirmedId(null)
      setLookupError(null)
      setBaseStats(null)
    }
  }, [speciesId, setValue])

  useEffect(() => {
    if (!baseStats) return
    const lvl = Number(currentLevel)
    if (!lvl || lvl < 1 || lvl > 100) return
    setValue('hp', Math.floor(2 * baseStats.hp * lvl / 100) + lvl + 10)
    setValue('attack', Math.floor(2 * baseStats.attack * lvl / 100) + 5)
    setValue('defense', Math.floor(2 * baseStats.defense * lvl / 100) + 5)
    setValue('sp_attack', Math.floor(2 * baseStats.sp_attack * lvl / 100) + 5)
    setValue('sp_defense', Math.floor(2 * baseStats.sp_defense * lvl / 100) + 5)
    setValue('speed', Math.floor(2 * baseStats.speed * lvl / 100) + 5)
  }, [baseStats, currentLevel, setValue])

  async function fetchBaseStats(pokemonId: number) {
    const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${pokemonId}`)
    if (!res.ok) return
    const data = await res.json()
    const stats: Record<string, number> = {}
    for (const s of data.stats as { base_stat: number; stat: { name: string } }[]) {
      const key = s.stat.name.replace('special-attack', 'sp_attack').replace('special-defense', 'sp_defense')
      stats[key] = s.base_stat
    }
    setBaseStats(stats)
  }

  async function lookupPokemon() {
    const id = Number(speciesId)
    if (!id || id < 1 || id > 1025) return
    setLookupError(null)
    setLooking(true)
    setVarieties([])
    setSelectedVariety(0)
    try {
      const res = await fetch(`https://pokeapi.co/api/v2/pokemon-species/${id}`)
      if (!res.ok) {
        setLookupError(`No se encontró ningún Pokémon con el número #${id}.`)
        setValue('species_name', '')
        setConfirmedId(null)
        return
      }
      const data = await res.json()
      const esName = data.names.find((n: { language: { name: string }; name: string }) => n.language.name === 'es')
      if (esName) setValue('species_name', esName.name)

      const baseRegion = GENERATION_REGION[data.generation?.name] ?? 'Original'
      const vars: { label: string; pokemonId: number; formName: string }[] = data.varieties.map(
        (v: { is_default: boolean; pokemon: { name: string; url: string } }) => {
          const suffix = v.pokemon.name.replace(`${data.name}-`, '')
          const label = v.is_default ? baseRegion : (VARIANT_LABEL[suffix] ?? suffix)
          return { label, pokemonId: idFromUrl(v.pokemon.url), formName: v.is_default ? '' : suffix }
        }
      )
      setVarieties(vars)
      setConfirmedId(vars[0].pokemonId)
      setValue('form_name', vars[0].formName || undefined)
      await fetchBaseStats(vars[0].pokemonId)
    } catch {
      setLookupError('Error al conectar con la API. Verificá tu conexión.')
    } finally {
      setLooking(false)
    }
  }

  async function onSubmit(data: FormData) {
    await addMutation.mutateAsync({
      species_id: data.species_id,
      species_name: data.species_name,
      nickname: data.nickname || undefined,
      level: data.level,
      nature_name: data.nature_name || undefined,
      gender: data.gender || undefined,
      is_shiny: data.is_shiny,
      origin: data.origin,
      game: data.game || undefined,
      form_name: data.form_name || undefined,
      hp: data.hp,
      attack: data.attack,
      defense: data.defense,
      speed: data.speed,
      sp_attack: data.sp_attack,
      sp_defense: data.sp_defense,
    })
    if (data.game) localStorage.setItem('lastGame', data.game)
    navigate('/')
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white transition-colors text-lg">←</button>
        <h1 className="text-xl font-bold text-white">Agregar Pokémon</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        {/* Identity */}
        <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Especie</h2>
          <div className="grid grid-cols-2 gap-3">
            <Field label="# Pokédex" error={errors.species_id?.message}>
              <div className="flex gap-2">
                <input
                  type="number"
                  {...register('species_id')}
                  className={input}
                  placeholder="001"
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), lookupPokemon())}
                />
                <button
                  type="button"
                  onClick={lookupPokemon}
                  disabled={looking}
                  className="shrink-0 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:text-blue-400 text-white rounded-xl px-3 text-sm font-semibold transition-colors"
                >
                  {looking ? '...' : '→'}
                </button>
              </div>
            </Field>
            <Field label="Nombre" error={errors.species_name?.message}>
              <div className="relative">
                {confirmedId && (
                  <img
                    src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${isShiny ? 'shiny/' : ''}${confirmedId}.png`}
                    alt=""
                    key={`${confirmedId}-${isShiny}`}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 object-contain pixelated cursor-zoom-in hover:scale-[3] hover:-translate-y-10 hover:-translate-x-4 transition-transform duration-150 z-10"
                  />
                )}
                <input {...register('species_name')} className={input + ' pr-10 cursor-default'} placeholder="" readOnly />
              </div>
            </Field>
          </div>
          <button
            type="button"
            onClick={() => setValue('is_shiny', !isShiny)}
            className={`w-full py-2.5 rounded-xl text-sm font-medium border transition-colors flex items-center justify-center gap-2 ${
              isShiny
                ? 'bg-yellow-400/10 border-yellow-400/40 text-yellow-300'
                : 'bg-gray-800 border-gray-700 text-gray-500 hover:text-gray-300 hover:border-gray-600'
            }`}
          >
            ✨ {isShiny ? 'Sí, es shiny' : 'No es shiny'}
          </button>
          {lookupError && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-xl">
              {lookupError}
            </div>
          )}
          {varieties.length > 1 && (
            <Field label="Región / Forma">
              <div className="flex border border-gray-700 rounded-xl overflow-hidden">
                {varieties.map((v, i) => (
                  <button
                    key={v.formName}
                    type="button"
                    onClick={() => {
                      setSelectedVariety(i)
                      setConfirmedId(v.pokemonId)
                      setValue('form_name', v.formName || undefined)
                      fetchBaseStats(v.pokemonId)
                    }}
                    className={`flex-1 py-2.5 text-xs font-medium transition-colors ${i > 0 ? 'border-l border-gray-700' : ''} ${
                      selectedVariety === i
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  >
                    {v.label}
                  </button>
                ))}
              </div>
            </Field>
          )}
          <Field label="Apodo (opcional)">
            <input {...register('nickname')} className={input} placeholder="—" />
          </Field>
        </section>

        {/* Attributes */}
        <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Atributos</h2>
          <Field label="Nivel" error={errors.level?.message}>
            <input type="number" {...register('level')} className={input} placeholder="50" />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Naturaleza">
              <div className="relative">
                <input
                  value={natureSearch}
                  onChange={(e) => { setNatureSearch(e.target.value); setNatureOpen(true) }}
                  onFocus={() => setNatureOpen(true)}
                  placeholder="Buscar..."
                  className={input}
                />
                {natureOpen && natureSearch && (
                  <div className="absolute z-10 top-full mt-1 left-0 right-0 bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl max-h-48 overflow-y-auto">
                    {NATURES.filter((n) =>
                      normalize(n.es).includes(normalize(natureSearch))
                    ).map((n) => (
                      <button
                        key={n.en}
                        type="button"
                        onMouseDown={(e) => e.preventDefault()}
                        onClick={() => {
                          setValue('nature_name', n.en)
                          setNatureSearch(n.es)
                          setNatureOpen(false)
                        }}
                        className="w-full text-left px-4 py-2.5 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                      >
                        {n.es}
                      </button>
                    ))}
                    {NATURES.filter((n) => normalize(n.es).includes(normalize(natureSearch))).length === 0 && (
                      <p className="px-4 py-2.5 text-sm text-gray-600">Sin resultados</p>
                    )}
                  </div>
                )}
              </div>
            </Field>
            <Field label="Género">
              <div className="flex border border-gray-700 rounded-xl overflow-hidden">
                {([
                  { value: '', icon: <span className="text-sm font-bold">?</span>, active: 'bg-gray-700 text-gray-300' },
                  { value: 'M', icon: <Mars className="w-4 h-4" />, active: 'bg-blue-600 text-white' },
                  { value: 'F', icon: <Venus className="w-4 h-4" />, active: 'bg-pink-600 text-white' },
                  { value: 'N', icon: <Minus className="w-4 h-4" />, active: 'bg-gray-700 text-gray-300' },
                ] as const).map((o, i) => (
                  <button
                    key={o.value}
                    type="button"
                    title={o.value === '' ? 'Desconocido' : o.value === 'M' ? 'Macho' : o.value === 'F' ? 'Hembra' : 'Sin género'}
                    onClick={() => setValue('gender', o.value)}
                    className={`flex-1 py-2.5 flex items-center justify-center transition-colors ${i > 0 ? 'border-l border-gray-700' : ''} ${
                      gender === o.value ? o.active : 'bg-gray-800 text-gray-600 hover:text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {o.icon}
                  </button>
                ))}
              </div>
            </Field>
          </div>
          <Field label="Origen">
            <ButtonGroup
              options={[
                { value: 'unknown', label: 'Desconocido' },
                { value: 'captured', label: 'Capturado' },
                { value: 'traded', label: 'Intercambiado' },
                { value: 'transferred', label: 'Transferido' },
              ]}
              value={origin}
              onChange={(v) => setValue('origin', v)}
            />
          </Field>
          <Field label="Juego">
            <select {...register('game')} className={input}>
              <option value="">Desconocido</option>
              {Array.from(new Set(GAMES.map((g) => g.gen))).map((gen) => (
                <optgroup key={gen} label={gen}>
                  {GAMES.filter((g) => g.gen === gen).map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </Field>
        </section>

        {/* Stats */}
        <section className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Stats (opcional)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {([ ['hp','PS'], ['attack','Ataque'], ['defense','Defensa'],
                ['sp_attack','At. Esp.'], ['sp_defense','Def. Esp.'], ['speed','Velocidad'] ] as const).map(([k, label]) => (
              <Field key={k} label={label}>
                <input type="number" {...register(k)} className={input} placeholder="—" />
              </Field>
            ))}
          </div>
        </section>

        <button
          type="submit"
          disabled={addMutation.isPending}
          className="w-full bg-yellow-400 hover:bg-yellow-300 disabled:bg-yellow-900 disabled:text-yellow-600 text-gray-900 font-bold py-3.5 rounded-xl text-sm transition-colors"
        >
          {addMutation.isPending ? 'Guardando...' : 'Agregar Pokémon'}
        </button>
      </form>
    </div>
  )
}
