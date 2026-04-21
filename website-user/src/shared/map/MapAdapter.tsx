import { GoogleMapAdapter } from './GoogleMapAdapter'
import type { MapAdapterProps } from './types'

/** Map abstraction — swap `GoogleMapAdapter` implementation without touching features. */
export function MapAdapter(props: MapAdapterProps) {
  return <GoogleMapAdapter {...props} />
}
