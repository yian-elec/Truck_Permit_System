import { Stepper, type StepperStep } from '@/shared/ui'

export const APPLICATION_FLOW_STEPS: StepperStep[] = [
  { id: 'create', label: '建立案件' },
  { id: 'fill', label: '填寫資料' },
  { id: 'preview', label: '預覽確認' },
  { id: 'done', label: '送件完成' },
]

type Phase = 'new' | 'edit' | 'preview' | 'complete'

const phaseIndex: Record<Phase, number> = {
  new: 0,
  edit: 1,
  preview: 2,
  complete: 3,
}

export function ApplicationFlowStepper({ phase }: { phase: Phase }) {
  return <Stepper steps={APPLICATION_FLOW_STEPS} currentIndex={phaseIndex[phase]} />
}
