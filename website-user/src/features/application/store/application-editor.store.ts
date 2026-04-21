import { create } from 'zustand'

type EditorUiState = {
  dirty: boolean
  expandedSection: string | null
  setDirty: (v: boolean) => void
  setExpandedSection: (id: string | null) => void
}

export const useApplicationEditorStore = create<EditorUiState>((set) => ({
  dirty: false,
  expandedSection: null,
  setDirty: (dirty) => set({ dirty }),
  setExpandedSection: (expandedSection) => set({ expandedSection }),
}))
