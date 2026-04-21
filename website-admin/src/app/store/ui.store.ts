import { create } from 'zustand'

type UiState = {
  globalLoading: boolean
  setGlobalLoading: (value: boolean) => void
  sidebarOpen: boolean
  setSidebarOpen: (value: boolean) => void
  routePanelExpanded: boolean
  setRoutePanelExpanded: (value: boolean) => void
  routeCandidateTab: string | null
  setRouteCandidateTab: (value: string | null) => void
}

export const useUiStore = create<UiState>((set) => ({
  globalLoading: false,
  setGlobalLoading: (value) => set({ globalLoading: value }),
  sidebarOpen: true,
  setSidebarOpen: (value) => set({ sidebarOpen: value }),
  routePanelExpanded: true,
  setRoutePanelExpanded: (value) => set({ routePanelExpanded: value }),
  routeCandidateTab: null,
  setRouteCandidateTab: (value) => set({ routeCandidateTab: value }),
}))
