import { create } from 'zustand'

type RouteUiState = {
  mapExpanded: boolean
  setMapExpanded: (v: boolean) => void
}

export const useRouteUiStore = create<RouteUiState>((set) => ({
  mapExpanded: true,
  setMapExpanded: (mapExpanded) => set({ mapExpanded }),
}))
