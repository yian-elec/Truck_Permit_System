export type LatLng = {
  lat: number
  lng: number
}

export type MapAdapterProps = {
  center: LatLng
  zoom?: number
  height?: string
  path?: LatLng[]
  className?: string
}
