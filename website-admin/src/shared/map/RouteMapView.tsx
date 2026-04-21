import { useEffect } from 'react'
import { MapContainer, Polyline, TileLayer, useMap } from 'react-leaflet'

import 'leaflet/dist/leaflet.css'

function FitBounds({ positions }: { positions: [number, number][] }) {
  const map = useMap()
  useEffect(() => {
    if (positions.length === 0) return
    map.fitBounds(positions, { padding: [24, 24], maxZoom: 14 })
  }, [map, positions])
  return null
}

type Props = {
  lines: [number, number][][]
  className?: string
}

/** 以 WGS84 座標繪製簡易地圖；若無座標則顯示台灣概覽。 */
export function RouteMapView({ lines, className }: Props) {
  const flat: [number, number][] = lines.flat()
  const defaultCenter: [number, number] = [23.7, 121.0]
  const center = flat.length > 0 ? flat[Math.floor(flat.length / 2)]! : defaultCenter

  return (
    <MapContainer
      center={center}
      zoom={flat.length > 0 ? 12 : 8}
      className={className ?? 'h-72 w-full rounded-md border border-border'}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {lines.map((pos, i) => (
        <Polyline key={i} positions={pos} pathOptions={{ color: '#2563eb', weight: 4 }} />
      ))}
      {flat.length > 0 ? <FitBounds positions={flat} /> : null}
    </MapContainer>
  )
}
