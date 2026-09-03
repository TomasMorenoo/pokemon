// Generates minimal PNG icons for PWA (Pokéball design)
import { createWriteStream } from 'fs'
import { deflateSync } from 'zlib'

function writePNG(filename, size) {
  // Build raw RGBA pixel data
  const pixels = new Uint8Array(size * size * 4)
  const cx = size / 2, cy = size / 2, r = size / 2

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = x - cx, dy = y - cy
      const dist = Math.sqrt(dx * dx + dy * dy)
      const idx = (y * size + x) * 4

      if (dist > r) {
        // transparent outside circle
        pixels[idx] = 0; pixels[idx+1] = 0; pixels[idx+2] = 0; pixels[idx+3] = 0
        continue
      }

      const borderW = size * 0.05
      const lineH = size * 0.04
      const innerR = size * 0.18
      const innerBorder = size * 0.04

      // Outline ring
      if (dist > r - borderW) {
        pixels[idx] = 17; pixels[idx+1] = 24; pixels[idx+2] = 39; pixels[idx+3] = 255
      }
      // Center dividing line
      else if (Math.abs(dy) < lineH) {
        pixels[idx] = 17; pixels[idx+1] = 24; pixels[idx+2] = 39; pixels[idx+3] = 255
      }
      // Inner circle border
      else if (dist < innerR + innerBorder && dist > innerR - innerBorder) {
        pixels[idx] = 17; pixels[idx+1] = 24; pixels[idx+2] = 39; pixels[idx+3] = 255
      }
      // Inner circle fill
      else if (dist < innerR - innerBorder) {
        pixels[idx] = 255; pixels[idx+1] = 255; pixels[idx+2] = 255; pixels[idx+3] = 255
      }
      // Top half — red
      else if (dy < 0) {
        pixels[idx] = 239; pixels[idx+1] = 68; pixels[idx+2] = 68; pixels[idx+3] = 255
      }
      // Bottom half — white
      else {
        pixels[idx] = 255; pixels[idx+1] = 255; pixels[idx+2] = 255; pixels[idx+3] = 255
      }
    }
  }

  // Build PNG raw scanlines (filter byte 0 before each row)
  const scanlines = new Uint8Array(size * (1 + size * 4))
  for (let y = 0; y < size; y++) {
    scanlines[y * (1 + size * 4)] = 0 // filter none
    scanlines.set(pixels.subarray(y * size * 4, (y + 1) * size * 4), y * (1 + size * 4) + 1)
  }

  const compressed = deflateSync(scanlines)

  function chunk(type, data) {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length)
    const typeB = Buffer.from(type)
    const crcBuf = Buffer.concat([typeB, data])
    let crc = 0xFFFFFFFF
    for (const b of crcBuf) {
      crc ^= b
      for (let i = 0; i < 8; i++) crc = (crc >>> 1) ^ (crc & 1 ? 0xEDB88320 : 0)
    }
    crc ^= 0xFFFFFFFF
    const crcOut = Buffer.alloc(4); crcOut.writeUInt32BE(crc >>> 0)
    return Buffer.concat([len, typeB, data, crcOut])
  }

  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])

  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(size, 0)
  ihdr.writeUInt32BE(size, 4)
  ihdr[8] = 8   // bit depth
  ihdr[9] = 6   // RGBA
  ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0

  const png = Buffer.concat([
    sig,
    chunk('IHDR', ihdr),
    chunk('IDAT', compressed),
    chunk('IEND', Buffer.alloc(0)),
  ])

  const ws = createWriteStream(filename)
  ws.write(png)
  ws.end()
  console.log(`Written ${filename} (${size}x${size})`)
}

writePNG('public/pwa-192x192.png', 192)
writePNG('public/pwa-512x512.png', 512)
writePNG('public/apple-touch-icon.png', 180)
