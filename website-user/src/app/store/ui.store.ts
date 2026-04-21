import { create } from 'zustand'

type UiState = {
  globalLoading: boolean
  setGlobalLoading: (value: boolean) => void
}

export const useUiStore = create<UiState>((set) => ({
  globalLoading: false,
  setGlobalLoading: (value) => set({ globalLoading: value }),
}))
