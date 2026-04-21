import { storageKeys } from '@/shared/constants/storage-keys'
import { storage } from '@/shared/lib/storage'

export function getAccessToken(): string | null {
  return storage.get(storageKeys.accessToken)
}

export function setAccessToken(token: string): void {
  storage.set(storageKeys.accessToken, token)
}

export function clearAccessToken(): void {
  storage.remove(storageKeys.accessToken)
}
