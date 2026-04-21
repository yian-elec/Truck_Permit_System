import { APIProvider, Map, Polyline } from '@vis.gl/react-google-maps'

import { appConfig } from '@/shared/config/app-config'
import { cn } from '@/shared/lib/cn'

import type { MapAdapterProps } from './types'

export function GoogleMapAdapter({
  center,
  zoom = 12,
  height = '320px',
  path = [],
  className,
}: MapAdapterProps) {
  const apiKey = appConfig.googleMapsApiKey
  if (!apiKey) {
    return (
      <div
        className={cn(
          'flex items-center justify-center rounded-md border border-dashed border-border bg-muted/40 text-sm text-muted-foreground',
          className,
        )}
        style={{ height }}
      >
        Set VITE_GOOGLE_MAPS_API_KEY to show the map.
      </div>
    )
  }

  return (
    <div className={cn('overflow-hidden rounded-md border border-border', className)} style={{ height }}>
      <APIProvider apiKey={apiKey}>
        <Map
          defaultCenter={center}
          defaultZoom={zoom}
          gestureHandling="greedy"
          disableDefaultUI={false}
          style={{ width: '100%', height: '100%' }}
        >
          {path.length > 1 ? (
            <Polyline path={path} strokeColor="#2563eb" strokeOpacity={1} strokeWeight={4} />
          ) : null}
        </Map>
      </APIProvider>
    </div>
  )
}
